# Getting Started with ANN Competition

Welcome to the ANN (Approximate Nearest Neighbor) Competition! This guide will help you get started quickly.

## 🎯 Your Mission

Implement the fastest ANN algorithm possible while maintaining **≥90% recall@10**.

You only need to edit **ONE FILE**: `src/algorithm.cpp`

Everything else is taken care of!

## 🚀 Quick Start (5 minutes)

### Prerequisites

- C++ compiler with C++17 support (GCC, Clang, or MSVC)
- Python 3.9 or higher
- `uv` package manager ([install here](https://docs.astral.sh/uv/))
- CMake 3.15+
- OpenMP support (usually comes with your compiler)

### Installation

```bash
# Clone the repository (if you haven't already)
cd ann-competition

# Install dependencies (creates virtual environment automatically)
make setup

# Build the C++ code
make build

# Test your implementation
make quick
```

That's it! You're ready to compete.

## 📝 Development Workflow

### 1. Edit Your Algorithm

Open `src/algorithm.cpp` and implement your optimized ANN algorithm:

```cpp
class StudentAlgorithm : public ANNAlgorithm {
    void fit(const float* data, size_t n_samples) override {
        // Build your index here
        // Ideas: HNSW, IVF, Product Quantization, etc.
    }

    std::vector<int> query(const float* query, int k) override {
        // Query for k nearest neighbors
        // Use SIMD, OpenMP, smart data structures!
    }
};
```

### 2. Test Quickly

```bash
make quick
```

This runs a quick test on synthetic data (< 10 seconds). Perfect for rapid iteration!

### 3. Build and Iterate

Every time you modify `algorithm.cpp`:

```bash
make build    # Rebuild the C++ code
make quick    # Test it works
```

### 4. Full Benchmark

When you're ready to measure performance on real data:

```bash
make benchmark
```

This will:
- Download the GIST-960 dataset (~3.6GB, one-time only)
- Build your index
- Measure recall, QPS, latency, memory usage
- Save results to `results/` folder

### 5. Compare Against Baseline

```bash
make compare
```

This runs your implementation alongside the naive brute-force baseline.

## 🎓 Understanding the Interface

Your algorithm must implement these methods:

```cpp
class ANNAlgorithm {
    // Initialize with distance metric and dimension
    virtual void init(const std::string& metric, int dimension) = 0;

    // Build index from training data
    // data: flattened array of n_samples * dimension floats
    virtual void fit(const float* data, size_t n_samples) = 0;

    // Query for k nearest neighbors
    // Returns indices into the training data
    virtual std::vector<int> query(const float* query, int k) = 0;

    // OPTIONAL: Batch queries for better throughput
    virtual std::vector<std::vector<int>> batch_query(
        const float* queries, 
        size_t n_queries, 
        int k
    ) = 0;

    // Report memory usage in bytes
    virtual size_t get_memory_usage() const = 0;

    // Your algorithm name
    virtual std::string name() const = 0;
};
```

## 🏆 Competition Metrics

Your algorithm is scored on:

1. **Recall@10** (must be ≥ 90%)
   - Percentage of true nearest neighbors found
   - Lower recall = disqualified ❌

2. **Queries Per Second (QPS)** - PRIMARY METRIC
   - Higher is better!
   - Measured using `batch_query()`

3. **Latency Percentiles**
   - p50, p90, p95, p99 in milliseconds
   - Lower is better
   - Measured using single `query()` calls

4. **Memory Usage**
   - Total bytes used by your index
   - Lower is better

5. **Build Time**
   - Time to build the index
   - Lower is better

## 💡 Optimization Ideas

### Level 1: Basic Optimizations
- Use SIMD intrinsics (AVX2/AVX-512 on x86, NEON on ARM)
- OpenMP parallelization for batch queries
- Cache-friendly memory layout

### Level 2: Approximate Algorithms
- **HNSW** (Hierarchical Navigable Small World) - Best all-around
- **IVF** (Inverted File Index) - Good for clustering
- **LSH** (Locality Sensitive Hashing) - Simple to implement
- **Product Quantization** - Extreme memory efficiency

### Level 3: Advanced Techniques
- Graph-based search with pruning
- Hybrid approaches (e.g., IVF + PQ)
- Architecture-specific optimizations
- Prefetching and memory alignment

**👉 See [EXAMPLES.md](EXAMPLES.md) for concrete code examples!**

## 🛠 Available Tools

```bash
make help           # Show all commands
make build          # Build C++ code
make build-debug    # Build with debug symbols
make clean          # Clean build artifacts
make quick          # Quick test (synthetic data)
make test           # Full test suite
make benchmark      # Full benchmark (real data)
make compare        # Compare vs baseline
```

## 📊 Understanding Results

After running `make benchmark`, you'll see output like:

```
SUMMARY
============================================================
Algorithm:     StudentImplementation
Dataset:       gist-960-euclidean
Build time:    5.23s
Memory:        1234.5 MB
Recall@10:     0.9234
QPS:           12345.6
Latency (p50): 0.81ms
Latency (p95): 2.45ms
Latency (p99): 4.12ms
```

Key points:
- **Recall ≥ 0.90** = You're in the running! ✅
- **Higher QPS** = Better ranking
- **Lower latency** = Bonus points
- **Lower memory** = Bonus points

Results are saved as JSON in `results/benchmark_TIMESTAMP.json`

## 🐛 Debugging Tips

### Check Build Errors
```bash
make build
# Look for compilation errors
```

### Run with Debug Symbols
```bash
make build-debug
gdb python
(gdb) run scripts/quick_test.py --impl student
```

### Verify SIMD is Used

On x86_64:
```bash
objdump -d build/ann_cpp*.so | grep ymm   # AVX2
objdump -d build/ann_cpp*.so | grep zmm   # AVX-512
```

On ARM64:
```bash
objdump -d build/ann_cpp*.so | grep "ld1\|st1"  # NEON
```

### Check Memory Leaks
```bash
valgrind --leak-check=full python scripts/quick_test.py --impl student
```

## 📚 Resources

### Algorithms
- [HNSW Paper](https://arxiv.org/abs/1603.09320) - State-of-the-art graph-based ANN
- [FAISS Library](https://github.com/facebookresearch/faiss) - Facebook's ANN library (for ideas)
- [Annoy](https://github.com/spotify/annoy) - Spotify's ANN library (simpler)

### Optimization
- [Intel Intrinsics Guide](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/) - SIMD reference
- [ARM NEON Guide](https://developer.arm.com/architectures/instruction-sets/simd-isas/neon) - ARM SIMD
- [OpenMP Tutorial](https://www.openmp.org/resources/tutorials-articles/) - Parallel programming

### Datasets
- **GIST-960**: 960-dimensional GIST descriptors, Euclidean distance
- **SIFT-128**: 128-dimensional SIFT features (coming soon)
- **GloVe**: Word embeddings, Angular/Cosine distance (coming soon)

## ❓ FAQ

**Q: Can I use external libraries?**
A: Check with your instructor. Pure C++ teaches fundamentals, but libraries like Eigen can help with SIMD.

**Q: What if I can't achieve 90% recall?**
A: Start with the naive brute-force approach and gradually add optimizations. Focus on correctness first!

**Q: Should I optimize for QPS or latency?**
A: QPS is the primary metric. However, `batch_query()` uses `query()` internally, so optimizing both helps.

**Q: How do I submit?**
A: Submit your modified `src/algorithm.cpp` and a brief writeup explaining your approach.

**Q: Can I modify other files?**
A: You can add new files, but the benchmarking system only guarantees `algorithm.cpp` will be used. Don't modify the interface!

**Q: Help! My build is failing!**
A: Check that you have:
  - A C++17 compatible compiler
  - CMake 3.15+
  - OpenMP support
  - Run `make clean` and try again

**Q: The benchmark is slow!**
A: First time downloads the dataset (~3.6GB). Subsequent runs are much faster.

## 🎯 Next Steps

1. ✅ Complete the quick start above
2. 📖 Read through `src/algorithm.cpp` - understand the template
3. 🧪 Run `make test` to see both naive and student implementations
4. 💻 Start coding! Try a simple optimization first (e.g., OpenMP)
5. 🚀 Iterate with `make build && make quick`
6. 📊 Benchmark with `make benchmark`
7. 🏆 Optimize and compete!

## 💬 Support

Need help?
1. Check this guide and the comments in `src/algorithm.cpp`
2. Review the naive implementation in `src/naive_algorithm.cpp`
3. Post on the course forum
4. Attend office hours

Good luck! 🚀

