#include "vector_engine.h"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <queue>

// ============================================================================
// SIMD ACCELERATION (NEON)
// ============================================================================
#if defined(__ARM_NEON) || defined(__ARM_NEON__)
#include <arm_neon.h>
#define SIMD_IMPL "NEON"
float dot_product_simd(const float *a, const float *b, int size) {
  float32x4_t sum_vec = vdupq_n_f32(0.0f);
  int i = 0;
  for (; i + 4 <= size; i += 4) {
    float32x4_t va = vld1q_f32(a + i);
    float32x4_t vb = vld1q_f32(b + i);
    sum_vec = vfmaq_f32(sum_vec, va, vb);
  }
  float result = vaddvq_f32(sum_vec);
  for (; i < size; ++i)
    result += a[i] * b[i];
  return result;
}
#else
#define SIMD_IMPL "SCALAR"
float dot_product_simd(const float *a, const float *b, int size) {
  float sum = 0.0f;
  for (int i = 0; i < size; ++i)
    sum += a[i] * b[i];
  return sum;
}
#endif

// ============================================================================
// CORE HNSW IMPLEMENTATION
// ============================================================================

thread_local VectorEngine::ThreadCtx VectorEngine::ctx;

struct VisitedList {
  std::vector<unsigned int> list;
  unsigned int cur_version;
  VisitedList(size_t size) : list(size, 0), cur_version(1) {}
  bool isVisited(int id) {
    return id < (int)list.size() && list[id] == cur_version;
  }
  void visit(int id) {
    if (id < (int)list.size())
      list[id] = cur_version;
  }
};

VectorEngine::VectorEngine(int M, int efC, int efS)
    : M_(M), efConstruction_(efC), efSearch_default_(efS), entry_point_id_(-1),
      stop_worker_(false) {
  store_.reserve(1000000);
  id_map_.reserve(1000000);
  nodes_.reserve(1000000);
  worker_thread_ = std::thread([this] { backgroundWorkerLoop(); });
}

VectorEngine::~VectorEngine() {
  {
    std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
    stop_worker_ = true;
  }
  worker_cv_.notify_all();
  if (worker_thread_.joinable())
    worker_thread_.join();
  for (auto node : nodes_)
    delete node;
}

void VectorEngine::clear() {
  std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
  active_buffer_.clear();
  store_.clear();
  id_map_.clear();
  for (auto n : nodes_)
    delete n;
  nodes_.clear();
  deleted_nodes_.clear();
  entry_point_id_ = -1;
}

float VectorEngine::getDistance(const float *v1, const float *v2) {
  // Revert to standard HNSW distance for stability: 1.0 - similarity
  return 1.0f - dot_product_simd(v1, v2, (int)store_[0].size());
}

float VectorEngine::getDistance(int id1, int id2) {
  return getDistance(store_[id1].data(), store_[id2].data());
}

int VectorEngine::getRandomLayer() {
  std::uniform_real_distribution<float> dist(0.0, 1.0);
  float mult = -1.0f / log(1.0f / (float)M_);
  int layer = (int)(-log(dist(ctx.rng)) * mult);
  return std::min(layer, MAX_LAYERS - 1);
}

int VectorEngine::searchLayerGreedy(const float *query_vec, int entry_id,
                                    int layer) {
  int curr_id = entry_id;
  float curr_dist = getDistance(query_vec, store_[curr_id].data());
  bool changed = true;
  while (changed) {
    changed = false;
    HNSWNode *node = nodes_[curr_id];
    for (int neighbor_id : node->neighbors[layer]) {
      float d = getDistance(query_vec, store_[neighbor_id].data());
      if (d < curr_dist) {
        curr_dist = d;
        curr_id = neighbor_id;
        changed = true;
      }
    }
  }
  return curr_id;
}

