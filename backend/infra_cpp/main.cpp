#include "attention_index.h"
#include "clustering_engine.h"
#include "event_queue.h"
#include "graph_engine.h"
#include "httplib.h"
#include "json.hpp"
#include "memory_indexer.h"
#include "timeline_engine.h"
#include "vector_engine.h"
#include <iostream>

using json = nlohmann::json;

int main() {
  std::cout << "Memory C++ Infrastructure Service Starting..." << std::endl;

  EventQueue queue;
  VectorEngine vEngine;
  MemoryIndexer indexer;
  ClusteringEngine clusterEngine;
  GraphEngine graphEngine;
  TimelineEngine timelineEngine;
  AttentionIndex attentionIndex;

  const std::string vector_path = "backend/storage/vector_store/vectors.bin";
  vEngine.load(vector_path);

  httplib::Server svr;

  // Timeline Endpoints
  svr.Post("/append_event", [&](const httplib::Request &req,
                                httplib::Response &res) {
    auto j = json::parse(req.body);
    timelineEngine.appendEvent(j["user_id"], j["content"], j["timestamp"]);
    res.set_content("{\"status\":\"ok\"}", "application/json");
  });

  svr.Get("/get_timeline", [&](const httplib::Request &req,
                               httplib::Response &res) {
    auto id = req.get_param_value("id");
    auto limit_str = req.get_param_value("limit");
    int limit = limit_str.empty() ? 50 : std::stoi(limit_str);
    auto events = timelineEngine.getSequence(id, limit);
    json j_results = json::array();
    for (const auto &e : events) {
      j_results.push_back({{"content", e.content}, {"timestamp", e.timestamp}});
    }
    res.set_content(j_results.dump(), "application/json");
  });

  // Attention Endpoint
  svr.Post("/attention_filter",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             int topN = j["top_n"];
             std::vector<ScoredItem> items;
             for (auto &item : j["items"]) {
               items.push_back({item["id"], item["score"]});
             }
             auto filtered = attentionIndex.filter(items, topN);
             res.set_content(json(filtered).dump(), "application/json");
           });

  // Clustering Endpoints
  svr.Post("/cluster",
           [&](const httplib::Request &req, httplib::Response &res) {
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  svr.Get("/get_clusters",
          [&](const httplib::Request &req, httplib::Response &res) {
            auto clusters = clusterEngine.getClusters();
            json j_results = json::array();
            for (const auto &c : clusters) {
              j_results.push_back({{"id", c.clusterId},
                                   {"topic", c.topic},
                                   {"summary", c.summary},
                                   {"members", c.memberIds}});
            }
            res.set_content(j_results.dump(), "application/json");
          });

  // Graph Endpoints
  svr.Post("/add_node",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             graphEngine.addNode(j["id"], j["type"]);
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  svr.Post("/add_edge",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             graphEngine.addEdge(j["source"], j["target"], j["relation"]);
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  svr.Get("/get_neighbors", [&](const httplib::Request &req,
                                httplib::Response &res) {
    auto id = req.get_param_value("id");
    auto neighbors = graphEngine.getNeighbors(id);
    json j_results = json::array();
    for (const auto &e : neighbors) {
      j_results.push_back({{"target", e.target}, {"relation", e.relation}});
    }
    res.set_content(j_results.dump(), "application/json");
  });

  // Event Queue Endpoint
  svr.Post("/push_event",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             queue.push(j["event"]);
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  svr.Get(
      "/pop_event", [&](const httplib::Request &req, httplib::Response &res) {
        std::string event = queue.pop();
        res.set_content(json({{"event", event}}).dump(), "application/json");
      });

  // Vector Search Endpoints
  svr.Post("/bulk_add", [&](const httplib::Request &req, httplib::Response &res) {
    auto j = json::parse(req.body);
    for (auto &item : j["vectors"]) {
      vEngine.addVector(item["id"], item["vector"].get<std::vector<float>>());
    }
    res.set_content("{\"status\":\"ok\"}", "application/json");
  });

  svr.Post("/add_vector",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             vEngine.addVector(j["id"], j["vector"].get<std::vector<float>>());
             // Sync disk write removed for benchmark performance
             // vEngine.save(vector_path);
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  svr.Post("/search_vector", [&](const httplib::Request &req,
                                 httplib::Response &res) {
    auto j = json::parse(req.body);
    auto results =
        vEngine.search(j["query"].get<std::vector<float>>(), j["top_k"]);
    res.set_content(json({{"results", results}}).dump(), "application/json");
  });

  svr.Post("/save_vectors", [&](const httplib::Request &req,
                                 httplib::Response &res) {
    vEngine.save(vector_path);
    res.set_content("{\"status\":\"ok\"}", "application/json");
  });

  svr.Post("/remove_vector",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             vEngine.removeVector(j["id"]);
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  svr.Post("/remove_node",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             graphEngine.removeNode(j["id"]);
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  svr.Post("/remove_timeline_event",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             timelineEngine.removeEvent(j["user_id"], j["content"]);
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  // Indexing Endpoint
  svr.Post("/index_memory",
           [&](const httplib::Request &req, httplib::Response &res) {
             auto j = json::parse(req.body);
             indexer.index(j["id"], j["importance"], j["access_count"]);
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  svr.Post("/compact",
           [&](const httplib::Request &req, httplib::Response &res) {
             indexer.compact();
             res.set_content("{\"status\":\"ok\"}", "application/json");
           });

  std::cout << "Service is running on http://localhost:8080" << std::endl;
  svr.listen("0.0.0.0", 8080);

  return 0;
}
