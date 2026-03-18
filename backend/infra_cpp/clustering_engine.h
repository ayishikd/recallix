#ifndef CLUSTERING_ENGINE_H
#define CLUSTERING_ENGINE_H

#include <map>
#include <string>
#include <vector>

struct Cluster {
  std::string clusterId;
  std::string topic;
  std::string summary;
  std::vector<std::string> memberIds;
};

class ClusteringEngine {
public:
  void addMemoryToCluster(const std::string &clusterId,
                          const std::string &memoryId);
  std::vector<Cluster> getClusters();
  void
  clusterMemories(const std::map<std::string, std::vector<float>> &vectorStore);

private:
  std::map<std::string, Cluster> clusters_;
};

#endif
