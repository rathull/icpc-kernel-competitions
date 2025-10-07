"""
Modal app for running ANN benchmarks on powerful hardware.

Usage:
    modal run modal_app.py --impl student
    modal run modal_app.py --impl student --dataset nytimes-256-angular
    modal run modal_app.py --impl student --compare naive
"""

import modal
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

# Create Modal app
app = modal.App("ann-competition")

# Create a persistent volume for dataset storage (shared across all datasets)
# Using create_if_missing=True ensures it's created on first use
VOLUME_NAME = "ann-datasets"
dataset_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
VOLUME_MOUNT_PATH = "/data"

# Define the image with all dependencies and source code
# Note: .modalignore file automatically excludes build artifacts and cache
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install(
        "build-essential", 
        "cmake", 
        "libomp-dev", 
        "git", 
        "wget",
        "pybind11-dev"  # Provides CMake config for pybind11
    )
    .pip_install(
        "numpy>=1.24.0",
        "h5py>=3.8.0", 
        "pybind11>=2.11.0",
        "matplotlib>=3.7.0",
        "scipy>=1.10.0",
    )
    # Add source code (respects .modalignore)
    .add_local_dir(project_root, remote_path="/root/ann-competition")
)

def _download_dataset_internal(dataset):
    """Internal helper to download dataset (called within a running function)."""
    import subprocess
    import os
    
    DATASETS = {
        'gist-960-euclidean': 'http://ann-benchmarks.com/gist-960-euclidean.hdf5',
        'nytimes-256-angular': 'http://ann-benchmarks.com/nytimes-256-angular.hdf5',
        'fashion-mnist-784-euclidean': 'http://ann-benchmarks.com/fashion-mnist-784-euclidean.hdf5',
        'sift-128-euclidean': 'http://ann-benchmarks.com/sift-128-euclidean.hdf5',
    }
    
    if dataset not in DATASETS:
        return {"success": False, "error": f"Unknown dataset: {dataset}"}
    
    filename = f"{VOLUME_MOUNT_PATH}/{dataset}.hdf5"
    url = DATASETS[dataset]
    
    print(f"📥 Downloading {dataset} from {url}...")
    print(f"   Saving to volume: '{VOLUME_NAME}' at path: {filename}")
    print()
    result = subprocess.run(
        ["wget", "-O", filename, url, "--progress=bar:force"]
    )
    
    if result.returncode != 0:
        return {"success": False, "error": "Download failed"}
    
    # Verify downloaded file
    try:
        import h5py
        with h5py.File(filename, 'r') as f:
            print()
            print(f"✅ Downloaded and verified:")
            print(f"   Train: {f['train'].shape}")
            print(f"   Test: {f['test'].shape}")
    except Exception as e:
        os.remove(filename)
        return {"success": False, "error": f"Invalid file: {e}"}
    
    # Commit to volume so it persists for future runs
    print(f"💾 Committing dataset to volume '{VOLUME_NAME}'...")
    dataset_volume.commit()
    print(f"✅ Dataset '{dataset}' persisted to volume!")
    print(f"   Future runs will use the cached version (no download needed)")
    
    return {"success": True, "dataset": dataset}

