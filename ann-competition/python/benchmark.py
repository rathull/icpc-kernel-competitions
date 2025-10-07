"""
Comprehensive benchmarking for ANN algorithms.

Calculates:
- Recall @ k
- QPS (queries per second) for throughput
- Latency (p50, p90, p95, p99) for single queries
- Memory usage
- Build time
"""

import time
import numpy as np
from typing import Dict, List, Tuple
from .metrics import calculate_recall, calculate_percentiles
from .dataset_loader import DatasetLoader


class Benchmark:
    """Run comprehensive benchmarks on ANN algorithm."""
    
    def __init__(self, dataset_name: str = "gist-960-euclidean"):
        self.loader = DatasetLoader(dataset_name)
        self.dataset = self.loader.load()
        
    def run_full_benchmark(
        self, 
        algorithm, 
        k: int = 10,
        num_warmup: int = 10,
        num_latency_samples: int = 100
    ) -> Dict:
        """
        Run complete benchmark suite.
        
        Args:
            algorithm: ANNAlgorithm instance
            k: Number of neighbors to retrieve
            num_warmup: Warmup queries before timing
            num_latency_samples: Queries for latency measurement
            
        Returns:
            Dictionary with all metrics
        """
        print(f"Running benchmark on {self.dataset['name']}")
        print(f"  Train: {self.dataset['train'].shape}")
        print(f"  Test:  {self.dataset['test'].shape}")
        print(f"  k = {k}")
        
        # Build index
        print("\n[1/4] Building index...")
        build_time, memory_usage = self._measure_build(algorithm)
        print(f"  Build time: {build_time:.2f}s")
        print(f"  Memory: {memory_usage / 1e6:.1f} MB")
        
        # Warmup
        print(f"\n[2/4] Warming up ({num_warmup} queries)...")
        self._warmup(algorithm, k, num_warmup)
        
        # Measure throughput (batch)
        print("\n[3/4] Measuring throughput (batch queries)...")
        throughput_metrics = self._measure_throughput(algorithm, k)
        print(f"  QPS: {throughput_metrics['qps']:.1f}")
        print(f"  Batch time: {throughput_metrics['total_time']:.2f}s")
        
        # Measure latency (single queries)
        print(f"\n[4/4] Measuring latency ({num_latency_samples} queries)...")
        latency_metrics = self._measure_latency(
            algorithm, k, num_latency_samples
        )
        print(f"  p50: {latency_metrics['p50']*1000:.2f}ms")
        print(f"  p90: {latency_metrics['p90']*1000:.2f}ms")
        print(f"  p95: {latency_metrics['p95']*1000:.2f}ms")
        print(f"  p99: {latency_metrics['p99']*1000:.2f}ms")
        
        # Calculate recall
        print("\nCalculating recall...")
        recall = calculate_recall(
            throughput_metrics['results'],
            self.dataset['ground_truth'],
            k
        )
        print(f"  Recall@{k}: {recall:.4f}")
        
        return {
            'algorithm': algorithm.name(),
            'dataset': self.dataset['name'],
            'k': k,
            'build_time': build_time,
            'memory_mb': memory_usage / 1e6,
            'recall': recall,
            'throughput': throughput_metrics,
            'latency': latency_metrics,
        }
    
    def _measure_build(self, algorithm) -> Tuple[float, int]:
        """Measure index build time and memory usage."""
        start = time.perf_counter()
        algorithm.fit(self.dataset['train'])
        build_time = time.perf_counter() - start
        
        memory_usage = algorithm.get_memory_usage()
        return build_time, memory_usage
    
    def _warmup(self, algorithm, k: int, num_queries: int):
        """Warmup queries to stabilize performance."""
        test_queries = self.dataset['test'][:num_queries]
        for query in test_queries:
            algorithm.query(query, k)
    
    def _measure_throughput(self, algorithm, k: int) -> Dict:
        """Measure batch query throughput (QPS)."""
        test_queries = self.dataset['test']
        
        start = time.perf_counter()
        results = algorithm.batch_query(test_queries, k)
        total_time = time.perf_counter() - start
        
        qps = len(test_queries) / total_time
        
        return {
            'qps': qps,
            'total_time': total_time,
            'num_queries': len(test_queries),
            'results': results,
        }
    
    def _measure_latency(
        self, 
        algorithm, 
        k: int, 
        num_samples: int
    ) -> Dict:
        """Measure single-query latency distribution."""
        test_queries = self.dataset['test'][:num_samples]
        
        latencies = []
        for query in test_queries:
            start = time.perf_counter()
            algorithm.query(query, k)
            latency = time.perf_counter() - start
            latencies.append(latency)
        
        latencies = np.array(latencies)
        
        return {
            'mean': float(np.mean(latencies)),
            'std': float(np.std(latencies)),
            'min': float(np.min(latencies)),
            'max': float(np.max(latencies)),
            'p50': float(np.percentile(latencies, 50)),
            'p90': float(np.percentile(latencies, 90)),
            'p95': float(np.percentile(latencies, 95)),
            'p99': float(np.percentile(latencies, 99)),
        }


def run_comparison(algorithms: List, dataset_name: str = "gist-960-euclidean"):
    """
    Compare multiple algorithms.
    
    Args:
        algorithms: List of (name, algo_instance) tuples
        dataset_name: Dataset to use
    """
    benchmark = Benchmark(dataset_name)
    results = []
    
    for name, algo in algorithms:
        print(f"\n{'='*60}")
        print(f"Algorithm: {name}")
        print('='*60)
        
        result = benchmark.run_full_benchmark(algo)
        results.append(result)
    
    # Print comparison table
    print(f"\n{'='*60}")
    print("COMPARISON")
    print('='*60)
    print(f"{'Algorithm':<20} {'Recall@10':<12} {'QPS':<12} {'p50 (ms)':<12}")
    print('-'*60)
    for r in results:
        print(f"{r['algorithm']:<20} "
              f"{r['recall']:<12.4f} "
              f"{r['throughput']['qps']:<12.1f} "
              f"{r['latency']['p50']*1000:<12.2f}")
    
    return results