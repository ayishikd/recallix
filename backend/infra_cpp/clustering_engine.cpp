#include "clustering_engine.h"
#include <iostream>

void ClusteringEngine::addMemoryToCluster(const std::string &clusterId,
                                          const std::string &memoryId) {
  clusters_[clusterId].clusterId = clusterId;
  clusters_[clusterId].memberIds.push_back(memoryId);
}

std::vector<Cluster> ClusteringEngine::getClusters() {
  std::vector<Cluster> results;
  for (auto const &[id, cluster] : clusters_) {
    results.push_back(cluster);
  }
  return results;
}

void ClusteringEngine::clusterMemories(
    const std::map<std::string, std::vector<float>> &vectorStore) {
  std::cout << "Clustering " << vectorStore.size() << " memories..."
            << std::endl;
  // Mock clustering logic: group by first character of ID
  for (auto const &[id, vec] : vectorStore) {
    std::string clusterId = "cluster_" + id.substr(0, 1);
    addMemoryToCluster(clusterId, id);
  }
}
