#include "../include/ann_interface.hpp"
#include <cmath>
#include <algorithm>
#include <omp.h>        // OpenMP support

// SIMD intrinsics - architecture specific
#if defined(__x86_64__) || defined(_M_X64) || defined(__i386) || defined(_M_IX86)
    #include <immintrin.h>  // AVX/AVX2 intrinsics for x86_64
#elif defined(__aarch64__) || defined(__arm64__)
    #include <arm_neon.h>    // NEON intrinsics for ARM64
#endif

/**
 * YOUR IMPLEMENTATION HERE!
 * 
 * This is where you implement your optimized ANN algorithm.
 * 
 * Ideas to try:
 * 1. SIMD optimization (AVX2/AVX-512)
 * 2. OpenMP parallelization
 * 3. Cache-friendly memory layout
 * 4. Approximate algorithms:
 *    - HNSW (Hierarchical Navigable Small World)
 *    - IVF (Inverted File Index)
 *    - Product Quantization
 * 
 * Competition metrics:
 * - Recall @ k=10 (must be >= 90%)
 * - Queries per second (QPS)
 * - Latency (p50, p90, p95, p99)
 * - Memory usage
 * - Build time
 */
class StudentAlgorithm : public ANNAlgorithm {
public:
    void init(const std::string& metric, int dimension) override {
        metric_ = metric;
        dimension_ = dimension;
        
        // Your initialization code here
    }

    void fit(const float* data, size_t n_samples) override {
        n_samples_ = n_samples;
        
        // Build your index here
        // Example: copy data, build HNSW graph, etc.
        
        data_.resize(n_samples * dimension_);
        std::copy(data, data + n_samples * dimension_, data_.begin());
    }

    std::vector<int> query(const float* query, int k) override {
        // Your query implementation
        
        // For now, just copy naive implementation
        std::vector<std::pair<float, int>> distances;
        distances.reserve(n_samples_);
        
        for (size_t i = 0; i < n_samples_; ++i) {
            float dist = compute_distance(query, &data_[i * dimension_]);
            distances.emplace_back(dist, static_cast<int>(i));
        }
        
        std::partial_sort(
            distances.begin(),
            distances.begin() + k,
            distances.end()
        );
        
        std::vector<int> result(k);
        for (int i = 0; i < k; ++i) {
            result[i] = distances[i].second;
        }
        
        return result;
    }

    std::vector<std::vector<int>> batch_query(
        const float* queries,
        size_t n_queries,
        int k
    ) override {
        // OPTIMIZATION OPPORTUNITY: Use OpenMP here!
        // #pragma omp parallel for
        
        std::vector<std::vector<int>> results(n_queries);
        
        for (size_t i = 0; i < n_queries; ++i) {
            results[i] = query(queries + i * dimension_, k);
        }
        
        return results;
    }

    size_t get_memory_usage() const override {
        // Report your actual memory usage
        return data_.size() * sizeof(float);
    }

    std::string name() const override {
        return "StudentImplementation";
    }

private:
    float compute_distance(const float* a, const float* b) const {
        // YOUR OPTIMIZED DISTANCE FUNCTION
        // Use SIMD intrinsics here!
        
        if (metric_ == "euclidean") {
            float sum = 0.0f;
            for (int i = 0; i < dimension_; ++i) {
                float diff = a[i] - b[i];
                sum += diff * diff;
            }
            return std::sqrt(sum);
        } else {
            // Angular distance
            float dot = 0.0f, norm_a = 0.0f, norm_b = 0.0f;
            for (int i = 0; i < dimension_; ++i) {
                dot += a[i] * b[i];
                norm_a += a[i] * a[i];
                norm_b += b[i] * b[i];
            }
            return 1.0f - (dot / (std::sqrt(norm_a) * std::sqrt(norm_b)));
        }
    }

    std::vector<float> data_;
    size_t n_samples_ = 0;
};

// Factory function
extern "C" ANNAlgorithm* create_student_algorithm() {
    return new StudentAlgorithm();
}
