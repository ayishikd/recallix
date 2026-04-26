#include "vector_engine.h"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <queue>
#include <numeric>
#include <arm_neon.h>

thread_local VectorEngine::ThreadCtx VectorEngine::ctx;

VectorEngine::VectorEngine() {
    nodes_.reserve(1100000);
}

// Hyper-optimized NEON dot product
float VectorEngine::dotProduct(const std::vector<float> &v1,
                               const std::vector<float> &v2) {
    const float* a = v1.data();
    const float* b = v2.data();
    size_t size = v1.size();
    float32x4_t sum_vec = vdupq_n_f32(0.0f);
    size_t i = 0;
    for (; i + 3 < size; i += 4) {
        float32x4_t va = vld1q_f32(a + i);
        float32x4_t vb = vld1q_f32(b + i);
        sum_vec = vmlaq_f32(sum_vec, va, vb);
    }
    float dot = vaddvq_f32(sum_vec);
    for (; i < size; ++i) dot += a[i] * b[i];
    return dot;
}

int VectorEngine::getRandomLayer() {
    std::uniform_real_distribution<float> dist(0, 1);
    float r = dist(ctx.rng);
    int layer = 0;
    while (r < 0.5 && layer < 4) { // Only 4 layers for ultra-fast build
        layer++;
        r = dist(ctx.rng);
    }
    return layer;
}

void VectorEngine::addVector(const std::string &id, const std::vector<float> &data) {
    int idx = store_.size();
    store_.push_back({data, id});
    insertHNSW(idx);
}

void VectorEngine::bulkAdd(const std::vector<std::pair<std::string, std::vector<float>>> &vectors) {
    for (const auto& v : vectors) {
        int idx = store_.size();
        store_.push_back({v.second, v.first});
        insertHNSW(idx);
    }
}

void VectorEngine::insertHNSW(int node_idx) {
    int layer = getRandomLayer();
    HNSWNode* new_node = new HNSWNode(node_idx);
    new_node->neighbors.resize(layer + 1);
    
    if (nodes_.size() <= (size_t)node_idx) nodes_.resize(node_idx + 200000, nullptr);
    nodes_[node_idx] = new_node;

    if (entry_node_ == -1) {
        entry_node_ = node_idx;
        max_layer_ = layer;
        return;
    }

    const auto& query = store_[node_idx].data;
    int curr_node = entry_node_;
    
    // Fast greedy search to find entry point
    for (int l = max_layer_; l > layer; --l) {
        float curr_dist = dotProduct(query, store_[curr_node].data);
        bool changed = true;
        while (changed) {
            changed = false;
            for (int neighbor : nodes_[curr_node]->neighbors[l]) {
                float d = dotProduct(query, store_[neighbor].data);
                if (d > curr_dist) {
                    curr_dist = d;
                    curr_node = neighbor;
                    changed = true;
                }
            }
        }
    }

    // Connect to neighbors with minimal search (ef=4)
    for (int l = std::min(layer, max_layer_); l >= 0; --l) {
        auto candidates = searchLayer(query, curr_node, 4, l); // ef=4 is the magic number for build speed
        for (auto& cand : candidates) {
            int cand_idx = cand.second;
            if (cand_idx == node_idx) continue;
            
            new_node->neighbors[l].push_back(cand_idx);
            auto& n_list = nodes_[cand_idx]->neighbors[l];
            n_list.push_back(node_idx);
            
            // Fast trim: only sort if it exceeds 2*M to reduce frequency of expensive ops
            if (n_list.size() > (size_t)(M * 2)) {
                std::sort(n_list.begin(), n_list.end(), [&](int a, int b) {
                    return dotProduct(store_[cand_idx].data, store_[a].data) > dotProduct(store_[cand_idx].data, store_[b].data);
                });
                n_list.resize(M);
            }
        }
        if (!candidates.empty()) curr_node = candidates[0].second;
    }

    if (layer > max_layer_) {
        max_layer_ = layer;
        entry_node_ = node_idx;
    }
}

