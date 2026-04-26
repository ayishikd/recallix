#ifndef VECTOR_ENGINE_H
#define VECTOR_ENGINE_H

#include <string>
#include <vector>
#include <map>
#include <random>

struct Vector {
  std::vector<float> data;
  std::string id;
};

class VectorEngine {
public:
  VectorEngine();
  void addVector(const std::string &id, const std::vector<float> &data);
  void bulkAdd(const std::vector<std::pair<std::string, std::vector<float>>> &vectors);
  std::vector<std::string> search(const std::vector<float> &query, int topK);
  void removeVector(const std::string &id);
  void save(const std::string &filename);
  void load(const std::string &filename);

  void rebuildIndex();

private:
  std::vector<Vector> store_;
  
  struct HNSWNode {
      int store_idx;
      std::vector<std::vector<int>> neighbors; // neighbors[layer]
      HNSWNode(int idx) : store_idx(idx) {}
  };
  
  std::vector<HNSWNode*> nodes_;

  int entry_node_ = -1;
  int max_layer_ = -1;
  
  struct ThreadCtx {
      std::vector<int> visited_list;
      int visited_tag = 0;
      std::mt19937 rng;
      ThreadCtx() : rng(42) { visited_list.resize(2000000, 0); }
  };
  
  static thread_local ThreadCtx ctx;

  const int M = 16;
  const int efConstruction = 64;
  const int efSearch = 64;
  const float mult_ = 0.5f; 

  float dotProduct(const std::vector<float> &v1, const std::vector<float> &v2);
  int getRandomLayer();
  
  void insertHNSW(int node_idx);
  std::vector<std::pair<float, int>> searchLayer(const std::vector<float>& query, int entry_node, int ef, int layer);
};

#endif
