# ANN Competition Framework

A complete benchmarking framework for Approximate Nearest Neighbor (ANN) algorithm competitions.

## 🎯 For Competitors

**You only need to edit ONE file: `src/algorithm.cpp`**

Everything else is handled by the framework!

### Quick Start

```bash
# 1. Install dependencies
make setup

# 2. Build your code
make build

# 3. Test it works
make quick

# 4. Benchmark on real data
make benchmark
```

**👉 New here? Read [QUICKSTART.md](QUICKSTART.md) (30 seconds) or [GETTING_STARTED.md](GETTING_STARTED.md) (complete guide)**

## 📋 What You Get

- ✅ **Simple Interface**: Implement 4 methods, that's it!
- ✅ **Fast Iteration**: Quick tests on synthetic data (< 10 seconds)
- ✅ **Comprehensive Metrics**: Recall, QPS, latency, memory usage
- ✅ **Real Datasets**: GIST-960 automatically downloaded
- ✅ **Reference Implementation**: Study the naive brute-force baseline
- ✅ **Modern Tools**: Uses `uv` for dependency management
- ✅ **Cross-Platform**: Works on x86_64 and ARM64 (Apple Silicon)

## 🏆 Competition Metrics

| Metric | Target | Priority |
|--------|--------|----------|
| **Recall@10** | ≥ 90% | ✅ Required |
| **QPS** | Maximize | 🥇 Primary |
| **Latency (p95)** | Minimize | 🥈 Secondary |
| **Memory** | Minimize | 🥉 Tertiary |
| **Build Time** | Minimize | Bonus |

## 🛠 Available Commands

```bash
make setup      # Install dependencies with uv
make build      # Build C++ extensions
make clean      # Clean build artifacts
make quick      # Quick test on synthetic data (~10s)
make test       # Run full test suite
make benchmark  # Full benchmark on GIST dataset (~5min)
make compare    # Compare your impl vs naive baseline
make help       # Show all commands
```

## 📁 Repository Structure

```
ann-competition/
├── src/
│   ├── algorithm.cpp          ← YOU EDIT THIS FILE
│   ├── naive_algorithm.cpp    (reference implementation)
│   └── bindings.cpp           (Python bindings - don't touch)
│
├── include/
│   ├── ann_interface.hpp      (interface definition)
│   └── dataset.hpp            (dataset configs)
│
├── scripts/
│   ├── quick_test.py          (fast testing)
│   └── benchmark.py           (full evaluation)
│
├── python/                    (benchmarking framework)
├── results/                   (benchmark outputs)
├── GETTING_STARTED.md         (detailed guide)
└── Makefile                   (convenient commands)
```

## 💻 The Interface

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

## 🚀 Optimization Ideas

### Beginner
- ✅ OpenMP parallelization (`#pragma omp parallel for`)
- ✅ SIMD instructions (AVX2/NEON)
- ✅ Better memory layout

### Intermediate
- 🎯 HNSW (Hierarchical Navigable Small World)
- 🎯 IVF (Inverted File Index)
- 🎯 LSH (Locality Sensitive Hashing)

### Advanced
- 🔥 Product Quantization
- 🔥 Graph pruning strategies
- 🔥 Hybrid algorithms

## 📊 Example Results

```
SUMMARY
============================================================
Algorithm:     StudentImplementation
Dataset:       gist-960-euclidean
Build time:    12.34s
Memory:        2048.0 MB
Recall@10:     0.9523
QPS:           8234.5
Latency (p50): 1.23ms
Latency (p95): 4.56ms
Latency (p99): 7.89ms
```

## 🔧 Requirements

- **C++ Compiler**: GCC 7+, Clang 8+, or MSVC 2019+
- **Python**: 3.9 or higher
- **CMake**: 3.15 or higher
- **uv**: Python package manager ([install](https://docs.astral.sh/uv/))
- **OpenMP**: Usually included with compiler

### macOS

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Compiler and CMake (via Homebrew)
brew install cmake libomp
```

### Linux

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ubuntu/Debian
sudo apt-get install build-essential cmake libomp-dev

# Fedora/RHEL
sudo dnf install gcc-c++ cmake libomp-devel
```

### Windows

```bash
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install Visual Studio 2019+ with C++ support
# Install CMake from https://cmake.org/download/
```

## 📚 Resources

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete setup and development guide
- **[include/ann_interface.hpp](include/ann_interface.hpp)** - Interface documentation
- **[src/naive_algorithm.cpp](src/naive_algorithm.cpp)** - Reference implementation
- **[HNSW Paper](https://arxiv.org/abs/1603.09320)** - State-of-the-art ANN algorithm
- **[FAISS](https://github.com/facebookresearch/faiss)** - Facebook's ANN library (for reference)

## 🐛 Troubleshooting

### Build fails with "uv not found"
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart your terminal
```

### Module 'ann_cpp' not found
```bash
make clean
make build
```

### OpenMP not found
```bash
# macOS
brew install libomp

# Linux
sudo apt-get install libomp-dev  # Ubuntu/Debian
sudo dnf install libomp-devel     # Fedora/RHEL
```

### Slow first benchmark run
The first run downloads ~3.6GB of data. Subsequent runs use cached data.

## 🏅 Submission

When ready to submit:
1. Make sure `make test` passes
2. Run `make benchmark` to generate results
3. Submit:
   - Your modified `src/algorithm.cpp`
   - Any additional files you created
   - Brief writeup explaining your approach
   - The results JSON from `results/` directory

## 📖 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Start here! Complete guide for competitors
- **Makefile** - Run `make help` to see all available commands
- **Code Comments** - `src/algorithm.cpp` has extensive inline documentation

## 🤝 Contributing

For instructors setting up competitions:
1. Fork this repository
2. Customize datasets in `python/dataset_loader.py`
3. Adjust metrics/scoring in `python/metrics.py`
4. Update competition rules in `GETTING_STARTED.md`

## 📜 License

This project is provided as-is for educational purposes.

## 🎓 Credits

Built for ICPC-style programming competitions focusing on algorithmic optimization and systems programming.

---

**Ready to compete? Read [GETTING_STARTED.md](GETTING_STARTED.md) and start coding! 🚀**
