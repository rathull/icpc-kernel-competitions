# Setup Verification Guide

This guide helps you verify that your ANN competition setup works correctly.

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.9+** installed (`python --version`)
- [ ] **uv** installed ([install guide](https://docs.astral.sh/uv/))
- [ ] **C++ compiler** (GCC/Clang/MSVC)
- [ ] **CMake 3.15+** installed (`cmake --version`)
- [ ] **Git** installed (for cloning the repo)

## 🚀 Fresh Installation Test

### Step 1: Clone the Repository

```bash
git clone <repository-url> ann-competition
cd ann-competition
```

### Step 2: Initial Setup

```bash
make setup
```

**Expected output:**
```
Installing dependencies with uv...
✓ Setup complete
```

**What it does:**
- Installs `uv` if not present
- Creates Python virtual environment (`.venv/`)
- Installs all dependencies from `pyproject.toml`

### Step 3: Build C++ Code

```bash
make build
```

**Expected output:**
```
Building C++ extensions...
-- Found pybind11: ...
-- OpenMP found: TRUE
-- Configuring done
-- Generating done
[100%] Built target ann_cpp
✓ Build complete
```

**What it does:**
- Configures CMake
- Compiles C++ code with optimizations
- Creates `ann_cpp` Python module in `build/`

### Step 4: Quick Test

```bash
make quick
```

**Expected output:**
```
🖥️  SYSTEM SPECIFICATIONS
============================================================
Platform:         <your-platform>
Architecture:     <your-arch>
CPU Cores:       <your-cores>
Memory:          <your-memory>
Environment:     Local Machine
============================================================

Testing student implementation with euclidean metric
...
✓ Test complete!
```

**What it does:**
- Runs on synthetic data (1000 vectors)
- Tests correctness
- Takes ~10 seconds

### Step 5: Full Benchmark (Optional)

```bash
make benchmark
```

**Expected output:**
```
Loading gist-960-euclidean...
Downloading gist-960-euclidean...  (first time only)
✓ Downloaded to data/gist-960-euclidean.hdf5

Running benchmark on gist-960-euclidean
[1/4] Building index...
[2/4] Warming up...
[3/4] Measuring throughput...
[4/4] Measuring latency...

SUMMARY
============================================================
Recall@10:     0.9993
QPS:           <your-qps>
✓ Results saved to results/benchmark_<timestamp>.json
```

**What it does:**
- Downloads GIST dataset (~3.6GB, one-time)
- Runs full benchmark
- Takes 5-15 minutes

## 🔍 Troubleshooting

### Issue: "uv not found"

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart terminal
source ~/.bashrc  # or ~/.zshrc
```

### Issue: "CMake not found"

```bash
# macOS
brew install cmake

# Ubuntu/Debian
sudo apt-get install cmake

# Fedora/RHEL
sudo dnf install cmake
```

### Issue: "OpenMP not found"

```bash
# macOS
brew install libomp

# Ubuntu/Debian
sudo apt-get install libomp-dev

# Fedora/RHEL
sudo dnf install libomp-devel
```

### Issue: "Build fails with SIMD errors"

This is normal on ARM64 (Apple Silicon) or older CPUs. The code automatically falls back to scalar implementations.

### Issue: "Module 'ann_cpp' not found"

```bash
make clean
make build
```

### Issue: "Dataset download is slow"

First download takes 5-10 minutes for GIST dataset (~3.6GB). Subsequent runs use cached data.

## 🌩️ Modal Setup (Cloud Benchmarking)

### Step 1: Install Modal

```bash
pip install modal
# Or use the Makefile
make modal-setup
```

### Step 2: Authenticate

```bash
modal token new
```

Follow prompts to:
1. Create Modal account (free tier available)
2. Get API token
3. Authenticate locally

### Step 3: Download Dataset (One-time)

```bash
make modal-download
```

**Expected output:**
```
📥 Downloading gist-960-euclidean to persistent volume...
Downloading from http://ann-benchmarks.com/...
✓ Downloaded successfully
💾 Committing to persistent volume...
✅ Dataset download complete!
```

**Cost:** ~$0.50 (one-time)
**Time:** 5-10 minutes

### Step 4: Run Modal Benchmark

```bash
make modal-benchmark
```

**Expected output:**
```
🚀 Running ANN benchmark on Modal
   Implementation: student
   Dataset: gist-960-euclidean
   CPU cores: 32
   Memory: 32GB

🖥️  SYSTEM SPECIFICATIONS
Platform:         Linux-...
Architecture:     x86_64 (64bit)
CPU Cores:       32
Memory:          32.0 GB
Environment:     Modal Cloud Platform

Running benchmark on gist-960-euclidean
...
✅ Benchmark completed successfully!
```

**Cost:** ~$2-5 per run
**Time:** 2-8 minutes

## 📋 Verification Checklist

### Local Setup
- [ ] `make setup` completes without errors
- [ ] `make build` compiles successfully
- [ ] `make quick` passes all tests
- [ ] `make benchmark` runs full evaluation
- [ ] Results saved to `results/` directory
- [ ] System specs logged correctly

### Modal Setup (Optional)
- [ ] Modal CLI installed
- [ ] Modal authentication successful
- [ ] Dataset downloaded to volume
- [ ] `make modal-benchmark` runs successfully
- [ ] Shows 32 CPU cores, 32GB RAM
- [ ] Environment shows "Modal Cloud Platform"

## 🎯 Expected Performance

### Local (Apple M1 Pro, 10 cores, 16GB)
- **QPS:** 15-25 queries/second
- **Build time:** 1-3 seconds
- **Benchmark time:** 5-15 minutes
- **Recall@10:** >99%

### Modal (32 cores, 32GB)
- **QPS:** 50-100+ queries/second (3-5x faster)
- **Build time:** 1-2 seconds
- **Benchmark time:** 2-8 minutes
- **Recall@10:** >99%

## 🐛 Common Issues

### 1. Permission Errors

```bash
# Fix file permissions
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### 2. Python Version Issues

```bash
# Check Python version
python --version  # Should be 3.9+

# Use specific Python version with uv
uv sync --python 3.12
```

### 3. Build Artifacts

```bash
# Clean everything and rebuild
make clean
make build
```

### 4. Modal Authentication

```bash
# Re-authenticate
modal token new

# Check authentication
modal profile current
```

## ✅ Success Criteria

Your setup is complete and working if:

1. ✅ `make quick` passes all tests
2. ✅ System specs are logged
3. ✅ Recall@10 ≥ 90%
4. ✅ QPS > 0 (non-zero)
5. ✅ No Python import errors
6. ✅ No C++ build errors

## 📚 Next Steps

Once verified:
1. Read [GETTING_STARTED.md](GETTING_STARTED.md) for detailed guide
2. Study [EXAMPLES.md](EXAMPLES.md) for optimization examples
3. Edit `src/algorithm.cpp` to improve your algorithm
4. Test with `make quick`, evaluate with `make benchmark`
5. Compare with `make compare`

## 💬 Support

If you encounter issues:
1. Check this verification guide
2. Review [README.md](README.md) troubleshooting section
3. Check Modal docs: https://modal.com/docs
4. Post on course forum

---

**Happy benchmarking! 🚀**

