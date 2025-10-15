#!/usr/bin/env python3
"""
Main benchmark script.

Usage:
    python scripts/benchmark.py --impl vectordb
    python scripts/benchmark.py --impl naive --dataset nytimes-256-angular
    python scripts/benchmark.py --impl vectordb --compare naive
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root and build directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "build"))

from python.benchmark import Benchmark, run_comparison
from python.dataset_loader import DatasetLoader
from ann_cpp import ANNAlgorithm


def main():
    parser = argparse.ArgumentParser(
        description='Benchmark ANN algorithm implementation'
    )
    parser.add_argument(
        '--impl',
        choices=['naive', 'vectordb'],
        default='vectordb',
        help='Implementation to benchmark'
    )
    parser.add_argument(
        '--dataset',
        default='gist-960-euclidean',
        help='Dataset to use'
    )
    parser.add_argument(
        '--compare',
        help='Compare against another implementation'
    )
    parser.add_argument(
        '--k',
        type=int,
        default=10,
        help='Number of neighbors to retrieve'
    )
    parser.add_argument(
        '--output',
        help='Save results to JSON file'
    )
    parser.add_argument(
        '--subset-size',
        type=int,
        help='Use only a subset of the dataset for quick testing'
    )
    parser.add_argument(
        '--list-datasets',
        action='store_true',
        help='List available datasets'
    )
    
    args = parser.parse_args()
    
    # List datasets if requested
    if args.list_datasets:
        print("Available datasets:")
        for name in DatasetLoader.list_datasets():
            config = DatasetLoader.DATASETS[name]
            print(f"  - {name}")
            print(f"      Dimension: {config['dimension']}")
            print(f"      Metric: {config['metric']}")
        return
    
    # Load dataset info
    loader = DatasetLoader(args.dataset)
    metric = loader.config['metric']
    
    # Create algorithm instance(s)
    algorithms = []
    
    algo = ANNAlgorithm(args.impl, metric)
    algorithms.append((f"{args.impl} ({metric})", algo))
    
    if args.compare:
        compare_algo = ANNAlgorithm(args.compare, metric)
        algorithms.append((f"{args.compare} ({metric})", compare_algo))
    
    # Run benchmark
    if len(algorithms) == 1:
        benchmark = Benchmark(args.dataset, subset_size=args.subset_size)
        results = benchmark.run_full_benchmark(algo, k=args.k)
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Algorithm:     {results['algorithm']}")
        print(f"Dataset:       {results['dataset']}")
        print(f"Build time:    {results['build_time']:.2f}s")
        print(f"Memory:        {results['memory_mb']:.1f} MB")
        print(f"Recall@{args.k}:     {results['recall']:.4f}")
        print(f"QPS:           {results['throughput']['qps']:.1f}")
        print(f"Latency (p50): {results['latency']['p50']*1000:.2f}ms")
        print(f"Latency (p95): {results['latency']['p95']*1000:.2f}ms")
        print(f"Latency (p99): {results['latency']['p99']*1000:.2f}ms")
        
        results_list = [results]
    else:
        results_list = run_comparison(algorithms, args.dataset, subset_size=args.subset_size)
    
    # Save results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results_list,
            }, f, indent=2)
        
        print(f"\n✓ Results saved to {output_path}")


if __name__ == '__main__':
    main()