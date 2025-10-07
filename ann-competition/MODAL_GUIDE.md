# 🚀 Modal Cloud Benchmarking Guide

Run your ANN benchmarks on Modal's powerful cloud infrastructure with **32 CPU cores** and **32GB RAM**!

## 🎯 Why Use Modal?

- **32 CPU cores** - Massive parallelization power
- **32GB RAM** - Handle large datasets easily  
- **Persistent datasets** - Download once, reuse forever
- **Fast networking** - High-speed dataset downloads
- **Pay-per-use** - Only pay for compute time

## ⚡ Quick Start

### 1. Setup Modal (One-time)

```bash
# Install Modal CLI
pip install modal

# Authenticate with Modal
modal token new

# Add Modal to your project
make modal-setup
```

### 2. Download Dataset (One-time)

```bash
# Download GIST dataset to persistent volume (~3.6GB)
make modal-download
```

### 3. Run Benchmark

```bash
# Run benchmark on 32 CPU cores
make modal-benchmark

# Compare implementations
make modal-compare

# Custom benchmark
make modal-benchmark-custom IMPL=student DATASET=nytimes-256-angular
```

## 📋 Available Commands

| Command | Purpose | Time | Cost |
|---------|---------|------|------|
| `make modal-setup` | Install Modal package | 30s | Free |
| `make modal-download` | Download dataset once | 5-10min | ~$0.50 |
| `make modal-benchmark` | Full benchmark | 10-30min | ~$2-5 |
| `make modal-compare` | Compare implementations | 15-45min | ~$3-8 |

## 🔧 How It Works

### Persistent Volume Storage

```python
# Datasets are stored in Modal volumes
dataset_volume = modal.Volume.from_name("ann-datasets", create_if_missing=True)

# Volume persists across runs
volumes={"/data": dataset_volume}
```

**Benefits:**
- ✅ Download once, reuse forever
- ✅ Shared across all your benchmarks
- ✅ Survives container restarts
- ✅ Fast access (no re-downloading)

### High-Performance Hardware

```python
@app.function(
    cpu=32,        # 32 CPU cores
    memory=32768,  # 32GB RAM
    timeout=3600,  # 1 hour max
)
```

**Specs:**
- **CPU**: 32 cores (vs your local 4-8 cores)
- **RAM**: 32GB (vs your local 8-16GB)
- **Network**: High-speed internet
- **Storage**: Fast SSD storage

## 📊 Performance Comparison

| Metric | Local (MacBook) | Modal (32 cores) | Speedup |
|--------|-----------------|------------------|---------|
| **Build time** | 10-30s | 5-15s | 2-3x |
| **Benchmark time** | 5-15min | 2-8min | 2-4x |
| **QPS** | 100-1000 | 1000-10000 | 5-10x |
| **Memory limit** | 8-16GB | 32GB | 2-4x |

## 💰 Cost Estimation

### Typical Usage

```bash
# One-time setup
make modal-setup        # Free
make modal-download     # ~$0.50 (one-time)

# Daily development
make modal-benchmark    # ~$2-5 per run
make modal-compare      # ~$3-8 per run
```

### Cost Breakdown

- **CPU**: ~$0.10/hour per core = $3.20/hour for 32 cores
- **Memory**: ~$0.01/hour per GB = $0.32/hour for 32GB
- **Storage**: ~$0.10/GB/month for volumes
- **Network**: Free for downloads

**Example**: 30-minute benchmark = ~$1.76

## 🛠 Advanced Usage

### Custom Datasets

```bash
# Use different dataset
make modal-benchmark-custom IMPL=student DATASET=nytimes-256-angular

# Compare on specific dataset
modal run modal_app.py --impl student --compare naive --dataset sift-128-euclidean
```

### Direct Modal Commands

```bash
# Run benchmark directly
modal run modal_app.py --impl student --dataset gist-960-euclidean

# Download dataset only
modal run modal_app.py --download-only --dataset nytimes-256-angular

# Compare implementations
modal run modal_app.py --impl student --compare naive --k 20
```

