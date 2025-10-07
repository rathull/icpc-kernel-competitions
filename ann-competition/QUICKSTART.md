# ⚡ Quick Start (30 seconds)

## Prerequisites
- C++ compiler (GCC/Clang/MSVC)
- Python 3.9+
- [uv package manager](https://docs.astral.sh/uv/)
- CMake 3.15+

## Get Running

```bash
make setup    # Install dependencies
make build    # Compile C++
make quick    # Test it works
```

## Your Task

Edit **ONE FILE**: `src/algorithm.cpp`

Implement:
```cpp
void fit(const float* data, size_t n_samples) {
    // Build your index
}

std::vector<int> query(const float* query, int k) {
    // Find k nearest neighbors
}
```

## Workflow

```bash
# Edit src/algorithm.cpp

make build      # Rebuild
make quick      # Test (10s)
make benchmark  # Full eval (5min)
```

## Goal

- **Recall@10 ≥ 90%** (required)
- **Maximize QPS** (primary metric)
- **Minimize latency** (secondary)

## Help

- Full guide: [GETTING_STARTED.md](GETTING_STARTED.md)
- All commands: `make help`
- Reference: `src/naive_algorithm.cpp`

**That's it! Start coding! 🚀**

