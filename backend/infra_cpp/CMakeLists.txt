cmake_minimum_required(VERSION 3.10)
project(MemoryInfra)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find SQLite3
find_package(SQLite3 REQUIRED)
include_directories(${SQLite3_INCLUDE_DIRS})

add_executable(memory_service 
    main.cpp
    event_queue.cpp
    vector_engine.cpp
    memory_indexer.cpp
    clustering_engine.cpp
    graph_engine.cpp
    timeline_engine.cpp
)
target_link_libraries(memory_service ${SQLite3_LIBRARIES})

# ADD BENCHMARK TOOL
add_executable(benchmark_hnsw
    benchmark_hnsw.cpp
    vector_engine.cpp
)
target_link_libraries(benchmark_hnsw ${SQLite3_LIBRARIES})
