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

    // --- Configuration Endpoint ---
    svr.Post("/configure", [&](const httplib::Request &req, httplib::Response &res) {
        try {
            auto j = json::parse(req.body);
            int M = j.value("M", 32);
            int efC = j.value("efConstruction", 400);
            int efS = j.value("efSearch", 100);
            
            vEngine.clear(); 
            vEngine.reconfigure(M, efC, efS);
            
            res.set_content("{\"status\":\"ok\", \"message\":\"HNSW configured\"}", "application/json");
        } catch (std::exception& e) {
            res.status = 400;
        }
    });

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
            int ef_search = j.value("ef_search", -1);
            auto results = vEngine.search(j["query"].get<std::vector<float>>(), j["top_k"], ef_search);
            
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

    svr.Post("/remove_vector", [&](const httplib::Request &req, httplib::Response &res) {
        try {
            auto j = json::parse(req.body);
            std::string id = j["id"].get<std::string>();
            vEngine.removeVector(id);
            res.set_content("{\"status\":\"ok\"}", "application/json");
        } catch (std::exception& e) {
            res.status = 400;
        }
    });

    svr.Post("/snapshot/save", [&](const httplib::Request &req, httplib::Response &res) {
        auto j = json::parse(req.body);
        std::string path = j.value("path", "memory_snapshot.bin");
        if (vEngine.saveSnapshot(path)) {
            res.set_content("{\"status\":\"ok\"}", "application/json");
        } else {
            res.status = 500;
        }
    });

    svr.Post("/snapshot/load", [&](const httplib::Request &req, httplib::Response &res) {
        auto j = json::parse(req.body);
        std::string path = j.value("path", "memory_snapshot.bin");
        if (vEngine.loadSnapshot(path)) {
            res.set_content("{\"status\":\"ok\"}", "application/json");
        } else {
            res.status = 500;
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

    svr.Get("/stats", [&](const httplib::Request &req, httplib::Response &res) {
        auto s = vEngine.getStats();
        res.set_content(json({
            {"total_nodes", s.total_nodes},
            {"pending_nodes", s.pending_nodes},
            {"entry_point_id", s.entry_point_id},
            {"max_layer", s.max_layer},
            {"M", s.M},
            {"efConstruction", s.efConstruction},
            {"efSearch", s.efSearch}
        }).dump(), "application/json");
    });

    svr.Get("/health", [](const httplib::Request &req, httplib::Response &res) {
        res.set_content("{\"status\":\"healthy\", \"engine\":\"HNSW+NEON\"}", "application/json");
    });

    // Increase payload limit for large bulk ingestions
    svr.set_payload_max_length(1024LL * 1024 * 1024); // 1GB

    std::cout << "✅ Service is running on http://127.0.0.1:8080" << std::endl;
    std::cout << "🔒 Internal Authentication: ENABLED" << std::endl;
    
    // Fix #13: Bind to localhost and add shared secret check
    svr.set_pre_routing_handler([](const httplib::Request& req, httplib::Response& res) {
        if (req.get_header_value("X-Internal-Key") != "Recallix-Core-8892") {
            res.status = 401;
            return httplib::Server::HandlerResponse::Handled;
        }
        return httplib::Server::HandlerResponse::Unhandled;
    });

    svr.listen("127.0.0.1", 8080);

    return 0;
}
