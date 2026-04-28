#include "vector_engine.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <queue>
#include <cmath>
#include <set>

// ============================================================================
// CROSS-PLATFORM SIMD DISPATCHER
// Compile-time detection: AVX2 → SSE → NEON → Scalar
// ============================================================================

#if defined(__AVX2__)
    #include <immintrin.h>
    #define SIMD_IMPL "AVX2"

    float dot_product_simd(const float* a, const float* b, int size) {
        __m256 sum = _mm256_setzero_ps();
        int i = 0;
        for (; i + 8 <= size; i += 8) {
            __m256 va = _mm256_loadu_ps(a + i);
            __m256 vb = _mm256_loadu_ps(b + i);
            sum = _mm256_fmadd_ps(va, vb, sum);
        }
        __m128 vlow = _mm256_castps256_ps128(sum);
        __m128 vhigh = _mm256_extractf128_ps(sum, 1);
        __m128 vsum = _mm_add_ps(vlow, vhigh);
        __m128 shuf = _mm_shuffle_ps(vsum, vsum, _MM_SHUFFLE(2, 3, 0, 1));
        vsum = _mm_add_ps(vsum, shuf);
        shuf = _mm_shuffle_ps(vsum, vsum, _MM_SHUFFLE(1, 0, 3, 2));
        vsum = _mm_add_ps(vsum, shuf);
        float result = _mm_cvtss_f32(vsum);
        for (; i < size; ++i) result += a[i] * b[i];
        return result;
    }

#elif defined(__SSE__)
    #include <xmmintrin.h>
    #define SIMD_IMPL "SSE"

    float dot_product_simd(const float* a, const float* b, int size) {
        __m128 sum = _mm_setzero_ps();
        int i = 0;
        for (; i + 4 <= size; i += 4) {
            __m128 va = _mm_loadu_ps(a + i);
            __m128 vb = _mm_loadu_ps(b + i);
            sum = _mm_add_ps(sum, _mm_mul_ps(va, vb));
        }
        __m128 shuf = _mm_shuffle_ps(sum, sum, _MM_SHUFFLE(2, 3, 0, 1));
        sum = _mm_add_ps(sum, shuf);
        shuf = _mm_shuffle_ps(sum, sum, _MM_SHUFFLE(1, 0, 3, 2));
        sum = _mm_add_ps(sum, shuf);
        float result = _mm_cvtss_f32(sum);
        for (; i < size; ++i) result += a[i] * b[i];
        return result;
    }

#elif defined(__ARM_NEON) || defined(__ARM_NEON__)
    #include <arm_neon.h>
    #define SIMD_IMPL "NEON"

    float dot_product_simd(const float* a, const float* b, int size) {
        float32x4_t sum_vec = vdupq_n_f32(0.0f);
        int i = 0;
        for (; i + 4 <= size; i += 4) {
            float32x4_t va = vld1q_f32(a + i);
            float32x4_t vb = vld1q_f32(b + i);
            sum_vec = vfmaq_f32(sum_vec, va, vb);
        }
        float result = vaddvq_f32(sum_vec);
        for (; i < size; ++i) result += a[i] * b[i];
        return result;
    }

#else
    #define SIMD_IMPL "SCALAR"

    float dot_product_simd(const float* a, const float* b, int size) {
        float sum = 0.0f;
        for (int i = 0; i < size; ++i) {
            sum += a[i] * b[i];
        }
        return sum;
    }
#endif

thread_local VectorEngine::ThreadCtx VectorEngine::ctx;

float VectorEngine::calculateCosineSimilarity(const std::vector<float>& a, const std::vector<float>& b) {
    if (a.size() != b.size()) return 0.0f;
    float dot = dot_product_simd(a.data(), b.data(), a.size());
    float norm_a = std::sqrt(dot_product_simd(a.data(), a.data(), a.size()));
    float norm_b = std::sqrt(dot_product_simd(b.data(), b.data(), b.size()));
    if (norm_a == 0 || norm_b == 0) return 0.0f;
    return dot / (norm_a * norm_b);
}