void VectorEngine::searchLayerBeam(
    const float *query_vec, int entry_id, int ef, int layer,
    std::priority_queue<std::pair<float, int>> &top_candidates) {
  size_t n_size;
  {
    std::shared_lock<std::shared_timed_mutex> lock(engine_mutex_);
    n_size = nodes_.size();
  }
  VisitedList vl(n_size + 1000);

  // candidates: Min-heap to explore closest first
  std::priority_queue<std::pair<float, int>, std::vector<std::pair<float, int>>,
                      std::greater<>>
      candidates;

  float d = getDistance(query_vec, store_[entry_id].data());
  candidates.push({d, entry_id});
  top_candidates.push({d, entry_id});
  vl.visit(entry_id);

  while (!candidates.empty()) {
    auto [c_dist, c_id] = candidates.top();
    candidates.pop();

    // top_candidates is a Max-heap. top() is the furthest result.
    // If current candidate is further than the worst in our top list, skip.
    if (c_dist > top_candidates.top().first &&
        top_candidates.size() >= (size_t)ef)
      break;

    HNSWNode *node = nodes_[c_id];
    for (int neighbor_id : node->neighbors[layer]) {
      if (!vl.isVisited(neighbor_id)) {
        vl.visit(neighbor_id);
        float n_dist = getDistance(query_vec, store_[neighbor_id].data());

        if (top_candidates.size() < (size_t)ef ||
            n_dist < top_candidates.top().first) {
          candidates.push({n_dist, neighbor_id});
          top_candidates.push({n_dist, neighbor_id});
          if (top_candidates.size() > (size_t)ef)
            top_candidates.pop();
        }
      }
    }
  }
}

void VectorEngine::selectNeighborsHeuristic(
    int node_idx, std::priority_queue<std::pair<float, int>> &candidates, int M,
    int layer) {
  std::vector<std::pair<float, int>> sorted;
  // candidates is a Max-heap of {dist, id}. We want closest first.
  while (!candidates.empty()) {
    sorted.push_back(candidates.top());
    candidates.pop();
  }
  std::sort(sorted.begin(), sorted.end()); // closest (smallest dist) first

  std::vector<int> selected;
  for (auto &p : sorted) {
    int cand = p.second;
    bool too_close = false;
    for (int s : selected) {
      // With dist = 1.0 - dot, 0.01 means extremely similar
      if (getDistance(cand, s) < 0.01f) {
        too_close = true;
        break;
      }
    }
    if (!too_close) {
      selected.push_back(cand);
    }
    if ((int)selected.size() >= M)
      break;
  }

  for (auto s : selected) {
    candidates.push({0.0f, s});
  }
}

void VectorEngine::insertHNSW(int node_idx) {
  int curr_entry_id = -1;
  int max_l = -1;
  const float *query_vec = store_[node_idx].data();

  {
    std::shared_lock<std::shared_timed_mutex> lock(engine_mutex_);
    if (entry_point_id_ != -1) {
      curr_entry_id = entry_point_id_;
      max_l = nodes_[entry_point_id_]->max_layer;
    }
  }

  int target_layer = getRandomLayer();
  nodes_[node_idx]->max_layer = target_layer;

  if (curr_entry_id == -1) {
    std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
    if (entry_point_id_ == -1) {
      entry_point_id_ = node_idx;
      return;
    }
    curr_entry_id = entry_point_id_;
    max_l = nodes_[entry_point_id_]->max_layer;
  }

  for (int l = max_l; l > target_layer; --l) {
    std::shared_lock<std::shared_timed_mutex> lock(engine_mutex_);
    curr_entry_id = searchLayerGreedy(query_vec, curr_entry_id, l);
  }

  for (int l = std::min(target_layer, max_l); l >= 0; --l) {
    std::priority_queue<std::pair<float, int>> results; // Max-heap
    searchLayerBeam(query_vec, curr_entry_id, efConstruction_, l, results);

    std::priority_queue<std::pair<float, int>> candidates; // Max-heap
    while (!results.empty()) {
      candidates.push(results.top());
      results.pop();
    }

    int layer_M = (l == 0) ? M_ * 2 : M_;
    selectNeighborsHeuristic(node_idx, candidates, layer_M, l);

    std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
    while (!candidates.empty()) {
      int neighbor_id = candidates.top().second;
      candidates.pop();
      nodes_[node_idx]->neighbors[l].push_back(neighbor_id);
      nodes_[neighbor_id]->neighbors[l].push_back(node_idx);

      if (nodes_[neighbor_id]->neighbors[l].size() > (size_t)layer_M) {
        std::priority_queue<std::pair<float, int>> n_candidates;
        for (int nid : nodes_[neighbor_id]->neighbors[l]) {
          n_candidates.push({getDistance(neighbor_id, nid), nid});
        }
        selectNeighborsHeuristic(neighbor_id, n_candidates, layer_M, l);
        nodes_[neighbor_id]->neighbors[l].clear();
        while (!n_candidates.empty()) {
          nodes_[neighbor_id]->neighbors[l].push_back(
              n_candidates.top().second);
          n_candidates.pop();
        }
      }
    }
    if (!nodes_[node_idx]->neighbors[l].empty()) {
      curr_entry_id = nodes_[node_idx]->neighbors[l][0];
    }
  }

  std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
  if (target_layer > nodes_[entry_point_id_]->max_layer) {
    entry_point_id_ = node_idx;
  }
}

