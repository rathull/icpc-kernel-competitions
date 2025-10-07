#include "../include/ann_interface.hpp"
#include <cmath>
#include <algorithm>
#include <queue>

/**
 * STARTER CODE: Naive brute-force implementation.
 * 
 * This is a baseline implementation that:
 * - Stores all vectors in memory
 * - Computes exact distances to all vectors for each query
 * - Returns the k smallest distances
 * 
 * You should:
 * 1. Optimize this with SIMD (see TODOs below)
 * 2. Optimize with OpenMP parallelization
 * 3. Eventually replace with approximate algorithms (HNSW, IVF, etc.)
 */
class NaiveAlgorithm : public ANNAlgorithm {
public:
    void init(const std::string& metric, int dimension) override {
        metric_ = metric;
        dimension_ = dimension;
    }

    void fit(const float* data, size_t n_samples) override {
        n_samples_ = n_samples;
        
        // Copy data into our storage
        // TODO: Consider memory alignment for SIMD (use aligned_alloc)
        data_.resize(n_samples * dimension_);
        std::copy(data, data + n_samples * dimension_, data_.begin());
    }

    std::vector<int> query(const float* query, int k) override {
        // Compute distances to all vectors
        std::vector<std::pair<float, int>> distances;
        distances.reserve(n_samples_);
        
        for (size_t i = 0; i < n_samples_; ++i) {
            float dist = compute_distance(query, &data_[i * dimension_]);
            distances.emplace_back(dist, static_cast<int>(i));
        }
        
        // Partial sort to get k smallest
        std::partial_sort(
            distances.begin(),
            distances.begin() + k,
            distances.end()
        );
        
        // Extract indices
        std::vector<int> result(k);
        for (int i = 0; i < k; ++i) {
            result[i] = distances[i].second;
        }
        
        return result;
    }

    size_t get_memory_usage() const override {
        return data_.size() * sizeof(float);
    }

    std::string name() const override {
        return "NaiveBruteForce";
    }

private:
    /**
     * Compute distance between two vectors.
     * 
     * TODO for VectorDBKernel implementation:
     * 1. Vectorize with SIMD intrinsics (_mm256_*)
     * 2. Use FMA instructions if available
     * 3. Consider loop unrolling
     */
    float compute_distance(const float* a, const float* b) const {
        if (metric_ == "euclidean") {
            return euclidean_distance(a, b);
        } else { // angular (cosine)
            return angular_distance(a, b);
        }
    }
    
    float euclidean_distance(const float* a, const float* b) const {
        float sum = 0.0f;
        
        // TODO: Optimize with AVX2
        // __m256 vec_sum = _mm256_setzero_ps();
        // for (int i = 0; i < dimension_; i += 8) {
        //     __m256 va = _mm256_loadu_ps(&a[i]);
        //     __m256 vb = _mm256_loadu_ps(&b[i]);
        //     __m256 diff = _mm256_sub_ps(va, vb);
        //     vec_sum = _mm256_fmadd_ps(diff, diff, vec_sum);
        // }
        
        for (int i = 0; i < dimension_; ++i) {
            float diff = a[i] - b[i];
            sum += diff * diff;
        }
        
        return std::sqrt(sum);
    }
    
    float angular_distance(const float* a, const float* b) const {
        // Cosine similarity: 1 - (a·b) / (|a||b|)
        float dot = 0.0f;
        float norm_a = 0.0f;
        float norm_b = 0.0f;
        
        // TODO: Optimize with SIMD
        for (int i = 0; i < dimension_; ++i) {
            dot += a[i] * b[i];
            norm_a += a[i] * a[i];
            norm_b += b[i] * b[i];
        }
        
        return 1.0f - (dot / (std::sqrt(norm_a) * std::sqrt(norm_b)));
    }

    std::vector<float> data_;
    size_t n_samples_ = 0;
};

// Factory function for Python bindings
extern "C" ANNAlgorithm* create_naive_algorithm() {
    return new NaiveAlgorithm();
}
