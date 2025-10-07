# 🚀 Modal Setup Instructions

Quick setup guide for running ANN benchmarks on Modal's cloud infrastructure.

## Prerequisites

- Python 3.9+ installed
- Internet connection
- Modal account (free tier available)

## Step 1: Install Modal

```bash
# Install Modal CLI
pip install modal

# Or add to your project
make modal-setup
```

## Step 2: Authenticate

```bash
# Create Modal account and get API token
modal token new
```

Follow the prompts to:
1. Create a Modal account (if you don't have one)
2. Get your API token
3. Authenticate locally

## Step 3: Verify Installation

```bash
# Check Modal is working
modal --version

# List your apps (should be empty initially)
modal app list
```

## Step 4: Download Dataset (One-time)

```bash
# Download GIST dataset to persistent volume
make modal-download
```

This will:
- Create a persistent volume named `ann-datasets`
- Download ~3.6GB GIST dataset
- Cache it for future use

**Note**: This costs ~$0.50 and takes 5-10 minutes, but only needs to be done once.

## Step 5: Run Your First Benchmark

```bash
# Run benchmark on 32 CPU cores
make modal-benchmark
```

This will:
- Build your C++ code on Modal
- Run benchmark on GIST dataset
- Use 32 CPU cores and 32GB RAM
- Save results to `results/` directory

## Expected Output

```
🚀 Running ANN benchmark on Modal
   Implementation: student
   Dataset: gist-960-euclidean
   CPU cores: 32
   Memory: 32GB

📁 Setting up project files...
🔨 Building C++ extensions...
✅ Build complete

📊 Running benchmark...
Running benchmark on gist-960-euclidean
  Train: (1000000, 960)
  Test:  (1000, 960)
  k = 10

[1/4] Building index...
  Build time: 15.23s
  Memory: 3840.0 MB

[2/4] Warming up (10 queries)...

[3/4] Measuring throughput (batch queries)...
  QPS: 1245.6
  Batch time: 0.80s

[4/4] Measuring latency (1000 queries)...
  p50: 0.65ms
  p90: 0.89ms
  p95: 1.12ms
  p99: 1.45ms

Calculating recall...
  Recall@10: 0.9234

✅ Operation completed successfully!
```

## Cost Estimation

| Operation | Time | Cost |
|-----------|------|------|
| **Setup** | 5 min | ~$0.50 (one-time) |
| **Benchmark** | 10-30 min | ~$2-5 per run |
| **Compare** | 15-45 min | ~$3-8 per run |

**Total for development**: ~$10-20 for a week of intensive benchmarking.

## Troubleshooting

### "Modal not found"
```bash
pip install modal
```

### "Authentication failed"
```bash
modal token new
```

### "Volume not found"
```bash
make modal-download
```

### "Build failed"
Check the logs:
```bash
modal logs ann-competition
```

### "Timeout error"
The default timeout is 1 hour. For longer runs, modify `modal_app.py`:
```python
@app.function(..., timeout=7200)  # 2 hours
```

## Next Steps

1. **Read the full guide**: [MODAL_GUIDE.md](MODAL_GUIDE.md)
2. **Try different datasets**: `make modal-benchmark-custom IMPL=student DATASET=nytimes-256-angular`
3. **Compare implementations**: `make modal-compare`
4. **Monitor usage**: Check your [Modal dashboard](https://modal.com/dashboard)

## Support

- **Modal Docs**: https://modal.com/docs
- **Modal Community**: https://modal.com/community
- **Issues**: Check [MODAL_GUIDE.md](MODAL_GUIDE.md) troubleshooting section

---

**Ready to supercharge your benchmarks? Run `make modal-benchmark`! 🚀**
