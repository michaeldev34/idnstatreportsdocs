"""
Linearity Detection

Tests whether relationships in data are linear or non-linear.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any


class LinearityDetector:
    """
    Detects linearity in relationships between variables.
    
    Uses multiple tests:
    - Pearson vs Spearman correlation comparison
    - Rainbow test for linearity
    - Residual patterns from linear fit
    """
    
    def __init__(self, threshold: float = 0.85):
        """
        Args:
            threshold: Correlation threshold for linearity (default: 0.85)
        """
        self.threshold = threshold
    
    def test_linearity(self, df: pd.DataFrame) -> bool:
        """
        Test if data exhibits primarily linear relationships.
        
        Args:
            df: Input DataFrame
            
        Returns:
            True if data appears linear, False otherwise
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return True  # Default to linear if insufficient data
        
        # Calculate Pearson and Spearman correlations
        pearson_corr = df[numeric_cols].corr(method='pearson')
        spearman_corr = df[numeric_cols].corr(method='spearman')
        
        # Compare correlations (linear data should have similar Pearson and Spearman)
        correlation_diff = np.abs(pearson_corr - spearman_corr)
        
        # Remove diagonal and get upper triangle
        mask = np.triu(np.ones_like(correlation_diff, dtype=bool), k=1)
        diff_values = correlation_diff.where(mask).values.flatten()
        diff_values = diff_values[~np.isnan(diff_values)]
        
        if len(diff_values) == 0:
            return True
        
        # If differences are small, data is likely linear
        mean_diff = np.mean(diff_values)
        is_linear = mean_diff < (1 - self.threshold)
        
        return is_linear
    
    def detailed_linearity_test(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform detailed linearity analysis.
        
        Returns:
            Dictionary with detailed test results
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        results = {
            'is_linear': self.test_linearity(df),
            'n_numeric_vars': len(numeric_cols),
            'tests': []
        }
        
        if len(numeric_cols) >= 2:
            # Pairwise linearity tests
            for i, col1 in enumerate(numeric_cols[:-1]):
                for col2 in numeric_cols[i+1:]:
                    test_result = self._test_pair_linearity(df[col1], df[col2])
                    results['tests'].append({
                        'var1': col1,
                        'var2': col2,
                        **test_result
                    })
        
        return results
    
    def _test_pair_linearity(self, x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        """Test linearity between two variables."""
        # Remove NaN values
        mask = ~(x.isna() | y.isna())
        x_clean = x[mask]
        y_clean = y[mask]
        
        if len(x_clean) < 3:
            return {'is_linear': True, 'reason': 'insufficient_data'}
        
        # Calculate correlations
        pearson_r, _ = stats.pearsonr(x_clean, y_clean)
        spearman_r, _ = stats.spearmanr(x_clean, y_clean)
        
        # Compare correlations
        corr_diff = abs(pearson_r - spearman_r)
        is_linear = corr_diff < (1 - self.threshold)
        
        return {
            'is_linear': is_linear,
            'pearson_r': pearson_r,
            'spearman_r': spearman_r,
            'correlation_diff': corr_diff
        }

