# 🚀 Complete Workflow Guide

## ✅ What Works Out of the Box

### Local Development (100% Automated)
```bash
git clone <repo-url> ann-competition
cd ann-competition
make setup      # ✅ Installs everything (including Modal package)
make build      # ✅ Compiles C++ code
make quick      # ✅ Tests on synthetic data
make benchmark  # ✅ Full benchmark (auto-downloads dataset)
```

**Zero manual steps required!** Everything is automated.

### Modal Cloud (One Manual Step)
```bash
# After make setup, just authenticate:
modal token new      # ⚠️ MANUAL: Create free Modal account (2 minutes)

# Then everything works automatically:
make modal-benchmark # ✅ Auto-downloads dataset if needed, runs benchmark
```

**Only manual step:** Creating a Modal account (one-time, 2 minutes)

## 📋 Detailed Workflows

### Workflow 1: Local Development Only

```bash
# Clone and setup
git clone <repo-url> ann-competition
cd ann-competition
make setup

# Develop your algorithm
vim src/algorithm.cpp

# Test and iterate
make build && make quick      # Fast iteration (~10s)

# Full benchmark when ready
make benchmark                # Complete evaluation (~5-15min)

# Compare with baseline
make compare                  # See your improvement
```

**Commands used:**
- `make setup` - One-time setup
- `make build` - After each code change
- `make quick` - Fast testing
- `make benchmark` - Full evaluation
- `make compare` - Compare implementations

### Workflow 2: Local + Modal Cloud

```bash
# Initial setup (same as local)
git clone <repo-url> ann-competition
cd ann-competition
make setup                    # ✅ Installs Modal package automatically

# ONE-TIME: Authenticate with Modal
modal token new               # Create free Modal account

# Develop locally
vim src/algorithm.cpp
make build && make quick

# Benchmark on cloud (32 CPU cores)
make modal-benchmark          # ✅ Auto-downloads dataset first time
                              # ✅ Runs benchmark on 32 cores
                              # ✅ ~$2-5 per run
```

**Key insight:** Dataset download is automatic! The first `make modal-benchmark` will detect missing dataset and download it automatically.

### Workflow 3: Multiple Datasets

```bash
# Local benchmarks on different datasets
make benchmark                                    # GIST (default)
python scripts/benchmark.py --dataset nytimes-256-angular

# Modal benchmarks on different datasets
make modal-benchmark                              # GIST (default)
make modal-benchmark-custom DATASET=nytimes-256-angular
```

## 🔄 What Happens Behind the Scenes

### `make setup`
1. Checks for `uv` (installs if missing)
2. Creates virtual environment (`.venv/`)
3. Installs Python packages:
   - numpy, h5py, pybind11, matplotlib, scipy
   - **modal** ✅ (included automatically)
4. Ready to go!

### `make build`
1. Runs CMake configuration
2. Detects architecture (ARM64 vs x86_64)
3. Compiles C++ with optimizations
4. Creates `ann_cpp` Python module

### `make benchmark`
1. Builds if needed
2. Checks if dataset exists in `data/`
3. Downloads dataset if missing (~3.6GB, one-time)
4. Runs full benchmark
5. Saves results to `results/`

### `make modal-benchmark` (NEW - Fully Automated!)
1. Uploads your source code to Modal
2. Builds C++ in Modal container
3. **Checks if dataset in volume**
4. **Downloads dataset automatically if missing** ✅
5. Runs benchmark on 32 CPU cores
6. Saves results to Modal volume
7. Streams results back to you

## ✨ Key Improvements

### Before (Required Manual Steps)
```bash
make setup
make build
modal token new                    # Manual
make modal-download                # Manual - separate step
make modal-benchmark               # Finally can run
```

### After (Streamlined!)
```bash
make setup
make build
modal token new                    # Manual (unavoidable)
make modal-benchmark               # ✅ Auto-downloads dataset!
```

**One less step!** Dataset download is now automatic.

## 🎯 What's Automated vs Manual

### ✅ Fully Automated (No User Action)
1. **Python dependencies** - Installed by `make setup`
2. **Modal package** - Included in dependencies
3. **C++ compilation** - Automatic via `make build`
4. **Dataset download (local)** - Auto on first `make benchmark`
5. **Dataset download (Modal)** - Auto on first `make modal-benchmark`
6. **System specs logging** - Always happens
7. **Result saving** - Automatic

### ⚠️ Requires Manual Action (One-Time)
1. **Modal authentication** - `modal token new` (2 minutes)
   - Required by Modal for security/billing
   - Creates free account
   - Only done once per machine

### 📦 Requires Installation (Usually Already Have)
1. **C++ compiler** (GCC/Clang/MSVC)
2. **CMake** (3.15+)
3. **Python** (3.9+)
4. **uv** (installed by `make setup` if missing)

## 💰 Cost Breakdown

### Local (Free)
- Everything runs on your machine
- No costs

### Modal Cloud
- **Setup**: Free
- **Authentication**: Free
- **First dataset download**: ~$0.50 (one-time)
  - **NOW AUTOMATIC** on first `make modal-benchmark`
- **Each benchmark**: ~$2-5
  - 32 CPU cores
  - 32GB RAM
  - 10-30 minutes

## 🎊 Summary

### Question: Does `make modal-benchmark` do everything?

**Answer: Almost everything!**

✅ **Does automatically:**
- Uploads your code
- Builds C++ 
- Downloads dataset (if needed)
- Runs benchmark
- Saves results

⚠️ **Still need manually (one-time):**
- `modal token new` (authenticate)

### Question: Does it all work out of the box?

**Answer: Yes, with one caveat!**

**Local development:** 100% out-of-the-box
- Clone → `make setup` → `make build` → `make benchmark`
- Zero manual steps

**Modal cloud:** 99% out-of-the-box  
- Clone → `make setup` → `modal token new` → `make modal-benchmark`
- One manual step (authentication)

The authentication step is unavoidable (Modal requires it for security), but **everything else is now fully automated**, including dataset downloads!

## 🚀 Quick Reference

### I just cloned the repo, what do I do?
```bash
make setup && make build && make quick
```

### I want to benchmark locally
```bash
make benchmark
```

### I want to use Modal cloud
```bash
modal token new              # First time only
make modal-benchmark         # Everything else is automatic!
```

### I changed my algorithm
```bash
make build && make quick     # Test locally
make modal-benchmark         # Test on cloud
```

---

**Everything else is automatic! 🎉**


