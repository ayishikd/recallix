#include "event_queue.h"

void EventQueue::push(const std::string &event) {
  std::lock_guard<std::mutex> lock(mutex_);
  queue_.push(event);
  cond_.notify_one();
}

std::string EventQueue::pop() {
  std::unique_lock<std::mutex> lock(mutex_);
  cond_.wait(lock, [this] { return !queue_.empty(); });
  std::string event = queue_.front();
  queue_.pop();
  return event;
}
