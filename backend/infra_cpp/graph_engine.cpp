#include "graph_engine.h"

void GraphEngine::addNode(const std::string &id, const std::string &type) {
  nodes_[id] = type;
}

void GraphEngine::addEdge(const std::string &source, const std::string &target,
                          const std::string &relation) {
  adjacency_list_[source].push_back({target, relation});
}

void GraphEngine::removeNode(const std::string &id) {
  nodes_.erase(id);
  adjacency_list_.erase(id);
  // Also remove outgoing edges from other nodes to this node
  for (auto &pair : adjacency_list_) {
    auto &edges = pair.second;
    edges.erase(std::remove_if(edges.begin(), edges.end(),
                               [&id](const Edge &e) { return e.target == id; }),
                edges.end());
  }
}

std::vector<Edge> GraphEngine::getNeighbors(const std::string &id) {
  if (adjacency_list_.count(id)) {
    return adjacency_list_[id];
  }
  return {};
}
