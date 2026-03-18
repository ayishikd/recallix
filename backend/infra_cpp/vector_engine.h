#ifndef VECTOR_ENGINE_H
#define VECTOR_ENGINE_H

#include <string>
#include <vector>

struct Vector {
  std::vector<float> data;
  std::string id;
};

class VectorEngine {
public:
  void addVector(const std::string &id, const std::vector<float> &data);
  std::vector<std::string> search(const std::vector<float> &query, int topK);
  void removeVector(const std::string &id);
  void save(const std::string &filename);
  void load(const std::string &filename);

private:
  std::vector<Vector> store_;
  float cosineSimilarity(const std::vector<float> &v1,
                         const std::vector<float> &v2);
};

#endif
