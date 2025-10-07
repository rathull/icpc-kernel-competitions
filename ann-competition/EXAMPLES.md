# 💡 Optimization Examples

This guide shows concrete examples of how to optimize your ANN algorithm.

## Example 1: OpenMP Parallelization (Easy)

**Goal**: Speed up batch queries with parallel processing

**Before** (in `src/algorithm.cpp`):
```cpp
std::vector<std::vector<int>> batch_query(
    const float* queries,
    size_t n_queries,
    int k
) override {
    std::vector<std::vector<int>> results(n_queries);
    
    for (size_t i = 0; i < n_queries; ++i) {
        results[i] = query(queries + i * dimension_, k);
    }
    
    return results;
}
```

**After**:
```cpp
std::vector<std::vector<int>> batch_query(
    const float* queries,
    size_t n_queries,
    int k
) override {
    std::vector<std::vector<int>> results(n_queries);
    
    #pragma omp parallel for
    for (size_t i = 0; i < n_queries; ++i) {
        results[i] = query(queries + i * dimension_, k);
    }
    
    return results;
}
```

**Expected Improvement**: 4-8x speedup on multi-core CPUs

**Test it**:
```bash
make build && make quick
```

---

## Example 2: SIMD Distance Computation (Medium)

**Goal**: Use vector instructions to compute distances faster

**For x86_64 (AVX2)**:
```cpp
#if defined(__x86_64__) || defined(_M_X64)
float compute_distance_simd_avx2(const float* a, const float* b, int dim) {
    __m256 sum = _mm256_setzero_ps();
    
    int i = 0;
    // Process 8 floats at a time
    for (; i + 7 < dim; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        __m256 diff = _mm256_sub_ps(va, vb);
        sum = _mm256_fmadd_ps(diff, diff, sum);  // sum += diff * diff
    }
    
    // Horizontal sum
    float result[8];
    _mm256_storeu_ps(result, sum);
    float total = 0.0f;
    for (int j = 0; j < 8; ++j) {
        total += result[j];
    }
    
    // Handle remaining elements
    for (; i < dim; ++i) {
        float diff = a[i] - b[i];
        total += diff * diff;
    }
    
    return std::sqrt(total);
}
#endif
```

**For ARM64 (NEON)**:
```cpp
#elif defined(__aarch64__) || defined(__arm64__)
float compute_distance_simd_neon(const float* a, const float* b, int dim) {
    float32x4_t sum = vdupq_n_f32(0.0f);
    
    int i = 0;
    // Process 4 floats at a time
    for (; i + 3 < dim; i += 4) {
        float32x4_t va = vld1q_f32(a + i);
        float32x4_t vb = vld1q_f32(b + i);
        float32x4_t diff = vsubq_f32(va, vb);
        sum = vmlaq_f32(sum, diff, diff);  // sum += diff * diff
    }
    
    // Horizontal sum
    float total = vaddvq_f32(sum);
    
    // Handle remaining elements
    for (; i < dim; ++i) {
        float diff = a[i] - b[i];
        total += diff * diff;
    }
    
    return std::sqrt(total);
}
#endif
```

**Use it in your code**:
```cpp
float compute_distance(const float* a, const float* b) const {
    if (metric_ == "euclidean") {
        #if defined(__x86_64__) || defined(_M_X64)
            return compute_distance_simd_avx2(a, b, dimension_);
        #elif defined(__aarch64__) || defined(__arm64__)
            return compute_distance_simd_neon(a, b, dimension_);
        #else
            // Fallback to scalar code
            float sum = 0.0f;
            for (int i = 0; i < dimension_; ++i) {
                float diff = a[i] - b[i];
                sum += diff * diff;
            }
            return std::sqrt(sum);
        #endif
    }
    // ... handle other metrics
}
```

**Expected Improvement**: 2-4x faster distance computation

---

## Example 3: Simple Inverted File Index (Advanced)

**Goal**: Reduce search space using clustering

