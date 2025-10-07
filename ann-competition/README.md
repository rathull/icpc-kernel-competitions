# ANN Competition Framework

A complete benchmarking framework for Approximate Nearest Neighbor (ANN) algorithm competitions.

## Getting Started

**You only need to edit `src/algorithm.cpp` to implement your algorithm.**

### Quick Start

MacOS instructions:
```bash
# 1. Intstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install system dependencies
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Install required packages
brew install cmake libomp

# 3. Clone and setup
git clone https://github.com/rathull/icpc-kernel-competitions.git
cd ann-competition
make setup
make build
make test
make quick

# 4. Benchmark on real data
make benchmark
```

Modal setup:
```bash
#1. Install Modal CLI
make modal-setup

# 2. Authenticate with Modal
uv run modal login
uv run modal token new

# 3. Download dataset to persistent volume
make modal-download

# 4. Run benchmark on 64 threads!
make modal-benchmark
```
## The Interface

```cpp
class ANNAlgorithm {
public:
    // Initialize algorithm
    virtual void init(const std::string& metric, int dimension) = 0;

    // Build index from training data
    virtual void fit(const float* data, size_t n_samples) = 0;

    // Query for k nearest neighbors
    virtual std::vector<int> query(const float* query, int k) = 0;

    // Batch queries (optional, for better QPS)
    virtual std::vector<std::vector<int>> batch_query(
        const float* queries, size_t n_queries, int k) = 0;

    // Report memory usage
    virtual size_t get_memory_usage() const = 0;

    // Algorithm name
    virtual std::string name() const = 0;
};
```

# Optimization Ideas

- OpenMP pragmas
- SIMD instructions (AVX2)
- Improve memory layout

Algorithms to try:
- HNSW (Hierarchical Navigable Small World)
- IVF (Inverted File Index)
- LSH (Locality Sensitive Hashing)

Advanced:
- Product quantization
- Binary quantize queries or index
- LUT for distance calculation
- Graph pruning


## Credits

Built for ACM ICPC at UCLA's Fall 2025 kernel competitions.

