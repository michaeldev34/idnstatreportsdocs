"""
Scaling Handler

Handles data normalization and scaling.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class ScalingHandler:
    """
    Handles data scaling and normalization.
    
    Methods:
    - StandardScaler (z-score normalization)
    - MinMaxScaler (0-1 normalization)
    - RobustScaler (median and IQR)
    """
    
    def __init__(self, method: str = 'standard'):
        """
        Args:
            method: 'standard', 'minmax', or 'robust'
        """
        self.method = method
        self.scaling_params = {}
    
    def scale(self, df: pd.DataFrame, method: Optional[str] = None) -> pd.DataFrame:
        """
        Scale numeric columns.
        
        Args:
            df: Input DataFrame
            method: Override default scaling method
            
        Returns:
            Scaled DataFrame
        """
        method = method or self.method
        df_scaled = df.copy()
        
        numeric_cols = df_scaled.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if method == 'standard':
                df_scaled[col] = self._standard_scale(df_scaled[col], col)
            elif method == 'minmax':
                df_scaled[col] = self._minmax_scale(df_scaled[col], col)
            elif method == 'robust':
                df_scaled[col] = self._robust_scale(df_scaled[col], col)
        
        return df_scaled
    
    def _standard_scale(self, series: pd.Series, col_name: str) -> pd.Series:
        """Standard scaling (z-score)."""
        mean = series.mean()
        std = series.std()
        
        self.scaling_params[col_name] = {'mean': mean, 'std': std, 'method': 'standard'}
        
        if std == 0:
            return series - mean
        return (series - mean) / std
    
    def _minmax_scale(self, series: pd.Series, col_name: str) -> pd.Series:
        """Min-Max scaling to [0, 1]."""
        min_val = series.min()
        max_val = series.max()
        
        self.scaling_params[col_name] = {'min': min_val, 'max': max_val, 'method': 'minmax'}
        
        if max_val == min_val:
            return series - min_val
        return (series - min_val) / (max_val - min_val)
    
    def _robust_scale(self, series: pd.Series, col_name: str) -> pd.Series:
        """Robust scaling using median and IQR."""
        median = series.median()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        
        self.scaling_params[col_name] = {'median': median, 'iqr': iqr, 'method': 'robust'}
        
        if iqr == 0:
            return series - median
        return (series - median) / iqr
    
    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reverse scaling transformation.
        
        Args:
            df: Scaled DataFrame
            
        Returns:
            Original scale DataFrame
        """
        df_original = df.copy()
        
        for col, params in self.scaling_params.items():
            if col not in df_original.columns:
                continue
            
            method = params['method']
            
            if method == 'standard':
                df_original[col] = df_original[col] * params['std'] + params['mean']
            elif method == 'minmax':
                df_original[col] = df_original[col] * (params['max'] - params['min']) + params['min']
            elif method == 'robust':
                df_original[col] = df_original[col] * params['iqr'] + params['median']
        
        return df_original

