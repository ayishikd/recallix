#include "timeline_engine.h"
#include <algorithm>

void TimelineEngine::appendEvent(const std::string &userId,
                                 const std::string &content, double timestamp) {
  timelines_[userId].push_back({content, timestamp});
}

void TimelineEngine::removeEvent(const std::string &userId,
                                 const std::string &content) {
  if (timelines_.count(userId)) {
    auto &events = timelines_[userId];
    events.erase(std::remove_if(events.begin(), events.end(),
                                [&content](const TimelineEvent &e) {
                                  return e.content == content;
                                }),
                 events.end());
  }
}

std::vector<TimelineEvent>
TimelineEngine::getSequence(const std::string &userId, int limit) {
  if (timelines_.count(userId)) {
    auto &events = timelines_[userId];
    int start = std::max(0, (int)events.size() - limit);
    return std::vector<TimelineEvent>(events.begin() + start, events.end());
  }
  return {};
}

std::vector<std::string>
TimelineEngine::detectPatterns(const std::string &userId) {
  // Mock pattern detection
  return {"sequence_pattern_alpha"};
}
