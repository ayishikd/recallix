cmake_minimum_required(VERSION 3.10)
project(MemoryInfra)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ============================================================================
# Cross-Platform SIMD Detection
# Automatically selects the best SIMD backend for the target architecture.
# ARM: NEON (default on Apple Silicon / ARM64)
# x86: AVX2 if supported, else SSE (fallback)
# Other: Scalar (universal fallback)
# ============================================================================
include(CheckCXXCompilerFlag)

if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm|aarch64|ARM64")
    message(STATUS "Detected ARM architecture — using NEON SIMD")
    # NEON is enabled by default on ARM64, no extra flags needed
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64|i686")
    check_cxx_compiler_flag("-mavx2" HAS_AVX2)
    check_cxx_compiler_flag("-msse" HAS_SSE)
    if(HAS_AVX2)
        message(STATUS "Detected x86 architecture — using AVX2 SIMD")
        add_compile_options(-mavx2 -mfma)
    elseif(HAS_SSE)
        message(STATUS "Detected x86 architecture — using SSE SIMD (AVX2 not available)")
        add_compile_options(-msse -msse3)
    else()
        message(STATUS "Detected x86 architecture — no SIMD support, using scalar fallback")
    endif()
else()
    message(STATUS "Unknown architecture (${CMAKE_SYSTEM_PROCESSOR}) — using scalar fallback")
endif()

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
