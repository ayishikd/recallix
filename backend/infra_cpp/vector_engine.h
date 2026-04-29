#ifndef VECTOR_ENGINE_H
#define VECTOR_ENGINE_H

#include <condition_variable>
#include <deque>
#include <mutex>
#include <random>
#include <set>
#include <shared_mutex>
#include <string>
#include <thread>
#include <vector>

// 🧠 RESEARCH-GRADE HNSW NODE STRUCTURE
struct HNSWNode {
  int id;
  int max_layer;
  // neighbors[layer] is a vector of neighbor IDs
  std::vector<std::vector<int>> neighbors;

  HNSWNode(int _id, int _max_layer) : id(_id), max_layer(_max_layer) {
    neighbors.resize(16); // Pre-allocate for MAX_LAYERS to prevent segfaults
  }
};

struct EngineStats {
  size_t total_nodes;
  size_t pending_nodes;
  int entry_point_id;
  int max_layer;
  int M;
  int efConstruction;
  int efSearch;
};

class VectorEngine {
public:
  VectorEngine(int M = 48, int efConstruction = 200, int efSearch = 100);
  ~VectorEngine();

  // 🧩 API LAYER
  void addVector(const std::vector<float> &vec, const std::string &id);
  void addVectors(const std::vector<std::vector<float>> &vecs,
                  const std::vector<std::string> &ids);
  std::vector<std::pair<std::string, float>>
  search(const std::vector<float> &query_vec, int k, int ef_search = -1);

  void clear();
  EngineStats getStats() const;
  int getPendingCount() const;
  void removeVector(const std::string &id);
  void reconfigure(int M, int efC, int efS);

  // 🛠️ SYSTEM LAYER
  bool saveSnapshot(const std::string &path);
  bool loadSnapshot(const std::string &path);

private:
  // 🏗️ STORAGE
  std::vector<std::vector<float>> store_;
  std::vector<std::string> id_map_;
  std::vector<HNSWNode *> nodes_;
  std::set<int> deleted_nodes_;

  // 🚦 CONCURRENCY & INDEXING
  mutable std::shared_timed_mutex
      engine_mutex_; // shared_timed_mutex for concurrent search (C++14
                     // compatibility)
  std::deque<int> active_buffer_;
  std::thread worker_thread_;
  std::condition_variable_any worker_cv_;
  bool stop_worker_;

  // 📊 HNSW STATE
  int entry_point_id_;
  int M_;
  int efConstruction_;
  int efSearch_default_;
  const int MAX_LAYERS = 16;

  // 🔬 HNSW CORE SUBSYSTEMS
  void insertHNSW(int node_idx);
  int getRandomLayer();
  float getDistance(int id1, int id2);
  float getDistance(const float *vec1, const float *vec2);

  // 🔷 M-DIVERSITY SELECTION (Paper Correct)
  void selectNeighborsHeuristic(
      int node_idx, std::priority_queue<std::pair<float, int>> &candidates,
      int M, int layer);

  // 🔷 SEARCH KERNELS
  int searchLayerGreedy(const float *query_vec, int entry_id, int layer);
  void
  searchLayerBeam(const float *query_vec, int entry_id, int ef, int layer,
                  std::priority_queue<std::pair<float, int>> &top_candidates);

  void backgroundWorkerLoop();

  struct ThreadCtx {
    std::mt19937 rng;
    ThreadCtx() : rng(std::random_device{}()) {}
  };
  static thread_local ThreadCtx ctx;
};

const char *getSIMDBackend();

#endif