int VectorEngine::getRandomLayer() {
    std::uniform_real_distribution<float> dist(0, 1);
    float r = dist(ctx.rng);
    int layer = 0;
    while (r < 0.5 && layer < 4) {
        layer++;
        r = dist(ctx.rng);
    }
    return layer;
}

void VectorEngine::normalizeVector(std::vector<float>& vec) {
    float norm_sq = dot_product_simd(vec.data(), vec.data(), vec.size());
    if (norm_sq > 1e-12) {
        float norm = std::sqrt(norm_sq);
        for (float& x : vec) x /= norm;
    }
}

void VectorEngine::clear() {
    {
        std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
        active_buffer_.clear();
    }
    
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    store_.clear();
    id_map_.clear();
    deleted_nodes_.clear(); // Fix #2: Clear tombstones
    for (auto node : nodes_) delete node;
    nodes_.clear();
    entry_point_id_ = -1;
    max_id_ = 0;
    std::cout << "🧹 C++ Vector Engine cleared." << std::endl;
}

int VectorEngine::getPendingCount() const {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    return active_buffer_.size();
}

void VectorEngine::removeVector(const std::string& id) {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    for (size_t i = 0; i < id_map_.size(); ++i) {
        if (id_map_[i] == id) {
            deleted_nodes_.insert((int)i);
            break;
        }
    }
    
    if (!store_.empty() && (float)deleted_nodes_.size() / store_.size() > 0.25f) {
        std::cout << "[VectorEngine] Tombstone threshold reached. Rebuilding HNSW graph..." << std::endl;
        rebuildIndex();
    }
}

void VectorEngine::rebuildIndex() {
    // This assumes engine_mutex_ is already locked by the caller (removeVector)
    std::vector<std::vector<float>> new_store;
    std::vector<std::string> new_id_map;
    
    new_store.reserve(store_.size() - deleted_nodes_.size());
    new_id_map.reserve(id_map_.size() - deleted_nodes_.size());
    
    for (size_t i = 0; i < store_.size(); ++i) {
        if (deleted_nodes_.find(i) == deleted_nodes_.end()) {
            new_store.push_back(store_[i]);
            new_id_map.push_back(id_map_[i]);
        }
    }
    
    // Clear and re-initialize
    store_ = std::move(new_store);
    id_map_ = std::move(new_id_map);
    deleted_nodes_.clear();
    
    for (auto node : nodes_) delete node;
    nodes_.clear();
    entry_point_id_ = -1;
    
    // Re-index all vectors
    for (size_t i = 0; i < store_.size(); ++i) {
        nodes_.push_back(new HNSWNode(i));
        insertHNSW(i);
    }
    std::cout << "[VectorEngine] HNSW graph rebuilt with " << store_.size() << " nodes." << std::endl;
}

bool VectorEngine::saveSnapshot(const std::string& path) {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    std::ofstream out(path, std::ios::binary);
    if (!out) return false;
    
    size_t count = id_map_.size();
    out.write((char*)&count, sizeof(size_t));
    for (size_t i = 0; i < count; ++i) {
        size_t id_len = id_map_[i].size();
        out.write((char*)&id_len, sizeof(size_t));
        out.write(id_map_[i].data(), id_len);
        
        size_t vec_size = store_[i].size();
        out.write((char*)&vec_size, sizeof(size_t));
        out.write((char*)store_[i].data(), vec_size * sizeof(float));
    }
    
    size_t deleted_count = deleted_nodes_.size();
    out.write((char*)&deleted_count, sizeof(size_t));
    for (int idx : deleted_nodes_) {
        out.write((char*)&idx, sizeof(int));
    }
    
    return true;
}

