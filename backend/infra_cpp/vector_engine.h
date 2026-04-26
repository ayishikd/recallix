#ifndef VECTOR_ENGINE_H
#define VECTOR_ENGINE_H

#include <vector>
#include <string>
#include <mutex>
#include <random>
#include <map>
#include <thread>
#include <condition_variable>
#include <atomic>
#include <deque>

struct HNSWNode {
    int store_idx;
    int max_layer;
    int neighbors[8][16]; 
    int neighbor_counts[8];
    HNSWNode(int idx) : store_idx(idx), max_layer(0) {
        for (int i = 0; i < 8; ++i) neighbor_counts[i] = 0;
    }
};

class VectorEngine {
public:
    VectorEngine();
    ~VectorEngine();
    
    void addVector(const std::vector<float>& vec, const std::string& id);
    std::vector<std::pair<std::string, float>> search(const std::vector<float>& query_vec, int k);
    void clear();
    int getPendingCount() const;

private:
    std::vector<std::vector<float>> store_;
    std::vector<std::string> id_map_; // Maps internal index to original string ID
    std::vector<HNSWNode*> nodes_;
    
    // Background Indexing Support
    std::deque<int> active_buffer_;      // Nodes waiting to be indexed
    std::thread worker_thread_;
    std::condition_variable_any worker_cv_;
    std::atomic<bool> stop_worker_{false};
    void backgroundWorkerLoop();

    mutable std::recursive_mutex engine_mutex_;
    int entry_point_id_ = -1;
    int max_id_ = 0;
    
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

// Returns the SIMD backend used at compile time ("NEON", "AVX2", "SSE", or "SCALAR")
const char* getSIMDBackend();

#endif
