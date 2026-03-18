#ifndef TIMELINE_ENGINE_H
#define TIMELINE_ENGINE_H

#include <map>
#include <string>
#include <vector>

struct TimelineEvent {
  std::string content;
  double timestamp;
};

class TimelineEngine {
public:
  void appendEvent(const std::string &userId, const std::string &content,
                   double timestamp);
  void removeEvent(const std::string &userId, const std::string &content);
  std::vector<TimelineEvent> getSequence(const std::string &userId, int limit);
  std::vector<std::string> detectPatterns(const std::string &userId);

private:
  std::map<std::string, std::vector<TimelineEvent>> timelines_;
};

#endif