bool VectorEngine::loadSnapshot(const std::string& path) {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    std::ifstream in(path, std::ios::binary);
    if (!in) return false;
    
    clear();
    
    size_t count;
    in.read((char*)&count, sizeof(size_t));
    for (size_t i = 0; i < count; ++i) {
        size_t id_len;
        in.read((char*)&id_len, sizeof(size_t));
        std::string id(id_len, ' ');
        in.read(&id[0], id_len);
        
        size_t vec_size;
        in.read((char*)&vec_size, sizeof(size_t));
        std::vector<float> vec(vec_size);
        in.read((char*)vec.data(), vec_size * sizeof(float));
        
        addVector(vec, id);
    }
    
    size_t deleted_count;
    in.read((char*)&deleted_count, sizeof(size_t));
    for (size_t i = 0; i < deleted_count; ++i) {
        int idx;
        in.read((char*)&idx, sizeof(int));
        deleted_nodes_.insert(idx);
    }
    
    return true;
}

void VectorEngine::insertHNSW(int node_idx) {
    HNSWNode* new_node = nullptr;
    int max_l = -1;
    int curr_node_idx = -1;
    
    {
        std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
        if (node_idx >= (int)nodes_.size()) return;
        if (deleted_nodes_.count(node_idx)) return;
        new_node = nodes_[node_idx];
        if (entry_point_id_ != -1) {
            curr_node_idx = entry_point_id_;
            max_l = nodes_[entry_point_id_]->max_layer;
        }
    }
    
    int target_layer = getRandomLayer();
    new_node->max_layer = target_layer;

    if (curr_node_idx == -1) {
        std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
        entry_point_id_ = node_idx;
        return;
    }

    std::vector<float> query_vec;
    {
        std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
        if (node_idx >= (int)store_.size()) return;
        query_vec = store_[node_idx];
    }
    
    for (int l = max_l; l > target_layer; --l) {
        bool changed = true;
        while (changed) {
            changed = false;
            float curr_sim = dot_product_simd(query_vec.data(), store_[curr_node_idx].data(), query_vec.size());
            HNSWNode* curr_node = nodes_[curr_node_idx];
            for (int neighbor : curr_node->neighbors[l]) {
                float sim = dot_product_simd(query_vec.data(), store_[neighbor].data(), query_vec.size());
                if (sim > curr_sim) {
                    curr_node_idx = neighbor;
                    curr_sim = sim;
                    changed = true;
                }
            }
        }
    }

    static thread_local std::vector<int> visited_flags;
    static thread_local int current_version = 0;
    if (visited_flags.size() < nodes_.capacity()) {
        visited_flags.resize(nodes_.capacity() + 1000, 0);
    }
    current_version++;

    int efConstruction = efConstruction_;
    for (int l = std::min(target_layer, (int)MAX_LAYERS - 1); l >= 0; --l) {
        std::priority_queue<std::pair<float, int>, std::vector<std::pair<float, int>>, std::greater<>> top_k;
        std::priority_queue<std::pair<float, int>> candidates;
        
        float start_sim = dot_product_simd(query_vec.data(), store_[curr_node_idx].data(), query_vec.size());
        candidates.push({start_sim, curr_node_idx});
        top_k.push({start_sim, curr_node_idx});
        visited_flags[curr_node_idx] = current_version;

        std::vector<std::pair<float, int>> layer_results;
        while (!candidates.empty()) {
            auto [dist, c] = candidates.top(); candidates.pop();
            if (top_k.size() >= (size_t)efConstruction && dist < top_k.top().first) break;

            HNSWNode* node_c = nodes_[c];
            for (int neighbor : node_c->neighbors[l]) {
                if (visited_flags[neighbor] != current_version) {
                    visited_flags[neighbor] = current_version;
                    float sim = dot_product_simd(query_vec.data(), store_[neighbor].data(), query_vec.size());
                    
                    if (top_k.size() < (size_t)efConstruction || sim > top_k.top().first) {
                        candidates.push({sim, neighbor});
                        top_k.push({sim, neighbor});
                        if (top_k.size() > (size_t)efConstruction) top_k.pop();
                    }
                }
            }
        }

        while(!top_k.empty()) {
            layer_results.push_back(top_k.top());
            top_k.pop();
        }
        std::sort(layer_results.begin(), layer_results.end(), std::greater<>());
        curr_node_idx = layer_results[0].second;
        {
            std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
            for (auto& [sim, nbr] : layer_results) {
                if (nbr == node_idx) continue;
                HNSWNode* node_self = nodes_[node_idx];
                HNSWNode* node_nbr = nodes_[nbr];

                // Add nbr to self
                if (node_self->neighbors[l].size() < (size_t)M_) {
                    node_self->neighbors[l].push_back(nbr);
                }

                // Add self to nbr (bidirectional)
                bool exists = false;
                for (int n : node_nbr->neighbors[l]) if (n == node_idx) { exists = true; break; }
                if (!exists) {
                    node_nbr->neighbors[l].push_back(node_idx);
                    if (node_nbr->neighbors[l].size() > (size_t)M_) {
                        // Keep only best M
                        std::priority_queue<std::pair<float, int>, std::vector<std::pair<float, int>>, std::greater<>> neighbors_heap;
                        for (int n : node_nbr->neighbors[l]) {
                            float s = dot_product_simd(store_[nbr].data(), store_[n].data(), store_[nbr].size());
                            neighbors_heap.push({s, n});
                            if (neighbors_heap.size() > (size_t)M_) neighbors_heap.pop();
                        }
                        node_nbr->neighbors[l].clear();
                        while (!neighbors_heap.empty()) {
                            node_nbr->neighbors[l].push_back(neighbors_heap.top().second);
                            neighbors_heap.pop();
                        }
                    }
                }
            }
        }
    }

    {
        std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
        if (entry_point_id_ == -1 || target_layer > nodes_[entry_point_id_]->max_layer) {
            entry_point_id_ = node_idx;
        }
    }
}