std::vector<std::pair<std::string, float>>
VectorEngine::search(const std::vector<float> &query_vec, int k,
                     int ef_search) {
  std::shared_lock<std::shared_timed_mutex> lock(engine_mutex_);
  if (entry_point_id_ == -1)
    return {};

  int ef = (ef_search > 0) ? ef_search : efSearch_default_;
  int curr_id = entry_point_id_;
  const float *q = query_vec.data();

  for (int l = nodes_[curr_id]->max_layer; l > 0; --l) {
    curr_id = searchLayerGreedy(q, curr_id, l);
  }

  std::priority_queue<std::pair<float, int>> results; // Max-heap
  searchLayerBeam(q, curr_id, ef, 0, results);

  std::vector<std::pair<float, int>> sorted_results;
  while (!results.empty()) {
    if (deleted_nodes_.find(results.top().second) == deleted_nodes_.end()) {
      sorted_results.push_back(results.top());
    }
    results.pop();
  }
  std::sort(sorted_results.begin(), sorted_results.end());

  std::vector<std::pair<std::string, float>> final_results;
  for (size_t i = 0; i < (size_t)k && i < sorted_results.size(); ++i) {
    // Distance is 1.0 - Similarity, so Similarity is 1.0 - Distance
    final_results.push_back(
        {id_map_[sorted_results[i].second], 1.0f - sorted_results[i].first});
  }
  return final_results;
}

void VectorEngine::addVectors(const std::vector<std::vector<float>> &vecs,
                              const std::vector<std::string> &ids) {
  std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
  for (size_t i = 0; i < vecs.size(); ++i) {
    int idx = (int)store_.size();
    std::vector<float> norm_vec = vecs[i];
    float norm = sqrt(dot_product_simd(norm_vec.data(), norm_vec.data(),
                                       (int)norm_vec.size()));
    if (norm > 1e-10)
      for (float &x : norm_vec)
        x /= norm;
    store_.push_back(norm_vec);
    id_map_.push_back(ids[i]);
    nodes_.push_back(new HNSWNode(idx, 0));
    active_buffer_.push_back(idx);
  }
  worker_cv_.notify_one();
}

void VectorEngine::addVector(const std::vector<float> &vec,
                             const std::string &id) {
  addVectors({vec}, {id});
}

void VectorEngine::backgroundWorkerLoop() {
  while (true) {
    int node_idx = -1;
    {
      std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
      worker_cv_.wait(
          lock, [this] { return stop_worker_ || !active_buffer_.empty(); });
      if (stop_worker_ && active_buffer_.empty())
        break;
      node_idx = active_buffer_.front();
      active_buffer_.pop_front();
    }
    if (node_idx != -1)
      insertHNSW(node_idx);
  }
}

int VectorEngine::getPendingCount() const {
  std::shared_lock<std::shared_timed_mutex> lock(engine_mutex_);
  return (int)active_buffer_.size();
}

EngineStats VectorEngine::getStats() const {
  std::shared_lock<std::shared_timed_mutex> lock(engine_mutex_);
  return {store_.size(),
          active_buffer_.size(),
          entry_point_id_,
          (entry_point_id_ != -1 ? nodes_[entry_point_id_]->max_layer : -1),
          M_,
          efConstruction_,
          efSearch_default_};
}

void VectorEngine::removeVector(const std::string &id) {
  std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
  for (size_t i = 0; i < id_map_.size(); ++i) {
    if (id_map_[i] == id) {
      deleted_nodes_.insert((int)i);
      break;
    }
  }
}

void VectorEngine::reconfigure(int M, int efC, int efS) {
  std::unique_lock<std::shared_timed_mutex> lock(engine_mutex_);
  M_ = M;
  efConstruction_ = efC;
  efSearch_default_ = efS;
}

bool VectorEngine::saveSnapshot(const std::string &path) { return false; }
bool VectorEngine::loadSnapshot(const std::string &path) { return false; }
const char *getSIMDBackend() { return SIMD_IMPL; }
