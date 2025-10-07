"""
Metric calculations for ANN benchmarks.
"""

import numpy as np
from typing import List


def calculate_recall(
    predictions: List[List[int]],
    ground_truth: np.ndarray,
    k: int
) -> float:
    """
    Calculate recall@k.
    
    Recall = (# of true positives found) / k
    Averaged over all queries.
    
    Args:
        predictions: List of predicted neighbor indices for each query
        ground_truth: Array of shape (n_queries, k) with true neighbors
        k: Number of neighbors
        
    Returns:
        Mean recall across all queries
    """
    recalls = []
    
    for i, pred in enumerate(predictions):
        true_neighbors = set(ground_truth[i, :k])
        pred_neighbors = set(pred[:k])
        
        # How many predictions are actually in the true top-k?
        num_correct = len(true_neighbors & pred_neighbors)
        recall = num_correct / k
        recalls.append(recall)
    
    return float(np.mean(recalls))


def calculate_precision(
    predictions: List[List[int]],
    ground_truth: np.ndarray,
    k: int
) -> float:
    """
    Calculate precision@k.
    
    Similar to recall@k for ANN (usually equal).
    """
    return calculate_recall(predictions, ground_truth, k)


def calculate_percentiles(values: np.ndarray, percentiles: List[float]) -> dict:
    """
    Calculate percentile statistics.
    
    Args:
        values: Array of values
        percentiles: List of percentiles to compute (e.g., [50, 90, 95, 99])
        
    Returns:
        Dictionary mapping percentile to value
    """
    result = {}
    for p in percentiles:
        result[f'p{int(p)}'] = float(np.percentile(values, p))
    return result


def calculate_qps(num_queries: int, total_time: float) -> float:
    """
    Calculate queries per second.
    
    Args:
        num_queries: Number of queries executed
        total_time: Total execution time in seconds
        
    Returns:
        QPS (queries per second)
    """
    return num_queries / total_time


def calculate_speedup(baseline_qps: float, optimized_qps: float) -> float:
    """
    Calculate speedup relative to baseline.
    
    Args:
        baseline_qps: Baseline QPS
        optimized_qps: Optimized QPS
        
    Returns:
        Speedup factor
    """
    return optimized_qps / baseline_qps


def score_algorithm(recall: float, qps: float, memory_mb: float) -> float:
    """
    Calculate composite competition score.
    
    Score balances accuracy, speed, and memory usage.
    
    Formula: recall * log10(qps) / log10(memory_mb)
    
    Args:
        recall: Recall@k (0 to 1)
        qps: Queries per second
        memory_mb: Memory usage in MB
        
    Returns:
        Competition score (higher is better)
    """
    import math
    
    # Require minimum recall threshold
    if recall < 0.9:
        return 0.0
    
    # Reward high QPS, penalize high memory
    score = recall * math.log10(max(qps, 1.0))
    
    if memory_mb > 0:
        score /= math.log10(max(memory_mb, 10.0))
    
    return score
