#pragma once

#include <string>
#include <vector>

/**
 * Dataset configuration.
 * Makes it easy to swap between datasets.
 */
struct DatasetConfig {
    std::string name;           // "gist-960-euclidean"
    int dimension;              // 960
    size_t train_size;          // 1,000,000
    size_t test_size;           // 1,000
    std::string metric;         // "euclidean" or "angular"
    int k_neighbors;            // 100 (ground truth neighbors)
    std::string url;            // Download URL
    
    // Common datasets
    static DatasetConfig GIST_960() {
        return {
            "gist-960-euclidean",
            960,
            1000000,
            1000,
            "euclidean",
            100,
            "http://ann-benchmarks.com/gist-960-euclidean.hdf5"
        };
    }
    
    static DatasetConfig NYTIMES_256() {
        return {
            "nytimes-256-angular",
            256,
            290000,
            10000,
            "angular",
            100,
            "http://ann-benchmarks.com/nytimes-256-angular.hdf5"
        };
    }
    
    static DatasetConfig FASHION_MNIST() {
        return {
            "fashion-mnist-784-euclidean",
            784,
            60000,
            10000,
            "euclidean",
            100,
            "http://ann-benchmarks.com/fashion-mnist-784-euclidean.hdf5"
        };
    }
};
