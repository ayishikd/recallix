#include "vector_engine.h"
#include <iostream>
#include <algorithm>
#include <queue>
#include <cmath>
#include <set>
#include <arm_neon.h>

thread_local VectorEngine::ThreadCtx VectorEngine::ctx;

float dot_product_neon(const float* a, const float* b, int size) {
    float32x4_t sum_vec = vdupq_n_f32(0.0f);
    for (int i = 0; i < size; i += 4) {
        float32x4_t va = vld1q_f32(a + i);
        float32x4_t vb = vld1q_f32(b + i);
        sum_vec = vfmaq_f32(sum_vec, va, vb);
    }
    return vaddvq_f32(sum_vec);
}

float VectorEngine::calculateCosineSimilarity(const std::vector<float>& a, const std::vector<float>& b) {
    if (a.size() != b.size()) return 0.0f;
    float dot = dot_product_neon(a.data(), b.data(), a.size());
    float norm_a = std::sqrt(dot_product_neon(a.data(), a.data(), a.size()));
    float norm_b = std::sqrt(dot_product_neon(b.data(), b.data(), b.size()));
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
    std::lock_guard<std::mutex> lock(engine_mutex_);
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
    
    std::lock_guard<std::mutex> lock(engine_mutex_);
    nodes_.push_back(new_node);

    if (entry_point_id_ == -1) {
        entry_point_id_ = node_idx;
        return;
    }

    int curr_node_idx = entry_point_id_;
    const auto& query_vec = store_[node_idx];

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

    for (int l = std::min(target_layer, (int)MAX_LAYERS - 1); l >= 0; --l) {
        std::priority_queue<std::pair<float, int>> candidates;
        candidates.push({calculateCosineSimilarity(query_vec, store_[curr_node_idx]), curr_node_idx});
        
        std::set<int> visited;
        visited.insert(curr_node_idx);
        visited.insert(node_idx);

        std::vector<std::pair<float, int>> results;
        while (!candidates.empty()) {
            auto [dist, c] = candidates.top(); candidates.pop();
            results.push_back({dist, c});
            if (results.size() > 10) break;

            for (int neighbor : nodes_[c]->neighbors[l]) {
                if (visited.find(neighbor) == visited.end()) {
                    visited.insert(neighbor);
                    float sim = calculateCosineSimilarity(query_vec, store_[neighbor]);
                    candidates.push({sim, neighbor});
                }
            }
        }

        for (auto& [sim, neighbor] : results) {
            nodes_[node_idx]->neighbors[l].push_back(neighbor);
            nodes_[neighbor]->neighbors[l].push_back(node_idx);
            
            if (nodes_[neighbor]->neighbors[l].size() > 16) {
                std::sort(nodes_[neighbor]->neighbors[l].begin(), nodes_[neighbor]->neighbors[l].end(), [&](int a, int b) {
                    return calculateCosineSimilarity(store_[neighbor], store_[a]) > calculateCosineSimilarity(store_[neighbor], store_[b]);
                });
                nodes_[neighbor]->neighbors[l].resize(16);
            }
        }
    }
}

void VectorEngine::addVector(const std::vector<float>& vec, const std::string& id) {
    int node_idx = store_.size();
    store_.push_back(vec);
    id_map_.push_back(id);
    insertHNSW(node_idx);
}

std::vector<std::pair<std::string, float>> VectorEngine::search(const std::vector<float>& query_vec, int k) {
    if (entry_point_id_ == -1) return {};

    int curr_node_idx = entry_point_id_;
    int efSearch = 64; 

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
