#!/usr/bin/env python3
"""
Quick test script for rapid iteration.
Tests on a small subset of data for fast feedback.
"""

import sys
import numpy as np
from pathlib import Path

# Add project root and build directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "build"))

from ann_cpp import ANNAlgorithm


def create_synthetic_data(n_samples=1000, dimension=128):
    """Create small synthetic dataset for testing."""
    np.random.seed(42)
    
    # Random vectors
    train = np.random.randn(n_samples, dimension).astype(np.float32)
    test = np.random.randn(100, dimension).astype(np.float32)
    
    # Normalize for angular distance
    train = train / np.linalg.norm(train, axis=1, keepdims=True)
    test = test / np.linalg.norm(test, axis=1, keepdims=True)
    
    return train, test


def test_algorithm(impl='student', metric='euclidean'):
    """Quick functionality test."""
    print(f"Testing {impl} implementation with {metric} metric")
    
    # Create test data
    print("Creating synthetic data...")
    train, test = create_synthetic_data()
    print(f"  Train: {train.shape}")
    print(f"  Test:  {test.shape}")
    
    # Create algorithm
    print(f"\nInitializing {impl} algorithm...")
    algo = ANNAlgorithm(impl, metric)
    
    # Build index
    print("Building index...")
    import time
    start = time.time()
    algo.fit(train)
    build_time = time.time() - start
    print(f"  Build time: {build_time:.3f}s")
    print(f"  Memory: {algo.get_memory_usage() / 1e6:.1f} MB")
    
    # Single query test
    print("\nTesting single query...")
    start = time.time()
    result = algo.query(test[0], k=10)
    query_time = time.time() - start
    print(f"  Query time: {query_time*1000:.2f}ms")
    print(f"  Results: {result}")
    
    # Batch query test
    print("\nTesting batch query...")
    start = time.time()
    results = algo.batch_query(test, k=10)
    batch_time = time.time() - start
    qps = len(test) / batch_time
    print(f"  Batch time: {batch_time:.3f}s")
    print(f"  QPS: {qps:.1f}")
    print(f"  Results shape: {len(results)} queries x {len(results[0])} neighbors")
    
    # Validation
    print("\nValidation:")
    if len(results) == len(test):
        print("  ✓ Correct number of results")
    else:
        print(f"  ✗ Wrong number of results: {len(results)} != {len(test)}")
    
    if all(len(r) == 10 for r in results):
        print("  ✓ Correct number of neighbors per query")
    else:
        print("  ✗ Wrong number of neighbors in some results")
    
    if all(0 <= idx < len(train) for r in results for idx in r):
        print("  ✓ All indices in valid range")
    else:
        print("  ✗ Some indices out of range")
    
    print("\n✓ Test complete!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--impl', default='student', choices=['naive', 'student'])
    parser.add_argument('--metric', default='euclidean', choices=['euclidean', 'angular'])
    
    args = parser.parse_args()
    
    test_algorithm(args.impl, args.metric)
