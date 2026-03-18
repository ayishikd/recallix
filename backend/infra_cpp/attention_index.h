#ifndef ATTENTION_INDEX_H
#define ATTENTION_INDEX_H

#include <algorithm>
#include <string>
#include <vector>

struct ScoredItem {
  std::string id;
  float score;
};

class AttentionIndex {
public:
  std::vector<std::string> filter(const std::vector<ScoredItem> &items,
                                  int topN) {
    std::vector<ScoredItem> sortedItems = items;
    std::sort(sortedItems.begin(), sortedItems.end(),
              [](const ScoredItem &a, const ScoredItem &b) {
                return a.score > b.score;
              });

    std::vector<std::string> results;
    int count = std::min((int)sortedItems.size(), topN);
    for (int i = 0; i < count; ++i) {
      results.push_back(sortedItems[i].id);
    }
    return results;
  }
};

#endif
