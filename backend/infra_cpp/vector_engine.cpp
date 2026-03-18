#include "vector_engine.h"
#include <algorithm>
#include <cmath>
#include <fstream>

void VectorEngine::addVector(const std::string &id,
                             const std::vector<float> &data) {
  store_.push_back({data, id});
}

void VectorEngine::removeVector(const std::string &id) {
  store_.erase(std::remove_if(store_.begin(), store_.end(),
                              [&id](const Vector &v) { return v.id == id; }),
               store_.end());
}

void VectorEngine::save(const std::string &filename) {
  std::ofstream os(filename, std::ios::binary);
  size_t size = store_.size();
  os.write(reinterpret_cast<const char *>(&size), sizeof(size));
  for (const auto &v : store_) {
    size_t id_len = v.id.size();
    os.write(reinterpret_cast<const char *>(&id_len), sizeof(id_len));
    os.write(v.id.data(), id_len);

    size_t vec_len = v.data.size();
    os.write(reinterpret_cast<const char *>(&vec_len), sizeof(vec_len));
    os.write(reinterpret_cast<const char *>(v.data.data()),
             vec_len * sizeof(float));
  }
}

void VectorEngine::load(const std::string &filename) {
  std::ifstream is(filename, std::ios::binary);
  if (!is)
    return;

  size_t size;
  is.read(reinterpret_cast<char *>(&size), sizeof(size));
  store_.clear();
  for (size_t i = 0; i < size; ++i) {
    size_t id_len;
    is.read(reinterpret_cast<char *>(&id_len), sizeof(id_len));
    std::string id(id_len, ' ');
    is.read(&id[0], id_len);

    size_t vec_len;
    is.read(reinterpret_cast<char *>(&vec_len), sizeof(vec_len));
    std::vector<float> data(vec_len);
    is.read(reinterpret_cast<char *>(data.data()), vec_len * sizeof(float));

    store_.push_back({data, id});
  }
}

float VectorEngine::cosineSimilarity(const std::vector<float> &v1,
                                     const std::vector<float> &v2) {
  if (v1.size() != v2.size())
    return 0.0f;
  float dot = 0.0f, n1 = 0.0f, n2 = 0.0f;
  for (size_t i = 0; i < v1.size(); ++i) {
    dot += v1[i] * v2[i];
    n1 += v1[i] * v1[i];
    n2 += v2[i] * v2[i];
  }
  if (n1 == 0 || n2 == 0)
    return 0.0f;
  return dot / (std::sqrt(n1) * std::sqrt(n2));
}

std::vector<std::string> VectorEngine::search(const std::vector<float> &query,
                                              int topK) {
  std::vector<std::pair<float, std::string>> scores;
  for (const auto &v : store_) {
    scores.push_back({cosineSimilarity(query, v.data), v.id});
  }

  std::sort(scores.begin(), scores.end(),
            [](const auto &a, const auto &b) { return a.first > b.first; });

  std::vector<std::string> results;
  for (int i = 0; i < std::min((int)scores.size(), topK); ++i) {
    results.push_back(scores[i].second);
  }
  return results;
}
