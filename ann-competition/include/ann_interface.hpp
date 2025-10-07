#pragma once

#include <vector>
#include <string>
#include <cstddef>

/**
 * Core interface for ANN algorithms.
 * VectorDBKernel implements this interface in algorithm.cpp
 */
class ANNAlgorithm {
public:
    virtual ~ANNAlgorithm() = default;

    /**
     * Initialize the algorithm with dataset parameters.
     * Called once before fit().
     * 
     * @param metric "euclidean" or "angular" (cosine)
     * @param dimension Dimensionality of vectors
     */
    virtual void init(const std::string& metric, int dimension) = 0;

    /**
     * Build the index from training data.
     * This is where you construct your data structures.
     * 
     * @param data Pointer to flattened array: [n_samples * dimension] floats
     * @param n_samples Number of vectors in training set
     */
    virtual void fit(const float* data, size_t n_samples) = 0;

    /**
     * Query for k nearest neighbors of a single vector.
     * 
     * @param query Pointer to query vector [dimension floats]
     * @param k Number of neighbors to return
     * @return Vector of indices into training data (0 to n_samples-1)
     */
    virtual std::vector<int> query(const float* query, int k) = 0;

    /**
     * OPTIONAL: Batch query for better throughput.
     * Override this for OpenMP parallelization.
     * 
     * @param queries Pointer to flattened queries: [n_queries * dimension]
     * @param n_queries Number of query vectors
     * @param k Number of neighbors per query
     * @return Vector of vectors: outer[i] = neighbors for query i
     */
    virtual std::vector<std::vector<int>> batch_query(
        const float* queries, 
        size_t n_queries, 
        int k
    ) {
        // Default: call query() for each
        std::vector<std::vector<int>> results;
        results.reserve(n_queries);
        for (size_t i = 0; i < n_queries; ++i) {
            results.push_back(query(queries + i * dimension_, k));
        }
        return results;
    }

    /**
     * Get approximate memory usage in bytes.
     * Used for competition metrics.
     */
    virtual size_t get_memory_usage() const = 0;

    /**
     * Get algorithm name for leaderboard.
     */
    virtual std::string name() const = 0;

protected:
    int dimension_ = 0;
    std::string metric_;
};