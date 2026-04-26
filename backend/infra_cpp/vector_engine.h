#ifndef VECTOR_ENGINE_H
#define VECTOR_ENGINE_H

#include <vector>
#include <string>
#include <mutex>
#include <random>
#include <map>

struct HNSWNode {
    int store_idx;
    int max_layer;
    std::vector<int> neighbors[8]; 
    HNSWNode(int idx) : store_idx(idx), max_layer(0) {}
};

class VectorEngine {
public:
    VectorEngine() {
        entry_point_id_ = -1;
    }
    
    void addVector(const std::vector<float>& vec, const std::string& id);
    std::vector<std::pair<std::string, float>> search(const std::vector<float>& query_vec, int k);
    void clear();

private:
    std::vector<std::vector<float>> store_;
    std::vector<std::string> id_map_; // Maps internal index to original string ID
    std::vector<HNSWNode*> nodes_;
    int entry_point_id_;
    std::mutex engine_mutex_;
    
    struct ThreadCtx {
        std::mt19937 rng;
        ThreadCtx() : rng(42) {}
    };
    static thread_local ThreadCtx ctx;

    const int MAX_LAYERS = 8;
    float calculateCosineSimilarity(const std::vector<float>& a, const std::vector<float>& b);
    int getRandomLayer();
    void insertHNSW(int node_idx);
};

#endif
