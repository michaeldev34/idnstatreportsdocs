"""
Missing Data Handler

Detects and handles missing data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class MissingDataHandler:
    """
    Handles missing data detection and imputation.
    
    Strategies:
    - Mean/median imputation for numeric data
    - Mode imputation for categorical data
    - Forward/backward fill for time series
    - Deletion for high missing percentage
    """
    
    def __init__(self, threshold: float = 0.5):
        """
        Args:
            threshold: Drop columns with missing % above this (default: 0.5)
        """
        self.threshold = threshold
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze missing data patterns.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with missing data analysis
        """
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        missing_pct = (missing_cells / total_cells) * 100
        
        # Per-column analysis
        column_missing = {}
        for col in df.columns:
            col_missing = df[col].isnull().sum()
            col_pct = (col_missing / len(df)) * 100
            if col_missing > 0:
                column_missing[col] = {
                    'count': int(col_missing),
                    'percentage': round(col_pct, 2)
                }
        
        return {
            'has_missing': missing_cells > 0,
            'total_missing': int(missing_cells),
            'missing_percentage': round(missing_pct, 2),
            'columns_with_missing': column_missing,
            'n_columns_affected': len(column_missing)
        }
    
    def handle(self, df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
        """
        Handle missing data.
        
        Args:
            df: Input DataFrame
            strategy: 'auto', 'drop', 'mean', 'median', 'mode', 'ffill', 'bfill'
            
        Returns:
            DataFrame with missing data handled
        """
        df_clean = df.copy()
        
        if strategy == 'auto':
            # Auto-select strategy based on data type and missing percentage
            for col in df_clean.columns:
                missing_pct = (df_clean[col].isnull().sum() / len(df_clean)) * 100
                
                if missing_pct > self.threshold * 100:
                    # Drop column if too much missing
                    df_clean = df_clean.drop(columns=[col])
                elif pd.api.types.is_numeric_dtype(df_clean[col]):
                    # Use median for numeric
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
                else:
                    # Use mode for categorical
                    mode_val = df_clean[col].mode()
                    if len(mode_val) > 0:
                        df_clean[col].fillna(mode_val[0], inplace=True)
        
        elif strategy == 'drop':
            df_clean = df_clean.dropna()
        
        elif strategy == 'mean':
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        
        elif strategy == 'median':
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
        
        elif strategy == 'mode':
            for col in df_clean.columns:
                mode_val = df_clean[col].mode()
                if len(mode_val) > 0:
                    df_clean[col].fillna(mode_val[0], inplace=True)
        
        elif strategy in ['ffill', 'bfill']:
            df_clean = df_clean.fillna(method=strategy)
        
        return df_clean

