"""
Product KPIs

Metrics for product quality and performance.
Calculates KPIs per observation for time series, panel, and cross-sectional data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class ProductKPIs:
    """
    Product-specific KPI calculations.

    Calculates per-observation KPIs:
    - Yield Rate (per period)
    - Defect Rate (per period)
    - Scrap Rate (per period)
    """

    def calculate_all(self, df: pd.DataFrame, data_type: str = 'time_series') -> List[Dict[str, Any]]:
        """Calculate all applicable product KPIs per observation."""
        results = []

        if self._has_yield_data(df):
            results.append(self.yield_rate(df, data_type))

        if self._has_defect_data(df):
            results.append(self.defect_rate(df, data_type))

        if self._has_scrap_data(df):
            results.append(self.scrap_rate(df, data_type))

        return results

    def _calculate_summary_stats(self, series: pd.Series, kpi_name: str, unit: str) -> Dict[str, Any]:
        """Calculate summary statistics for a KPI series."""
        clean_series = series.replace([np.inf, -np.inf], np.nan).dropna()

        if len(clean_series) == 0:
            return {
                'kpi': kpi_name, 'unit': unit, 'series': series,
                'mean': None, 'median': None, 'std': None,
                'min': None, 'max': None, 'n_observations': 0,
                'error': 'No valid observations'
            }

        return {
            'kpi': kpi_name, 'unit': unit, 'series': series,
            'mean': round(clean_series.mean(), 2),
            'median': round(clean_series.median(), 2),
            'std': round(clean_series.std(), 2),
            'min': round(clean_series.min(), 2),
            'max': round(clean_series.max(), 2),
            'n_observations': len(clean_series),
            'current': round(clean_series.iloc[-1], 2) if len(clean_series) > 0 else None
        }

    def yield_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate yield rate per observation.

        Formula: (Good Units / Total Units) * 100 for each row
        """
        good_col = self._find_column(df, ['good_units', 'passed', 'accepted'])
        total_col = self._find_column(df, ['total_units', 'produced', 'output'])

        if good_col is None or total_col is None:
            return {'kpi': 'Yield Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = (df[good_col] / df[total_col].replace(0, np.nan)) * 100
        series.name = 'yield_rate'

        return self._calculate_summary_stats(series, 'Yield Rate', '%')

    def defect_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate defect rate per observation.

        Formula: (Defective Units / Total Units) * 100 for each row
        """
        defects_col = self._find_column(df, ['defects', 'defective', 'rejected', 'failed'])
        total_col = self._find_column(df, ['total_units', 'produced', 'output'])

        if defects_col is None or total_col is None:
            return {'kpi': 'Defect Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = (df[defects_col] / df[total_col].replace(0, np.nan)) * 100
        series.name = 'defect_rate'

        return self._calculate_summary_stats(series, 'Defect Rate', '%')

    def scrap_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate scrap rate per observation.

        Formula: (Scrapped Units / Total Units) * 100 for each row
        """
        scrap_col = self._find_column(df, ['scrap', 'scrapped', 'waste'])
        total_col = self._find_column(df, ['total_units', 'produced', 'output'])

        if scrap_col is None or total_col is None:
            return {'kpi': 'Scrap Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = (df[scrap_col] / df[total_col].replace(0, np.nan)) * 100
        series.name = 'scrap_rate'

        return self._calculate_summary_stats(series, 'Scrap Rate', '%')

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
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

