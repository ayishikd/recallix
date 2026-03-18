#ifndef MEMORY_INDEXER_H
#define MEMORY_INDEXER_H

#include <map>
#include <string>
#include <vector>

struct MemoryMetadata {
  long importance;
  long lastAccessed;
  int accessCount;
};

class MemoryIndexer {
public:
  void index(const std::string &id, int importance, int accessCount);
  void compact();
  std::vector<std::string> getImportantMemories() const;

private:
  std::map<std::string, MemoryMetadata> index_;
};

#endif
