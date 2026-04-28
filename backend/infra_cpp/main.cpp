#include "httplib.h"
#include "json.hpp"
#include "vector_engine.h"
#include "timeline_engine.h"
#include "graph_engine.h"
#include "clustering_engine.h"
#include "event_queue.h"
#include "attention_index.h"
#include "memory_indexer.h"
#include <iostream>

using json = nlohmann::json;

int main() {
    std::cout << "🚀 Recallix C++ Infrastructure Starting..." << std::endl;

    VectorEngine vEngine;
    TimelineEngine timelineEngine;
    GraphEngine graphEngine;
    ClusteringEngine clusterEngine;
    EventQueue queue;
    AttentionIndex attentionIndex;
    MemoryIndexer indexer;

    httplib::Server svr;

    // --- Vector Engine Endpoints ---
    svr.Post("/add_vector", [&](const httplib::Request &req, httplib::Response &res) {
        try {
            auto j = json::parse(req.body);
            // Use the string ID from Python
            std::string id = j["id"].get<std::string>();
            vEngine.addVector(j["vector"].get<std::vector<float>>(), id);
            res.set_content("{\"status\":\"ok\"}", "application/json");
        } catch (std::exception& e) {
            std::cerr << "Error in /add_vector: " << e.what() << std::endl;
            res.status = 400;
        }
    });

    svr.Post("/bulk_add", [&](const httplib::Request &req, httplib::Response &res) {
        try {
            auto j = json::parse(req.body);
            auto vectors = j["vectors"];
            for (auto& v : vectors) {
                vEngine.addVector(v["vector"].get<std::vector<float>>(), v["id"].get<std::string>());
            }
            res.set_content("{\"status\":\"ok\"}", "application/json");
        } catch (std::exception& e) {
            std::cerr << "Error in /bulk_add: " << e.what() << std::endl;
            res.status = 400;
        }
    });

    svr.Post("/search_vector", [&](const httplib::Request &req, httplib::Response &res) {
        try {
            auto j = json::parse(req.body);
            auto results = vEngine.search(j["query"].get<std::vector<float>>(), j["top_k"]);
            
            json j_res = json::array();
            for (auto& r : results) {
                // Return string ID directly
                j_res.push_back({{"id", r.first}, {"score", r.second}});
            }
            res.set_content(json({{"results", j_res}}).dump(), "application/json");
        } catch (std::exception& e) {
            std::cerr << "Error in /search_vector: " << e.what() << std::endl;
            res.status = 400;
        }
    });

    svr.Post("/clear", [&](const httplib::Request &req, httplib::Response &res) {
        vEngine.clear();
        res.set_content("{\"status\":\"ok\", \"message\":\"System cleared\"}", "application/json");
    });

    // --- System Status ---
    svr.Get("/status", [&](const httplib::Request &req, httplib::Response &res) {
        res.set_content(json({
            {"status", "online"},
            {"pending_count", vEngine.getPendingCount()}
        }).dump(), "application/json");
    });

    svr.Get("/health", [](const httplib::Request &req, httplib::Response &res) {
        res.set_content("{\"status\":\"healthy\", \"engine\":\"HNSW+NEON\"}", "application/json");
    });

    std::cout << "✅ Service is running on http://localhost:8080" << std::endl;
    svr.listen("0.0.0.0", 8080);

    return 0;
}
