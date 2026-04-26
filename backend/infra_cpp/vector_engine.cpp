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
    for (auto node : nodes_) delete node;
    nodes_.clear();
    entry_point_id_ = -1;
    std::cout << "🧹 C++ Vector Engine cleared." << std::endl;
}

void VectorEngine::insertHNSW(int node_idx) {
    HNSWNode* new_node = new HNSWNode(node_idx);
    int target_layer = getRandomLayer();
    new_node->max_layer = target_layer;
    
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    nodes_.push_back(new_node);

    if (entry_point_id_ == -1) {
        entry_point_id_ = node_idx;
        return;
    }

    int curr_node_idx = entry_point_id_;
    const auto& query_vec = store_[node_idx];

    // Greedy descent from top layer to target layer
    for (int l = nodes_[entry_point_id_]->max_layer; l > target_layer; --l) {
        bool changed = true;
        while (changed) {
            changed = false;
            float curr_sim = calculateCosineSimilarity(query_vec, store_[curr_node_idx]);
            for (int neighbor : nodes_[curr_node_idx]->neighbors[l]) {
                float sim = calculateCosineSimilarity(query_vec, store_[neighbor]);
                if (sim > curr_sim) {
                    curr_node_idx = neighbor;
                    curr_sim = sim;
                    changed = true;
                }
            }
        }
    }

    // efConstruction = 100: search beam width during graph construction
    const int efConstruction = 100;

    for (int l = std::min(target_layer, (int)MAX_LAYERS - 1); l >= 0; --l) {
        std::priority_queue<std::pair<float, int>> candidates;
        candidates.push({calculateCosineSimilarity(query_vec, store_[curr_node_idx]), curr_node_idx});
        
        std::set<int> visited;
        visited.insert(curr_node_idx);
        visited.insert(node_idx);

        std::vector<std::pair<float, int>> layer_results;
        while (!candidates.empty()) {
            auto [dist, c] = candidates.top(); candidates.pop();
            layer_results.push_back({dist, c});
            if ((int)layer_results.size() > efConstruction) break;

            for (int neighbor : nodes_[c]->neighbors[l]) {
                if (visited.find(neighbor) == visited.end()) {
                    visited.insert(neighbor);
                    float sim = calculateCosineSimilarity(query_vec, store_[neighbor]);
                    candidates.push({sim, neighbor});
                }
            }
        }

        // The best node found in this layer becomes the starting point for the next layer down
        if (!layer_results.empty()) {
            curr_node_idx = layer_results[0].second;
        }

        // M = 16: max neighbors per node per layer
        for (auto& [sim, nbr] : layer_results) {
            nodes_[node_idx]->neighbors[l].push_back(nbr);
            nodes_[nbr]->neighbors[l].push_back(node_idx);
            
            // Trim neighbors for existing node
            if (nodes_[nbr]->neighbors[l].size() > 16) {
                int n_idx = nbr;
                std::sort(nodes_[nbr]->neighbors[l].begin(), nodes_[nbr]->neighbors[l].end(), [&](int a, int b) {
                    return calculateCosineSimilarity(store_[n_idx], store_[a]) > calculateCosineSimilarity(store_[n_idx], store_[b]);
                });
                nodes_[nbr]->neighbors[l].resize(16);
            }
        }

        // Trim neighbors for NEW node
        if (nodes_[node_idx]->neighbors[l].size() > 16) {
            int n_idx = node_idx;
            std::sort(nodes_[node_idx]->neighbors[l].begin(), nodes_[node_idx]->neighbors[l].end(), [&](int a, int b) {
                return calculateCosineSimilarity(store_[n_idx], store_[a]) > calculateCosineSimilarity(store_[n_idx], store_[b]);
            });
            nodes_[node_idx]->neighbors[l].resize(16);
        }
    }

    // Update global entry point if new node is higher
    {
        std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
        if (entry_point_id_ == -1 || target_layer > nodes_[entry_point_id_]->max_layer) {
            entry_point_id_ = node_idx;
        }
    }
}

void VectorEngine::addVector(const std::vector<float>& vec, const std::string& id) {
    std::lock_guard<std::recursive_mutex> lock(engine_mutex_);
    int node_idx = store_.size();
    store_.push_back(vec);
    id_map_.push_back(id);
    insertHNSW(node_idx);
}

std::vector<std::pair<std::string, float>> VectorEngine::search(const std::vector<float>& query_vec, int k) {
    if (entry_point_id_ == -1) return {};

    int curr_node_idx = entry_point_id_;
    int efSearch = 50; 

    // Greedy descent from top layer to layer 0
    for (int l = nodes_[entry_point_id_]->max_layer; l > 0; --l) {
        bool changed = true;
        while (changed) {
            changed = false;
            float curr_sim = calculateCosineSimilarity(query_vec, store_[curr_node_idx]);
            for (int neighbor : nodes_[curr_node_idx]->neighbors[l]) {
                float sim = calculateCosineSimilarity(query_vec, store_[neighbor]);
                if (sim > curr_sim) {
                    curr_node_idx = neighbor;
                    curr_sim = sim;
                    changed = true;
                }
            }
        }
    }

    // Layer-0 beam search with efSearch candidates
    std::priority_queue<std::pair<float, int>, std::vector<std::pair<float, int>>, std::greater<>> top_k;
    std::priority_queue<std::pair<float, int>> candidates;
    
    float start_sim = calculateCosineSimilarity(query_vec, store_[curr_node_idx]);
    candidates.push({start_sim, curr_node_idx});
    top_k.push({start_sim, curr_node_idx});
    
    std::set<int> visited;
    visited.insert(curr_node_idx);

    while (!candidates.empty()) {
        auto [sim, c] = candidates.top(); candidates.pop();
        if (sim < top_k.top().first && top_k.size() >= (size_t)efSearch) break;

        for (int neighbor : nodes_[c]->neighbors[0]) {
            if (visited.find(neighbor) == visited.end()) {
                visited.insert(neighbor);
                float n_sim = calculateCosineSimilarity(query_vec, store_[neighbor]);
                if (n_sim > top_k.top().first || top_k.size() < (size_t)efSearch) {
                    candidates.push({n_sim, neighbor});
                    top_k.push({n_sim, neighbor});
                    if (top_k.size() > (size_t)efSearch) top_k.pop();
                }
            }
        }
    }

    std::vector<std::pair<std::string, float>> results;
    while (!top_k.empty()) {
        results.push_back({id_map_[top_k.top().second], top_k.top().first});
        top_k.pop();
    }
    std::reverse(results.begin(), results.end());
    if (results.size() > (size_t)k) results.resize(k);
    return results;
}

const char* getSIMDBackend() {
    return SIMD_IMPL;
}