std::vector<std::pair<float, int>> VectorEngine::searchLayer(const std::vector<float>& query, int entry_node, int ef, int layer) {
    std::priority_queue<std::pair<float, int>, std::vector<std::pair<float, int>>, std::greater<std::pair<float, int>>> top_candidates;
    std::priority_queue<std::pair<float, int>> candidate_queue;
    
    ctx.visited_tag++;
    if (ctx.visited_tag == 0) std::fill(ctx.visited_list.begin(), ctx.visited_list.end(), 0), ctx.visited_tag = 1;

    float dist = dotProduct(query, store_[entry_node].data);
    top_candidates.push({dist, entry_node});
    candidate_queue.push({dist, entry_node});
    ctx.visited_list[entry_node] = ctx.visited_tag;

    float lower_bound = dist;

    while (!candidate_queue.empty()) {
        auto curr = candidate_queue.top();
        candidate_queue.pop();
        if (curr.first < lower_bound && top_candidates.size() >= (size_t)ef) break;

        for (int neighbor : nodes_[curr.second]->neighbors[layer]) {
            if (ctx.visited_list[neighbor] != ctx.visited_tag) {
                ctx.visited_list[neighbor] = ctx.visited_tag;
                float d = dotProduct(query, store_[neighbor].data);
                if (top_candidates.size() < (size_t)ef || d > lower_bound) {
                    candidate_queue.push({d, neighbor});
                    top_candidates.push({d, neighbor});
                    if (top_candidates.size() > (size_t)ef) top_candidates.pop();
                    lower_bound = top_candidates.top().first;
                }
            }
        }
    }

    std::vector<std::pair<float, int>> results;
    while (!top_candidates.empty()) {
        results.push_back(top_candidates.top());
        top_candidates.pop();
    }
    std::reverse(results.begin(), results.end());
    return results;
}

std::vector<std::string> VectorEngine::search(const std::vector<float> &query, int topK) {
    if (entry_node_ == -1) return {};
    int curr_node = entry_node_;
    float curr_dist = dotProduct(query, store_[curr_node].data);
    for (int l = max_layer_; l > 0; --l) {
        bool changed = true;
        while (changed) {
            changed = false;
            for (int neighbor : nodes_[curr_node]->neighbors[l]) {
                float d = dotProduct(query, store_[neighbor].data);
                if (d > curr_dist) {
                    curr_dist = d;
                    curr_node = neighbor;
                    changed = true;
                }
            }
        }
    }
    auto candidates = searchLayer(query, curr_node, std::max(64, topK), 0);
    std::vector<std::string> results;
    for (int i = 0; i < std::min((int)candidates.size(), topK); ++i) results.push_back(store_[candidates[i].second].id);
    return results;
}

void VectorEngine::rebuildIndex() {
    entry_node_ = -1;
    max_layer_ = -1;
    for (auto n : nodes_) if (n) delete n;
    nodes_.clear();
    for (int i = 0; i < (int)store_.size(); ++i) insertHNSW(i);
}

void VectorEngine::removeVector(const std::string &id) {
    store_.erase(std::remove_if(store_.begin(), store_.end(), [&id](const Vector &v) { return v.id == id; }), store_.end());
    rebuildIndex();
}

void VectorEngine::save(const std::string &filename) {
    std::ofstream os(filename, std::ios::binary);
    size_t size = store_.size();
    os.write(reinterpret_cast<const char *>(&size), sizeof(size));
    for (const auto &v : store_) {
        size_t id_len = v.id.size();
        os.write(reinterpret_cast<const char *>(&id_len), sizeof(id_len));
        os.write(v.id.data(), id_len);
        size_t vec_len = v.data.size();
        os.write(reinterpret_cast<const char *>(&vec_len), sizeof(vec_len));
        os.write(reinterpret_cast<const char *>(v.data.data()), vec_len * sizeof(float));
    }
}

void VectorEngine::load(const std::string &filename) {
    std::ifstream is(filename, std::ios::binary);
    if (!is) return;
    size_t size;
    is.read(reinterpret_cast<char *>(&size), sizeof(size));
    store_.clear();
    for (size_t i = 0; i < size; ++i) {
        size_t id_len;
        is.read(reinterpret_cast<char *>(&id_len), sizeof(id_len));
        std::string id(id_len, ' ');
        is.read(&id[0], id_len);
        size_t vec_len;
        is.read(reinterpret_cast<char *>(&vec_len), sizeof(vec_len));
        std::vector<float> data(vec_len);
        is.read(reinterpret_cast<char *>(data.data()), vec_len * sizeof(float));
        store_.push_back({data, id});
    }
    rebuildIndex();
}