VectorEngine::VectorEngine(int M, int efConstruction, int efSearch) 
    : entry_point_id_(-1), max_id_(0), stop_worker_(false), M_(M), efConstruction_(efConstruction), efSearch_default_(efSearch) {
    store_.reserve(1000000);
    id_map_.reserve(1000000);
    nodes_.reserve(1000000);
    worker_thread_ = std::thread(&VectorEngine::backgroundWorkerLoop, this);
}

void VectorEngine::reconfigure(int M, int efConstruction, int efSearch) {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    M_ = M;
    efConstruction_ = efConstruction;
    efSearch_default_ = efSearch;
    std::cout << "[VectorEngine] Reconfigured: M=" << M_ << ", efConstruction=" << efConstruction_ << ", efSearch=" << efSearch_default_ << std::endl;
}

VectorEngine::~VectorEngine() {
    {
        std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
        stop_worker_ = true;
    }
    worker_cv_.notify_all();
    if (worker_thread_.joinable()) {
        worker_thread_.join();
    }
}

void VectorEngine::addVector(const std::vector<float>& vec, const std::string& id) {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    
    // Fix #8: Enforce dimensionality consistency (Fail-fast)
    if (!store_.empty() && vec.size() != store_[0].size()) {
        throw std::invalid_argument("Dimension mismatch: expected " + std::to_string(store_[0].size()) + ", got " + std::to_string(vec.size()));
    }

    std::vector<float> norm_vec = vec;
    normalizeVector(norm_vec);

    int node_idx = store_.size();
    store_.push_back(norm_vec);
    id_map_.push_back(id);
    nodes_.push_back(new HNSWNode(node_idx));
    active_buffer_.push_back(node_idx);
    worker_cv_.notify_one();
}

void VectorEngine::backgroundWorkerLoop() {
    while (true) {
        int node_to_index = -1;
        {
            std::unique_lock<std::recursive_mutex> lock(engine_mutex_);
            worker_cv_.wait(lock, [this] { return stop_worker_ || !active_buffer_.empty(); });
            if (stop_worker_ && active_buffer_.empty()) break;
            if (!active_buffer_.empty()) {
                node_to_index = active_buffer_.front();
                active_buffer_.pop_front();
            }
        }
        if (node_to_index != -1) {
            try {
                std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
                // Verify node still exists and isn't deleted before indexing
                if (node_to_index < (int)nodes_.size() && deleted_nodes_.find(node_to_index) == deleted_nodes_.end()) {
                    insertHNSW(node_to_index);
                }
            } catch (const std::exception& e) {
                std::cerr << "Indexing Error: " << e.what() << std::endl;
            }
        }
    }
}

