#ifndef VECTOR_ENGINE_H
#define VECTOR_ENGINE_H

#include <vector>
#include <string>
#include <mutex>
#include <thread>
#include <condition_variable>
#include <deque>
#include <random>
#include <set>

struct HNSWNode {
    int id;
    int max_layer;
    std::vector<int> neighbors[8];
    int neighbor_counts[8];

    HNSWNode(int _id) : id(_id), max_layer(0) {
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
    void normalizeVector(std::vector<float>& vec);
    void insertHNSW(int node_idx);
    void removeVector(const std::string& id);
    void rebuildIndex();
    bool saveSnapshot(const std::string& path);
    bool loadSnapshot(const std::string& path);

private:
    std::vector<std::vector<float>> store_;
    std::vector<std::string> id_map_;
    std::vector<HNSWNode*> nodes_;
    std::set<int> deleted_nodes_; // Fix #2: Tombstones
    
    // Background Indexing Support
    std::deque<int> active_buffer_;
    std::thread worker_thread_;
    std::condition_variable_any worker_cv_;
    bool stop_worker_;

    mutable std::recursive_mutex engine_mutex_;
    int entry_point_id_;
    int max_id_;

    struct ThreadCtx {
        std::mt19937 rng;
        ThreadCtx() : rng(std::random_device{}()) {}
    };
    static thread_local ThreadCtx ctx;

    float calculateCosineSimilarity(const std::vector<float>& a, const std::vector<float>& b);
    int getRandomLayer();
    void backgroundWorkerLoop();

    const int MAX_LAYERS = 8;
};

const char* getSIMDBackend();

#endif