### Environment Variables

```bash
# Set OpenMP threads (automatic)
export OMP_NUM_THREADS=32

# Custom timeout
export MODAL_TIMEOUT=7200  # 2 hours
```

## 🔍 Monitoring and Debugging

### View Logs

```bash
# Real-time logs
modal logs ann-competition

# Specific function logs
modal logs ann-competition::run_benchmark
```

### Check Volume Status

```bash
# List volumes
modal volume list

# Check volume contents
modal volume get ann-datasets
```

### Debug Mode

```python
# Add to modal_app.py for debugging
@app.function(..., timeout=7200)  # Longer timeout
def run_benchmark(...):
    import pdb; pdb.set_trace()  # Debug breakpoint
```

## 📈 Optimization Tips

### For Modal Performance

1. **Use all cores**: Set `OMP_NUM_THREADS=32`
2. **Batch operations**: Process multiple queries together
3. **Memory efficiency**: Use 32GB wisely
4. **Persistent data**: Keep datasets in volumes

### For Cost Optimization

1. **Download once**: Use `modal-download` for datasets
2. **Batch benchmarks**: Run multiple tests in one session
3. **Right-size**: Use appropriate CPU/memory for your needs
4. **Monitor usage**: Check Modal dashboard for costs

## 🐛 Troubleshooting

### Common Issues

**"Modal not found"**
```bash
pip install modal
modal token new
```

**"Volume not found"**
```bash
make modal-download  # Creates volume
```

**"Build failed"**
```bash
# Check logs
modal logs ann-competition::run_benchmark
```

**"Timeout error"**
```bash
# Increase timeout in modal_app.py
@app.function(..., timeout=7200)
```

### Performance Issues

**Slow downloads**
- First download is slow (~10 min)
- Subsequent runs use cached data

**Low QPS**
- Check OpenMP threads: `OMP_NUM_THREADS=32`
- Verify parallelization in your code
- Check memory usage

**High costs**
- Monitor usage in Modal dashboard
- Use smaller datasets for testing
- Batch multiple operations

## 📚 Examples

### Basic Workflow

```bash
# 1. Setup (one-time)
make modal-setup
make modal-download

# 2. Development loop
make build && make quick          # Local testing
make modal-benchmark              # Cloud benchmarking

# 3. Optimization
make modal-compare                # Compare implementations
```

### Advanced Workflow

```bash
# 1. Test different datasets
make modal-benchmark-custom IMPL=student DATASET=nytimes-256-angular
make modal-benchmark-custom IMPL=student DATASET=sift-128-euclidean

# 2. Compare implementations
modal run modal_app.py --impl student --compare naive --dataset gist-960-euclidean

# 3. Custom parameters
modal run modal_app.py --impl student --k 20 --dataset gist-960-euclidean
```

## 🔗 Resources

- **Modal Docs**: https://modal.com/docs
- **Modal Pricing**: https://modal.com/pricing
- **OpenMP Guide**: https://www.openmp.org/resources/tutorials-articles/
- **ANN Benchmarks**: http://ann-benchmarks.com/

## 🎯 Best Practices

### Development

1. **Local first**: Use `make quick` for rapid iteration
2. **Cloud for final**: Use `make modal-benchmark` for evaluation
3. **Compare regularly**: Use `make modal-compare` to track progress
4. **Monitor costs**: Check Modal dashboard weekly

### Optimization

1. **Parallelize everything**: Use all 32 cores
2. **Memory efficient**: Leverage 32GB RAM
3. **Cache datasets**: Download once, reuse forever
4. **Batch operations**: Minimize Modal calls

### Cost Management

1. **Download once**: Use persistent volumes
2. **Batch benchmarks**: Run multiple tests together
3. **Right-size**: Match hardware to needs
4. **Monitor usage**: Track spending in dashboard

---

**Ready to supercharge your ANN benchmarks? Start with `make modal-setup`! 🚀**
