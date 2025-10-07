"""
Dataset loading and management.
Supports easy swapping between datasets.
"""

import os
import h5py
import numpy as np
import urllib.request
from pathlib import Path
from typing import Dict


class DatasetLoader:
    """Load and cache ANN benchmark datasets."""
    
    DATASETS = {
        'gist-960-euclidean': {
            'url': 'http://ann-benchmarks.com/gist-960-euclidean.hdf5',
            'dimension': 960,
            'metric': 'euclidean',
        },
        'nytimes-256-angular': {
            'url': 'http://ann-benchmarks.com/nytimes-256-angular.hdf5',
            'dimension': 256,
            'metric': 'angular',
        },
        'fashion-mnist-784-euclidean': {
            'url': 'http://ann-benchmarks.com/fashion-mnist-784-euclidean.hdf5',
            'dimension': 784,
            'metric': 'euclidean',
        },
        'sift-128-euclidean': {
            'url': 'http://ann-benchmarks.com/sift-128-euclidean.hdf5',
            'dimension': 128,
            'metric': 'euclidean',
        },
    }
    
    def __init__(self, dataset_name: str, data_dir: str = 'data'):
        if dataset_name not in self.DATASETS:
            raise ValueError(
                f"Unknown dataset: {dataset_name}. "
                f"Available: {list(self.DATASETS.keys())}"
            )
        
        self.dataset_name = dataset_name
        self.config = self.DATASETS[dataset_name]
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    @property
    def filepath(self) -> Path:
        """Path to dataset file."""
        return self.data_dir / f"{self.dataset_name}.hdf5"
    
    def download(self):
        """Download dataset if not already cached."""
        if self.filepath.exists():
            print(f"Dataset already downloaded: {self.filepath}")
            return
        
        print(f"Downloading {self.dataset_name}...")
        url = self.config['url']
        
        # Download with progress
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / 1e6
            mb_total = total_size / 1e6
            print(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", 
                  end='', flush=True)
        
        try:
            urllib.request.urlretrieve(
                url, 
                self.filepath, 
                reporthook=report_progress
            )
            print(f"\n✓ Downloaded to {self.filepath}")
        except Exception as e:
            if self.filepath.exists():
                self.filepath.unlink()
            raise RuntimeError(f"Failed to download dataset: {e}")
    
    def load(self) -> Dict[str, np.ndarray]:
        """
        Load dataset into memory.
        
        Returns:
            Dictionary with:
            - 'train': Training vectors (n_train, dimension)
            - 'test': Test queries (n_test, dimension)
            - 'ground_truth': True k-NN for test queries (n_test, k)
            - 'distances': Distances to true neighbors (n_test, k)
            - 'name': Dataset name
            - 'metric': Distance metric
            - 'dimension': Vector dimension
        """
        # Download if needed
        if not self.filepath.exists():
            self.download()
        
        print(f"Loading {self.dataset_name}...")
        
        with h5py.File(self.filepath, 'r') as f:
            # Load data
            train = np.array(f['train'])
            test = np.array(f['test'])
            neighbors = np.array(f['neighbors'])
            
            # Optional: distances (not all datasets have this)
            distances = np.array(f['distances']) if 'distances' in f else None
            
            print(f"✓ Loaded:")
            print(f"  Train: {train.shape}")
            print(f"  Test:  {test.shape}")
            print(f"  Ground truth: {neighbors.shape}")
        
        return {
            'train': train.astype(np.float32),
            'test': test.astype(np.float32),
            'ground_truth': neighbors,
            'distances': distances,
            'name': self.dataset_name,
            'metric': self.config['metric'],
            'dimension': self.config['dimension'],
        }
    
    @classmethod
    def list_datasets(cls) -> list:
        """List all available datasets."""
        return list(cls.DATASETS.keys())


def quick_load(dataset_name: str = 'gist-960-euclidean') -> Dict:
    """
    Quick load a dataset.
    
    Args:
        dataset_name: Name of dataset to load
        
    Returns:
        Dataset dictionary
    """
    loader = DatasetLoader(dataset_name)
    return loader.load()
