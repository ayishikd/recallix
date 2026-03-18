cmake_minimum_required(VERSION 3.10)
project(MemoryInfra)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find gRPC/Protobuf if we decide to use them, or just simple HTTP via a library like httplib
# For now, let's start with a simple HTTP implementation for ease of setup, or raw sockets.
# Given the "high performance" requirement, let's plan for gRPC later but start with basic structure.

add_executable(memory_service 
    main.cpp
    event_queue.cpp
    vector_engine.cpp
    memory_indexer.cpp
    clustering_engine.cpp
    graph_engine.cpp
    timeline_engine.cpp
)

# SQLite3
find_package(SQLite3 REQUIRED)
include_directories(${SQLite3_INCLUDE_DIRS})

target_link_libraries(memory_service ${SQLite3_LIBRARIES})


# We might need a vector library like FAISS or a simple one.
# For now, we'll implement a simple one.