std::vector<std::pair<std::string, float>> VectorEngine::search(const std::vector<float>& query_vec, int k, int ef_search) {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    if (entry_point_id_ == -1) return {};

    int efSearch = (ef_search > 0) ? ef_search : efSearch_default_;
    int curr_node_idx = entry_point_id_;

    for (int l = nodes_[entry_point_id_]->max_layer; l > 0; --l) {
        bool changed = true;
        while (changed) {
            changed = false;
            float curr_sim = dot_product_simd(query_vec.data(), store_[curr_node_idx].data(), query_vec.size());
            HNSWNode* curr_node = nodes_[curr_node_idx];
            for (int neighbor : curr_node->neighbors[l]) {
                float sim = dot_product_simd(query_vec.data(), store_[neighbor].data(), query_vec.size());
                if (sim > curr_sim) {
                    curr_node_idx = neighbor;
                    curr_sim = sim;
                    changed = true;
                }
            }
        }
    }

    std::priority_queue<std::pair<float, int>, std::vector<std::pair<float, int>>, std::greater<>> top_k;
    std::priority_queue<std::pair<float, int>> candidates;
    
    static thread_local std::vector<int> search_visited_flags;
    static thread_local int search_version = 0;
    if (search_visited_flags.size() < nodes_.size() + 1) search_visited_flags.resize(nodes_.size() + 1000, 0);
    search_version++;

    float start_sim = dot_product_simd(query_vec.data(), store_[curr_node_idx].data(), query_vec.size());
    candidates.push({start_sim, curr_node_idx});
    top_k.push({start_sim, curr_node_idx});
    search_visited_flags[curr_node_idx] = search_version;

    while (!candidates.empty()) {
        auto [dist, c] = candidates.top(); candidates.pop();
        if (top_k.size() >= (size_t)efSearch && dist < top_k.top().first) break;

        HNSWNode* node_c = nodes_[c];
        for (int neighbor : node_c->neighbors[0]) {
            if (search_visited_flags[neighbor] != search_version) {
                search_visited_flags[neighbor] = search_version;
                float sim = dot_product_simd(query_vec.data(), store_[neighbor].data(), query_vec.size());
                
                if (top_k.size() < (size_t)efSearch || sim > top_k.top().first) {
                    candidates.push({sim, neighbor});
                    top_k.push({sim, neighbor});
                    if (top_k.size() > (size_t)efSearch) top_k.pop();
                }
            }
        }
    }

    std::vector<std::pair<int, float>> combined_results;
    while (!top_k.empty()) {
        if (deleted_nodes_.find(top_k.top().second) == deleted_nodes_.end()) {
            combined_results.push_back({top_k.top().second, top_k.top().first});
        }
        top_k.pop();
    }

    for (int buffer_idx : active_buffer_) {
        if (deleted_nodes_.find(buffer_idx) == deleted_nodes_.end()) {
            float sim = dot_product_simd(query_vec.data(), store_[buffer_idx].data(), query_vec.size());
            combined_results.push_back({buffer_idx, sim});
        }
    }

    std::sort(combined_results.begin(), combined_results.end(), [](const auto& a, const auto& b) {
        return a.second > b.second;
    });

    std::vector<std::pair<std::string, float>> final_results;
    std::set<int> seen;
    for (const auto& res : combined_results) {
        if (seen.find(res.first) == seen.end()) {
            final_results.push_back({id_map_[res.first], res.second});
            seen.insert(res.first);
            if (final_results.size() >= (size_t)k) break;
        }
    }
    
    return final_results;
}

const char* getSIMDBackend() {
    return SIMD_IMPL;
}
