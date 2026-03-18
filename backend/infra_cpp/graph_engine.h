#ifndef GRAPH_ENGINE_H
#define GRAPH_ENGINE_H

#include <map>
#include <string>
#include <vector>

struct Edge {
  std::string target;
  std::string relation;
};

class GraphEngine {
public:
  void addNode(const std::string &id, const std::string &type);
  void addEdge(const std::string &source, const std::string &target,
               const std::string &relation);
  void removeNode(const std::string &id);
  std::vector<Edge> getNeighbors(const std::string &id);

private:
  std::map<std::string, std::string> nodes_; // id -> type
  std::map<std::string, std::vector<Edge>> adjacency_list_;
};

#endif
