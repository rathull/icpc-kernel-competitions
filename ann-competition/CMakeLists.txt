cmake_minimum_required(VERSION 3.15)
project(ann_competition CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(OpenMP REQUIRED)

# Compiler flags
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -ffast-math -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -Wextra")

# Default to Release build
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Source files
set(SOURCES
    src/naive_algorithm.cpp
    src/algorithm.cpp
    src/bindings.cpp
)

# Create Python module
pybind11_add_module(ann_cpp ${SOURCES})

# Include directories
target_include_directories(ann_cpp PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Link libraries
target_link_libraries(ann_cpp PRIVATE
    OpenMP::OpenMP_CXX
)

# Enable SIMD - architecture specific
if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
    # ARM NEON for Apple Silicon / ARM64
    target_compile_options(ann_cpp PRIVATE -mcpu=native)
else()
    # x86_64 AVX2/AVX-512
    target_compile_options(ann_cpp PRIVATE -mavx2 -mfma)
endif()

# Installation
install(TARGETS ann_cpp
    LIBRARY DESTINATION python/ann_competition
)

# Print configuration
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ flags: ${CMAKE_CXX_FLAGS}")
message(STATUS "C++ flags (Release): ${CMAKE_CXX_FLAGS_RELEASE}")
message(STATUS "OpenMP found: ${OpenMP_FOUND}")
