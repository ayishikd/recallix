#include "vector_engine.h"
#include <iostream>
#include <chrono>
#include <random>
#include <vector>
#include <algorithm>
#include <cmath>
#include <thread>

int main() {
    const int num_nodes = 1000000;
    const int dim = 128;
    const int num_queries = 100;
    
    VectorEngine engine;
    
    std::cout << "🚀 Initializing 1,000,000 node benchmark..." << std::endl;
    std::cout << "   SIMD: " << getSIMDBackend() << " | M=16 | efConstruction=100 | efSearch=50 | dim=" << dim << std::endl;
    
    std::mt19937 rng(42);
    std::uniform_real_distribution<float> dist(-1.0, 1.0);
    
    auto start_build = std::chrono::high_resolution_clock::now();
    
    // Generate and add 1M vectors
    for (int i = 0; i < num_nodes; ++i) {
        std::vector<float> vec(dim);
        for (int d = 0; d < dim; ++d) vec[d] = dist(rng);
        
        // Normalize
        float norm = 0;
        for (float f : vec) norm += f * f;
        norm = sqrt(norm);
        for (float &f : vec) f /= norm;
        
        engine.addVector(vec, std::to_string(i));
        
        if (i > 0 && i % 100000 == 0) {
            auto now = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> elapsed = now - start_build;
            std::cout << "   Built " << i << " nodes... (" << elapsed.count() << "s elapsed)" << std::endl;
        }
    }
    
    auto end_ingest = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff_ingest = end_ingest - start_build;
    
    std::cout << "✅ Ingestion complete (" << num_nodes << " nodes) in " << diff_ingest.count() << " seconds." << std::endl;
    std::cout << "⏳ Waiting for background indexing to complete..." << std::endl;
    
    int next_milestone = 900000;
    while (engine.getPendingCount() > 0) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        int current = engine.getPendingCount();
        if (current <= next_milestone) {
            std::cout << "   Remaining in buffer: " << current << " nodes..." << std::endl;
            next_milestone -= 100000;
        }
    }
    
    auto end_index = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff_index = end_index - start_build;
    
    std::cout << "✅ Total Indexing complete in " << diff_index.count() << " seconds." << std::endl;
    
    // Search Benchmark
    std::cout << "🔍 Running " << num_queries << " random queries..." << std::endl;
    
    std::vector<double> latencies;
    for (int q = 0; q < num_queries; ++q) {
        std::vector<float> query(dim);
        for (int d = 0; d < dim; ++d) query[d] = dist(rng);
        
        // Normalize
        float norm = 0;
        for (float f : query) norm += f * f;
        norm = sqrt(norm);
        for (float &f : query) f /= norm;
        
        auto start_search = std::chrono::high_resolution_clock::now();
        auto results = engine.search(query, 5);
        auto end_search = std::chrono::high_resolution_clock::now();
        
        std::chrono::duration<double, std::milli> diff_search = end_search - start_search;
        latencies.push_back(diff_search.count());
    }
    
    double total_lat = 0;
    for (double l : latencies) total_lat += l;
    double avg_lat = total_lat / num_queries;
    
    std::sort(latencies.begin(), latencies.end());
    double p99 = latencies[(int)(num_queries * 0.99)];
    
    std::cout << "\n📊 FINAL MEASURED RESULTS (1,000,000 NODES):" << std::endl;
    std::cout << "   SIMD Backend:          " << getSIMDBackend() << std::endl;
    std::cout << "   Ingest Time:           " << diff_ingest.count() << " seconds" << std::endl;
    std::cout << "   Total Index Time:      " << diff_index.count() << " seconds" << std::endl;
    std::cout << "   Average Search Latency: " << avg_lat << " ms" << std::endl;
    std::cout << "   P99 Search Latency:     " << p99 << " ms" << std::endl;
    std::cout << "   Max Search Latency:     " << latencies.back() << " ms" << std::endl;
    
    return 0;
}
