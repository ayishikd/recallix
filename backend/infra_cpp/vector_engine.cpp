#include "vector_engine.h"
#include <iostream>
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
        // Horizontal sum of 8 floats
        __m128 hi = _mm256_extractf128_ps(sum, 1);
        __m128 lo = _mm256_castps256_ps128(sum);
        __m128 sum128 = _mm_add_ps(lo, hi);
        sum128 = _mm_hadd_ps(sum128, sum128);
        sum128 = _mm_hadd_ps(sum128, sum128);
        float result = _mm_cvtss_f32(sum128);
        // Handle remainder
        for (; i < size; ++i) result += a[i] * b[i];
        return result;
    }

#elif defined(__SSE__)
    #include <xmmintrin.h>
    #include <pmmintrin.h>
    #define SIMD_IMPL "SSE"

    float dot_product_simd(const float* a, const float* b, int size) {
        __m128 sum = _mm_setzero_ps();
        int i = 0;
        for (; i + 4 <= size; i += 4) {
            __m128 va = _mm_loadu_ps(a + i);
            __m128 vb = _mm_loadu_ps(b + i);
            sum = _mm_add_ps(sum, _mm_mul_ps(va, vb));
        }
        // Horizontal sum of 4 floats
        sum = _mm_hadd_ps(sum, sum);
        sum = _mm_hadd_ps(sum, sum);
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

void VectorEngine::clear() {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    store_.clear();
    id_map_.clear();
    active_buffer_.clear();
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

void VectorEngine::insertHNSW(int node_idx) {
    HNSWNode* new_node = nullptr;
    int max_l = -1;
    int curr_node_idx = -1;
    
    {
        std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
        if (node_idx >= (int)nodes_.size()) return;
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

    const auto& query_vec = store_[node_idx];
    
    // 1. Greedy descent from top layer to target layer
    for (int l = max_l; l > target_layer; --l) {
        bool changed = true;
        while (changed) {
            changed = false;
            float curr_sim = dot_product_simd(query_vec.data(), store_[curr_node_idx].data(), query_vec.size());
            
            HNSWNode* curr_node = nodes_[curr_node_idx];
            for (int i = 0; i < curr_node->neighbor_counts[l]; ++i) {
                int neighbor = curr_node->neighbors[l][i];
                float sim = dot_product_simd(query_vec.data(), store_[neighbor].data(), query_vec.size());
                if (sim > curr_sim) {
                    curr_node_idx = neighbor;
                    curr_sim = sim;
                    changed = true;
                }
            }
        }
    }

    // 2. Beam search from target layer down to 0
    static thread_local std::vector<int> visited_flags;
    static thread_local int current_version = 0;
    if (visited_flags.size() < nodes_.capacity()) {
        visited_flags.resize(nodes_.capacity() + 1000, 0);
    }
    current_version++;

    const int efConstruction = 100;
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
            for (int i = 0; i < node_c->neighbor_counts[l]; ++i) {
                int neighbor = node_c->neighbors[l][i];
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

        // Neighbor linking with max M=16
        {
            std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
            for (auto& [sim, nbr] : layer_results) {
                if (nbr == node_idx) continue;
                HNSWNode* node_self = nodes_[node_idx];
                HNSWNode* node_nbr = nodes_[nbr];

                // Ensure uniqueness in node_self->neighbors
                bool exists = false;
                for (int i = 0; i < node_self->neighbor_counts[l]; ++i) {
                    if (node_self->neighbors[l][i] == nbr) { exists = true; break; }
                }

                if (!exists && node_self->neighbor_counts[l] < 16) {
                    node_self->neighbors[l][node_self->neighbor_counts[l]++] = nbr;
                }
                
                // Ensure uniqueness in node_nbr->neighbors
                exists = false;
                for (int i = 0; i < node_nbr->neighbor_counts[l]; ++i) {
                    if (node_nbr->neighbors[l][i] == node_idx) { exists = true; break; }
                }

                if (!exists && node_nbr->neighbor_counts[l] < 16) {
                    node_nbr->neighbors[l][node_nbr->neighbor_counts[l]++] = node_idx;
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

VectorEngine::VectorEngine() : entry_point_id_(-1), max_id_(0), stop_worker_(false) {
    store_.reserve(1000000);
    id_map_.reserve(1000000);
    nodes_.reserve(1000000);
    worker_thread_ = std::thread(&VectorEngine::backgroundWorkerLoop, this);
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
    int node_idx = store_.size();
    store_.push_back(vec);
    id_map_.push_back(id);
    
    // Create node (not yet linked in HNSW)
    nodes_.push_back(new HNSWNode(node_idx));
    
    // Push to active buffer for background indexing
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
                insertHNSW(node_to_index);
                if (node_to_index % 1000 == 0) {
                    std::cout << "Index progress: " << node_to_index << " nodes indexed." << std::endl;
                }
            } catch (const std::exception& e) {
                std::cerr << "Indexing Error: " << e.what() << std::endl;
            }
        }
    }
}

std::vector<std::pair<std::string, float>> VectorEngine::search(const std::vector<float>& query_vec, int k) {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    if (entry_point_id_ == -1) return {};

    int efSearch = 50; 
    int curr_node_idx = entry_point_id_;

    // 1. Greedy descent to layer 0
    for (int l = nodes_[entry_point_id_]->max_layer; l > 0; --l) {
        bool changed = true;
        while (changed) {
            changed = false;
            float curr_sim = dot_product_simd(query_vec.data(), store_[curr_node_idx].data(), query_vec.size());
            HNSWNode* curr_node = nodes_[curr_node_idx];
            for (int i = 0; i < curr_node->neighbor_counts[l]; ++i) {
                int neighbor = curr_node->neighbors[l][i];
                float sim = dot_product_simd(query_vec.data(), store_[neighbor].data(), query_vec.size());
                if (sim > curr_sim) {
                    curr_node_idx = neighbor;
                    curr_sim = sim;
                    changed = true;
                }
            }
        }
    }

    // 2. Beam search at layer 0
    std::priority_queue<std::pair<float, int>, std::vector<std::pair<float, int>>, std::greater<>> top_k;
    std::priority_queue<std::pair<float, int>> candidates;
    
    // Use the versioned visited list
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
        for (int i = 0; i < node_c->neighbor_counts[0]; ++i) {
            int neighbor = node_c->neighbors[0][i];
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
        combined_results.push_back({top_k.top().second, top_k.top().first});
        top_k.pop();
    }

    // 3. Brute-force search on active buffer
    for (int buffer_idx : active_buffer_) {
        float sim = dot_product_simd(query_vec.data(), store_[buffer_idx].data(), query_vec.size());
        combined_results.push_back({buffer_idx, sim});
    }

    // 4. Sort and return top K
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