```cpp
class StudentAlgorithm : public ANNAlgorithm {
private:
    std::vector<float> data_;
    std::vector<float> centroids_;
    std::vector<std::vector<int>> clusters_;  // cluster_id -> point indices
    int num_clusters_ = 100;
    
public:
    void fit(const float* data, size_t n_samples) override {
        n_samples_ = n_samples;
        data_.resize(n_samples * dimension_);
        std::copy(data, data + n_samples * dimension_, data_.begin());
        
        // 1. Build clusters using k-means
        build_clusters();
    }
    
    void build_clusters() {
        // Simple k-means clustering
        centroids_.resize(num_clusters_ * dimension_);
        clusters_.resize(num_clusters_);
        
        // Initialize centroids randomly
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, n_samples_ - 1);
        
        for (int i = 0; i < num_clusters_; ++i) {
            int rand_idx = dis(gen);
            std::copy(
                data_.begin() + rand_idx * dimension_,
                data_.begin() + (rand_idx + 1) * dimension_,
                centroids_.begin() + i * dimension_
            );
        }
        
        // Run k-means iterations (simplified)
        for (int iter = 0; iter < 10; ++iter) {
            // Clear clusters
            for (auto& cluster : clusters_) {
                cluster.clear();
            }
            
            // Assign points to nearest centroid
            for (size_t i = 0; i < n_samples_; ++i) {
                float min_dist = std::numeric_limits<float>::max();
                int best_cluster = 0;
                
                for (int c = 0; c < num_clusters_; ++c) {
                    float dist = compute_distance(
                        &data_[i * dimension_],
                        &centroids_[c * dimension_]
                    );
                    if (dist < min_dist) {
                        min_dist = dist;
                        best_cluster = c;
                    }
                }
                clusters_[best_cluster].push_back(i);
            }
        }
    }
    
    std::vector<int> query(const float* query, int k) override {
        // 1. Find closest centroids
        std::vector<std::pair<float, int>> centroid_distances;
        for (int c = 0; c < num_clusters_; ++c) {
            float dist = compute_distance(query, &centroids_[c * dimension_]);
            centroid_distances.emplace_back(dist, c);
        }
        std::sort(centroid_distances.begin(), centroid_distances.end());
        
        // 2. Search only top-N closest clusters
        int n_probe = 5;  // Search 5 clusters
        std::vector<std::pair<float, int>> candidates;
        
        for (int i = 0; i < std::min(n_probe, num_clusters_); ++i) {
            int cluster_id = centroid_distances[i].second;
            
            // Search all points in this cluster
            for (int point_id : clusters_[cluster_id]) {
                float dist = compute_distance(
                    query,
                    &data_[point_id * dimension_]
                );
                candidates.emplace_back(dist, point_id);
            }
        }
        
        // 3. Return top-k
        std::partial_sort(
            candidates.begin(),
            candidates.begin() + std::min(k, (int)candidates.size()),
            candidates.end()
        );
        
        std::vector<int> result;
        for (int i = 0; i < std::min(k, (int)candidates.size()); ++i) {
            result.push_back(candidates[i].second);
        }
        return result;
    }
};
```

**Expected Improvement**: 10-100x faster with 90%+ recall

**Tuning**:
- Increase `num_clusters_` for more accuracy, less speed
- Increase `n_probe` for better recall, less speed

---

## Testing Your Optimizations

### 1. Quick Correctness Check
```bash
make build && make quick
```
✅ Passes validation  
✅ Returns correct number of results  
✅ Indices in valid range  

### 2. Measure Performance
```bash
make benchmark
```
📊 Get full metrics:
- Recall@10
- QPS (throughput)
- Latency (p50, p95, p99)
- Memory usage

### 3. Compare Against Baseline
```bash
make compare
```
📈 See side-by-side comparison

---

## Common Pitfalls

### ❌ Wrong: Out-of-bounds access
```cpp
// BAD: No bounds check
__m256 va = _mm256_loadu_ps(a + i);  // Might read past end!
```

### ✅ Right: Handle remainder
```cpp
// GOOD: Process bulk + remainder
int i = 0;
for (; i + 7 < dimension_; i += 8) {
    __m256 va = _mm256_loadu_ps(a + i);
    // ... process
}
// Handle remaining elements
for (; i < dimension_; ++i) {
    // scalar code
}
```

### ❌ Wrong: Race condition in parallel code
```cpp
std::vector<int> all_results;
#pragma omp parallel for
for (size_t i = 0; i < n_queries; ++i) {
    auto result = query(...);
    all_results.insert(all_results.end(), result.begin(), result.end());  // RACE!
}
```

### ✅ Right: Pre-allocate per-thread storage
```cpp
std::vector<std::vector<int>> results(n_queries);
#pragma omp parallel for
for (size_t i = 0; i < n_queries; ++i) {
    results[i] = query(...);  // Each thread writes to different index
}
```

---

## Next Steps

1. Start with OpenMP (easiest win)
2. Add SIMD for distance computation
3. Implement approximate algorithm (IVF, HNSW, etc.)
4. Fine-tune parameters
5. Profile and optimize bottlenecks

## Resources

- **Intel Intrinsics Guide**: https://www.intel.com/content/www/us/en/docs/intrinsics-guide/
- **ARM NEON Guide**: https://developer.arm.com/architectures/instruction-sets/simd-isas/neon
- **OpenMP Tutorial**: https://www.openmp.org/resources/tutorials-articles/
- **HNSW Paper**: https://arxiv.org/abs/1603.09320
- **FAISS (for reference)**: https://github.com/facebookresearch/faiss

Good luck! 🚀

