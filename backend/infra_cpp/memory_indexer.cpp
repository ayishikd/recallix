#include "memory_indexer.h"
#include <ctime>
#include <iostream>

void MemoryIndexer::index(const std::string &id, int importance,
                          int accessCount) {
  index_[id] = {(long)importance, (long)std::time(nullptr), accessCount};
}

void MemoryIndexer::compact() {
  std::cout << "Starting memory compaction with decay..." << std::endl;
  long now = (long)std::time(nullptr);

  for (auto it = index_.begin(); it != index_.end();) {
    long t = now - it->second.lastAccessed;
    // Stability S increases with more accesses
    float stability = (it->second.importance * 0.5f) *
                      (1.0f + std::log((float)it->second.accessCount + 1.0f));
    stability = std::max(stability, 0.1f);

    // retention = e^(-t/stability)
    float retention = std::exp(-(float)t / (stability * 3600.0f));

    // Demo mode: if time is small, scale stability down
    if (t < 3600)
      retention = std::exp(-(float)t / stability);

    float strength = retention * it->second.importance;

    if (strength < 1.0f) { // Threshold for forgetting
      std::cout << "Forgetting memory: " << it->first
                << " (Strength: " << strength << ")" << std::endl;
      it = index_.erase(it);
    } else {
      ++it;
    }
  }
  std::cout << "Compaction finished." << std::endl;
}

std::vector<std::string> MemoryIndexer::getImportantMemories() const {
  std::vector<std::string> results;
  for (const auto &pair : index_) {
    results.push_back(pair.first);
  }
  return results;
}
