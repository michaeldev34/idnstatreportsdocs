"""
Product KPIs

Metrics for product quality and performance.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class ProductKPIs:
    """
    Product-specific KPI calculations.
    
    KPIs:
    - Yield Rate
    - Defect Rate
    - First Pass Yield
    - Scrap Rate
    - Rework Rate
    """
    
    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all applicable product KPIs."""
        results = []
        
        if self._has_yield_data(df):
            results.append(self.yield_rate(df))
        
        if self._has_defect_data(df):
            results.append(self.defect_rate(df))
        
        if self._has_scrap_data(df):
            results.append(self.scrap_rate(df))
        
        return results
    
    def yield_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate yield rate.
        
        Formula: (Good Units / Total Units) * 100
        """
        good = self._find_column(df, ['good_units', 'passed', 'accepted'])
        total = self._find_column(df, ['total_units', 'produced', 'output'])
        
        if good is None or total is None:
            return {'kpi': 'Yield Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}
        
        total_good = df[good].sum()
        total_units = df[total].sum()
        
        if total_units == 0:
            rate = 0
        else:
            rate = (total_good / total_units) * 100
        
        return {
            'kpi': 'Yield Rate',
            'value': round(rate, 2),
            'unit': '%',
            'good_units': total_good,
            'total_units': total_units
        }
    
    def defect_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate defect rate.
        
        Formula: (Defective Units / Total Units) * 100
        """
        defects = self._find_column(df, ['defects', 'defective', 'rejected', 'failed'])
        total = self._find_column(df, ['total_units', 'produced', 'output'])
        
        if defects is None or total is None:
            return {'kpi': 'Defect Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}
        
        total_defects = df[defects].sum()
        total_units = df[total].sum()
        
        if total_units == 0:
            rate = 0
        else:
            rate = (total_defects / total_units) * 100
        
        return {
            'kpi': 'Defect Rate',
            'value': round(rate, 2),
            'unit': '%',
            'defective_units': total_defects,
            'total_units': total_units
        }
    
    def scrap_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate scrap rate.
        
        Formula: (Scrapped Units / Total Units) * 100
        """
        scrap = self._find_column(df, ['scrap', 'scrapped', 'waste'])
        total = self._find_column(df, ['total_units', 'produced', 'output'])
        
        if scrap is None or total is None:
            return {'kpi': 'Scrap Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}
        
        total_scrap = df[scrap].sum()
        total_units = df[total].sum()
        
        if total_units == 0:
            rate = 0
        else:
            rate = (total_scrap / total_units) * 100
        
        return {
            'kpi': 'Scrap Rate',
            'value': round(rate, 2),
            'unit': '%',
            'scrapped_units': total_scrap,
            'total_units': total_units
        }
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None
    
    def _has_yield_data(self, df: pd.DataFrame) -> bool:
        """Check if yield data is available."""
        return (self._find_column(df, ['good_units', 'passed']) is not None and
                self._find_column(df, ['total_units', 'produced']) is not None)
    
    def _has_defect_data(self, df: pd.DataFrame) -> bool:
        """Check if defect data is available."""
        return (self._find_column(df, ['defects', 'defective']) is not None and
                self._find_column(df, ['total_units', 'produced']) is not None)
    
    def _has_scrap_data(self, df: pd.DataFrame) -> bool:
        """Check if scrap data is available."""
        return (self._find_column(df, ['scrap', 'scrapped']) is not None and
                self._find_column(df, ['total_units', 'produced']) is not None)