@app.function(
    image=image,
    volumes={VOLUME_MOUNT_PATH: dataset_volume},
    cpu=32,  # Use up to 32 CPU cores
    memory=32768,  # 32GB RAM
    timeout=3600,  # 1 hour timeout
)
def run_benchmark(impl="student", dataset="gist-960-euclidean", compare=None, k=10):
    """Run ANN benchmark on Modal with high-performance hardware."""
    import subprocess
    import os
    import sys
    
    print(f"🚀 Running ANN benchmark on Modal")
    print(f"   Implementation: {impl}")
    print(f"   Dataset: {dataset}")
    print(f"   Volume: '{VOLUME_NAME}' mounted at {VOLUME_MOUNT_PATH}")
    print(f"   CPU cores: 32")
    print(f"   Memory: 32GB")
    print()
    
    # Set up environment
    os.environ["OMP_NUM_THREADS"] = "32"  # Use all cores for OpenMP
    os.environ["MODAL_TASK_ID"] = os.environ.get("MODAL_TASK_ID", "modal-benchmark")
    
    # Change to project directory
    os.chdir("/root/ann-competition")
    
    # Add python path
    sys.path.insert(0, "/root/ann-competition")
    sys.path.insert(0, "/root/ann-competition/build")
    
    # Build the project
    print("🔨 Building C++ extensions...")
    # Clean build directory to avoid cache conflicts
    subprocess.run(["rm", "-rf", "build"], check=True)
    subprocess.run(["mkdir", "-p", "build"], check=True)
    
    # Configure CMake
    result = subprocess.run(
        ["cmake", "-S", ".", "-B", "build", "-DCMAKE_BUILD_TYPE=Release"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ CMake configuration failed:")
        print(result.stdout)
        print(result.stderr)
        return {"success": False, "error": "CMake configuration failed"}
    
    print("✅ CMake configured")
    
    # Build with all cores
    result = subprocess.run(
        ["cmake", "--build", "build", "-j", "32"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Build failed:")
        print(result.stdout)
        print(result.stderr)
        return {"success": False, "error": "Build failed"}
    
    print("✅ Build complete")
    print()
    
    # Check if dataset exists in volume
    print(f"📦 Checking for dataset in volume '{VOLUME_NAME}'...")
    dataset_path = f"{VOLUME_MOUNT_PATH}/{dataset}.hdf5"
    
    # Reload volume to see any changes from other containers
    # This ensures we see datasets that may have been downloaded by other runs
    try:
        dataset_volume.reload()
        print(f"   ✓ Reloaded volume to check for latest changes")
    except Exception as e:
        # First access or volume is busy - this is normal
        print(f"   Note: Volume reload skipped ({str(e)[:50]}...)")
    
    if not os.path.exists(dataset_path):
        print(f"⚠️  Dataset '{dataset}' not found in volume '{VOLUME_NAME}'")
        print(f"   Downloading now (this is a ONE-TIME operation)...")
        print()
        download_result = _download_dataset_internal(dataset)
        if not download_result["success"]:
            return download_result
        print()
    else:
        print(f"✅ Dataset '{dataset}' found in volume '{VOLUME_NAME}'!")
        print(f"   Using cached dataset (no download needed)")
        print(f"   Path: {dataset_path}")
        print()
    
    # Run benchmark
    print("📊 Running benchmark...")
    print()
    
    # Build command
    if compare:
        cmd = [
            "python", "scripts/benchmark.py",
            "--impl", impl,
            "--compare", compare,
            "--dataset", dataset,
            "--k", str(k),
            "--output", f"results/modal_benchmark_{impl}_vs_{compare}.json"
        ]
    else:
        cmd = [
            "python", "scripts/benchmark.py", 
            "--impl", impl,
            "--dataset", dataset,
            "--k", str(k),
            "--output", f"results/modal_benchmark_{impl}.json"
        ]
    
    # Set environment for the benchmark
    env = os.environ.copy()
    env["PYTHONPATH"] = "/root/ann-competition:/root/ann-competition/build"
    
    # Run the benchmark - stream output in real-time
    result = subprocess.run(cmd, env=env)
    
    if result.returncode != 0:
        print(f"❌ Benchmark failed with return code {result.returncode}")
        return {"success": False, "error": f"Benchmark failed with return code {result.returncode}"}
    
    print()
    print("✅ Benchmark completed successfully!")
    
    return {
        "success": True,
        "impl": impl,
        "dataset": dataset,
        "compare": compare,
        "volume": VOLUME_NAME,
        "message": "Benchmark completed on Modal"
    }

@app.function(
    image=image,
    volumes={VOLUME_MOUNT_PATH: dataset_volume},
    cpu=8,
    memory=16384,
    timeout=1800,
)
def download_dataset(dataset="gist-960-euclidean"):
    """Download dataset to persistent volume."""
    import subprocess
    import os
    
    print(f"📥 Pre-downloading dataset to persistent volume")
    print(f"   Dataset: {dataset}")
    print(f"   Volume: '{VOLUME_NAME}' mounted at {VOLUME_MOUNT_PATH}")
    print()
    
    # Dataset URLs
    DATASETS = {
        'gist-960-euclidean': 'http://ann-benchmarks.com/gist-960-euclidean.hdf5',
        'nytimes-256-angular': 'http://ann-benchmarks.com/nytimes-256-angular.hdf5',
        'fashion-mnist-784-euclidean': 'http://ann-benchmarks.com/fashion-mnist-784-euclidean.hdf5',
        'sift-128-euclidean': 'http://ann-benchmarks.com/sift-128-euclidean.hdf5',
    }
    
    if dataset not in DATASETS:
        print(f"❌ Unknown dataset: {dataset}")
        print(f"   Available datasets: {', '.join(DATASETS.keys())}")
        return {"success": False, "error": f"Unknown dataset: {dataset}"}
    
    filename = f"{VOLUME_MOUNT_PATH}/{dataset}.hdf5"
    url = DATASETS[dataset]
    
    # Reload volume to see if another container already downloaded it
    try:
        dataset_volume.reload()
        print(f"✓ Reloaded volume '{VOLUME_NAME}' to check for existing datasets")
    except Exception as e:
        print(f"Note: Could not reload volume ({str(e)[:50]}...)")
    
    # Check if already downloaded
    if os.path.exists(filename):
        print(f"✅ Dataset already exists in volume '{VOLUME_NAME}'!")
        
        # Verify it's a valid HDF5 file
        try:
            import h5py
            with h5py.File(filename, 'r') as f:
                print(f"   Train: {f['train'].shape}")
                print(f"   Test: {f['test'].shape}")
                print(f"   Ground truth: {f['neighbors'].shape}")
            print()
            print("✓ Dataset is valid and ready to use")
            print("  (no download needed)")
            return {"success": True, "dataset": dataset, "already_exists": True, "volume": VOLUME_NAME}
        except Exception as e:
            print(f"⚠️  Existing file is corrupted: {e}")
            print(f"   Re-downloading...")
            os.remove(filename)
    
    # Download dataset
    print(f"📥 Downloading from {url}...")
    print(f"   Saving to: {filename}")
    print()
    result = subprocess.run(
        ["wget", "-O", filename, url, "--progress=bar:force"]
    )
    
    if result.returncode != 0:
        print(f"❌ Download failed")
        return {"success": False, "error": "Download failed"}
    
    # Verify downloaded file
    try:
        import h5py
        with h5py.File(filename, 'r') as f:
            print()
            print(f"✅ Downloaded successfully:")
            print(f"   Train: {f['train'].shape}")
            print(f"   Test: {f['test'].shape}")
            print(f"   Ground truth: {f['neighbors'].shape}")
    except Exception as e:
        print(f"❌ Downloaded file is invalid: {e}")
        os.remove(filename)
        return {"success": False, "error": f"Invalid file: {e}"}
    
    # Commit to volume so it persists
    print()
    print(f"💾 Committing dataset to volume '{VOLUME_NAME}'...")
    dataset_volume.commit()
    
    print(f"✅ Dataset '{dataset}' successfully saved to volume!")
    print(f"   All future benchmark runs will use this cached version")
    
    return {"success": True, "dataset": dataset, "volume": VOLUME_NAME}

@app.local_entrypoint()
def main(
    impl: str = "student",
    dataset: str = "gist-960-euclidean", 
    compare: str = None,
    k: int = 10,
    download_only: bool = False
):
    """Main entrypoint for Modal ANN benchmark."""
    
    if download_only:
        print("📥 Downloading dataset only...")
        result = download_dataset.remote(dataset)
    else:
        print("🚀 Running full benchmark...")
        result = run_benchmark.remote(impl, dataset, compare, k)
    
    if result["success"]:
        print()
        print("✅ Operation completed successfully!")
        return 0
    else:
        print()
        print("❌ Operation failed!")
        if "error" in result:
            print(f"Error: {result['error']}")
        return 1
