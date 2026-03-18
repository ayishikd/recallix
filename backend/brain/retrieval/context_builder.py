class ContextBuilder:
    def __init__(self, token_limit=2000):
        self.token_limit = token_limit

    def build(self, raw_results, planner_filters):
        """
        Merges results from multiple engines, ranks them, and applies limits.
        """
        final_set = []
        seen_content = set()

        # 1. Merge and Deduplicate
        for m_type, items in raw_results.items():
            if not items: continue # Skip empty engine results
            
            for item in items:
                # Basic normalization
                content = item.get("content") or item.get("id")
                if not content: continue
                
                content_str = str(content)
                if content_str not in seen_content:
                    importance = item.get("importance", 5.0)
                    
                    # Enforce importance filter from planner
                    if importance >= planner_filters.get("importance_min", 4.0):
                        memory_obj = {
                            "type": m_type,
                            "content": content_str,
                            "importance": importance
                        }
                        
                        # Add timestamp for episodic/timeline items
                        if "timestamp" in item:
                            memory_obj["timestamp"] = item["timestamp"]
                        elif "metadata" in item and "timestamp" in item["metadata"]:
                            memory_obj["timestamp"] = item["metadata"]["timestamp"]

                        final_set.append(memory_obj)
                        seen_content.add(content_str)

        # 2. Rank by Importance (High to Low)
        final_set.sort(key=lambda x: x["importance"], reverse=True)

        # 3. Token Budgeting (Simple approximation: 4 chars per token)
        output_set = []
        current_tokens = 0
        max_tokens = self.token_limit

        for item in final_set:
            tokens = len(item["content"]) // 4
            if current_tokens + tokens <= max_tokens:
                output_set.append(item)
                current_tokens += tokens
            else:
                break

        return output_set
