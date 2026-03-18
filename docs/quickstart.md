# MemoryOS Quickstart

Integrate long-term AI memory into your application with just a few lines of code.

## Installation

### Python
```bash
pip install memoryos
```

### TypeScript
```bash
npm install memoryos-sdk
```

## Basic Usage

### 1. Initialize the Client
Get your `local_dev_key` from `storage/api_keys.json`.

```python
from memoryos import Memory

memory = Memory(api_key="local_dev_key")
```

### 2. Store a Memory
```python
memory.store("User is interested in recursive algorithms.")
```

### 3. Recall Memories
```python
results = memory.recall("What is the user interested in?")
print(results)
```

### 4. Get Insights
```python
insights = memory.insights()
print(insights)
```
