#ifndef EVENT_QUEUE_H
#define EVENT_QUEUE_H

#include <condition_variable>
#include <mutex>
#include <queue>
#include <string>

class EventQueue {
public:
  void push(const std::string &event);
  std::string pop();

private:
  std::queue<std::string> queue_;
  std::mutex mutex_;
  std::condition_variable cond_;
};

#endif
