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
class VectorDBKernel : public ANNAlgorithm {
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
        // OPTIMIZATION: Use OpenMP parallelization for batch queries
        std::vector<std::vector<int>> results(n_queries);

        #pragma omp parallel for
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
        return "VectorDBKernel_SIMD_OpenMP";
    }

private:
    float compute_distance(const float* a, const float* b) const {
        // OPTIMIZED DISTANCE FUNCTION - Use SIMD intrinsics!

        if (metric_ == "euclidean") {
            return compute_euclidean_distance_simd(a, b);
        } else {
            return compute_angular_distance_simd(a, b);
        }
    }

    // SIMD-optimized Euclidean distance
    float compute_euclidean_distance_simd(const float* a, const float* b) const {
        float sum = 0.0f;

        #if defined(__x86_64__) || defined(_M_X64) || defined(__i386) || defined(_M_IX86)
            // AVX2 implementation for x86_64
            int i = 0;
            __m256 sum_vec = _mm256_setzero_ps();

            // Process 8 floats at a time
            for (; i + 7 < dimension_; i += 8) {
                __m256 va = _mm256_loadu_ps(a + i);
                __m256 vb = _mm256_loadu_ps(b + i);
                __m256 diff = _mm256_sub_ps(va, vb);
                sum_vec = _mm256_fmadd_ps(diff, diff, sum_vec);
            }

            // Horizontal sum of the vector
            __m128 sum_high = _mm256_extractf128_ps(sum_vec, 1);
            __m128 sum_low = _mm256_castps256_ps128(sum_vec);
            __m128 total = _mm_add_ps(sum_low, sum_high);

            // Sum remaining 4 floats
            __m128 shuf1 = _mm_shuffle_ps(total, total, _MM_SHUFFLE(2, 3, 0, 1));
            __m128 sum_2 = _mm_add_ps(total, shuf1);
            __m128 shuf2 = _mm_shuffle_ps(sum_2, sum_2, _MM_SHUFFLE(1, 0, 3, 2));
            __m128 sum_1 = _mm_add_ps(sum_2, shuf2);

            sum = _mm_cvtss_f32(sum_1);

            // Handle remaining elements
            for (; i < dimension_; ++i) {
                float diff = a[i] - b[i];
                sum += diff * diff;
            }

        #elif defined(__aarch64__) || defined(__arm64__)
            // NEON implementation for ARM64
            int i = 0;
            float32x4_t sum_vec = vdupq_n_f32(0.0f);

            // Process 4 floats at a time
            for (; i + 3 < dimension_; i += 4) {
                float32x4_t va = vld1q_f32(a + i);
                float32x4_t vb = vld1q_f32(b + i);
                float32x4_t diff = vsubq_f32(va, vb);
                sum_vec = vmlaq_f32(sum_vec, diff, diff);
            }

            // Sum the vector
            sum = vaddvq_f32(sum_vec);

            // Handle remaining elements
            for (; i < dimension_; ++i) {
                float diff = a[i] - b[i];
                sum += diff * diff;
            }

        #else
            // Fallback scalar implementation
            for (int i = 0; i < dimension_; ++i) {
                float diff = a[i] - b[i];
                sum += diff * diff;
            }
        #endif

        return std::sqrt(sum);
    }

    // SIMD-optimized Angular distance
    float compute_angular_distance_simd(const float* a, const float* b) const {
        float dot = 0.0f, norm_a = 0.0f, norm_b = 0.0f;

        #if defined(__x86_64__) || defined(_M_X64) || defined(__i386) || defined(_M_IX86)
            // AVX2 implementation for x86_64
            int i = 0;
            __m256 dot_vec = _mm256_setzero_ps();
            __m256 norm_a_vec = _mm256_setzero_ps();
            __m256 norm_b_vec = _mm256_setzero_ps();

            // Process 8 floats at a time
            for (; i + 7 < dimension_; i += 8) {
                __m256 va = _mm256_loadu_ps(a + i);
                __m256 vb = _mm256_loadu_ps(b + i);
                dot_vec = _mm256_fmadd_ps(va, vb, dot_vec);
                norm_a_vec = _mm256_fmadd_ps(va, va, norm_a_vec);
                norm_b_vec = _mm256_fmadd_ps(vb, vb, norm_b_vec);
            }

            // Horizontal sum for dot product
            __m128 dot_high = _mm256_extractf128_ps(dot_vec, 1);
            __m128 dot_low = _mm256_castps256_ps128(dot_vec);
            __m128 dot_total = _mm_add_ps(dot_low, dot_high);
            __m128 dot_shuf1 = _mm_shuffle_ps(dot_total, dot_total, _MM_SHUFFLE(2, 3, 0, 1));
            __m128 dot_sum_2 = _mm_add_ps(dot_total, dot_shuf1);
            __m128 dot_shuf2 = _mm_shuffle_ps(dot_sum_2, dot_sum_2, _MM_SHUFFLE(1, 0, 3, 2));
            __m128 dot_sum_1 = _mm_add_ps(dot_sum_2, dot_shuf2);
            dot = _mm_cvtss_f32(dot_sum_1);

            // Horizontal sum for norm_a
            __m128 norm_a_high = _mm256_extractf128_ps(norm_a_vec, 1);
            __m128 norm_a_low = _mm256_castps256_ps128(norm_a_vec);
            __m128 norm_a_total = _mm_add_ps(norm_a_low, norm_a_high);
            __m128 norm_a_shuf1 = _mm_shuffle_ps(norm_a_total, norm_a_total, _MM_SHUFFLE(2, 3, 0, 1));
            __m128 norm_a_sum_2 = _mm_add_ps(norm_a_total, norm_a_shuf1);
            __m128 norm_a_shuf2 = _mm_shuffle_ps(norm_a_sum_2, norm_a_sum_2, _MM_SHUFFLE(1, 0, 3, 2));
            __m128 norm_a_sum_1 = _mm_add_ps(norm_a_sum_2, norm_a_shuf2);
            norm_a = _mm_cvtss_f32(norm_a_sum_1);

            // Horizontal sum for norm_b
            __m128 norm_b_high = _mm256_extractf128_ps(norm_b_vec, 1);
            __m128 norm_b_low = _mm256_castps256_ps128(norm_b_vec);
            __m128 norm_b_total = _mm_add_ps(norm_b_low, norm_b_high);
            __m128 norm_b_shuf1 = _mm_shuffle_ps(norm_b_total, norm_b_total, _MM_SHUFFLE(2, 3, 0, 1));
            __m128 norm_b_sum_2 = _mm_add_ps(norm_b_total, norm_b_shuf1);
            __m128 norm_b_shuf2 = _mm_shuffle_ps(norm_b_sum_2, norm_b_sum_2, _MM_SHUFFLE(1, 0, 3, 2));
            __m128 norm_b_sum_1 = _mm_add_ps(norm_b_sum_2, norm_b_shuf2);
            norm_b = _mm_cvtss_f32(norm_b_sum_1);

            // Handle remaining elements
            for (; i < dimension_; ++i) {
                dot += a[i] * b[i];
                norm_a += a[i] * a[i];
                norm_b += b[i] * b[i];
            }

        #elif defined(__aarch64__) || defined(__arm64__)
            // NEON implementation for ARM64
            int i = 0;
            float32x4_t dot_vec = vdupq_n_f32(0.0f);
            float32x4_t norm_a_vec = vdupq_n_f32(0.0f);
            float32x4_t norm_b_vec = vdupq_n_f32(0.0f);

            // Process 4 floats at a time
            for (; i + 3 < dimension_; i += 4) {
                float32x4_t va = vld1q_f32(a + i);
                float32x4_t vb = vld1q_f32(b + i);
                dot_vec = vmlaq_f32(dot_vec, va, vb);
                norm_a_vec = vmlaq_f32(norm_a_vec, va, va);
                norm_b_vec = vmlaq_f32(norm_b_vec, vb, vb);
            }

            // Sum vectors
            dot = vaddvq_f32(dot_vec);
            norm_a = vaddvq_f32(norm_a_vec);
            norm_b = vaddvq_f32(norm_b_vec);

            // Handle remaining elements
            for (; i < dimension_; ++i) {
                dot += a[i] * b[i];
                norm_a += a[i] * a[i];
                norm_b += b[i] * b[i];
            }

        #else
            // Fallback scalar implementation
            for (int i = 0; i < dimension_; ++i) {
                dot += a[i] * b[i];
                norm_a += a[i] * a[i];
                norm_b += b[i] * b[i];
            }
        #endif

        return 1.0f - (dot / (std::sqrt(norm_a) * std::sqrt(norm_b)));
    }

    std::vector<float> data_;
    size_t n_samples_ = 0;
};

// Factory function
extern "C" ANNAlgorithm* create_vectordb_kernel() {
    return new VectorDBKernel();
}
