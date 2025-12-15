"""
Operations KPIs

Metrics for operational efficiency and performance.
Calculates KPIs per observation for time series, panel, and cross-sectional data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class OperationsKPIs:
    """
    Operations-specific KPI calculations.

    Calculates per-observation KPIs:
    - Uptime/Availability (per period)
    - Units per Hour (per period)
    - Capacity Utilization (per period)
    - Production Efficiency (per period)
    """

    def calculate_all(self, df: pd.DataFrame, data_type: str = 'time_series') -> List[Dict[str, Any]]:
        """Calculate all applicable operations KPIs per observation."""
        results = []

        if self._has_uptime_data(df):
            results.append(self.uptime_rate(df, data_type))

        if self._has_production_data(df):
            results.append(self.units_per_hour(df, data_type))

        if self._has_capacity_data(df):
            results.append(self.capacity_utilization(df, data_type))

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

    def uptime_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Uptime/Availability per observation.

        This is already a per-observation metric.
        """
        uptime_col = self._find_column(df, ['uptime', 'availability', 'uptime_pct'])

        if uptime_col is None:
            return {'kpi': 'Uptime', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = df[uptime_col].copy()
        series.name = 'uptime'

        return self._calculate_summary_stats(series, 'Uptime/Availability', '%')

    def units_per_hour(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Units per Hour per observation.

        Formula: Units Produced / Hours for each row
        """
        units_col = self._find_column(df, ['units_produced', 'units', 'production', 'output'])
        hours_col = self._find_column(df, ['production_hours', 'hours', 'time'])

        if units_col is None or hours_col is None:
            return {'kpi': 'Units per Hour', 'value': None, 'unit': 'units/hr', 'error': 'Missing data'}

        series = df[units_col] / df[hours_col].replace(0, np.nan)
        series.name = 'units_per_hour'

        return self._calculate_summary_stats(series, 'Units per Hour', 'units/hr')

    def capacity_utilization(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Capacity Utilization per observation.

        Formula: (Actual Output / Max Capacity) * 100 for each row
        """
        actual_col = self._find_column(df, ['units_produced', 'actual_output', 'production'])
        capacity_col = self._find_column(df, ['capacity', 'max_capacity', 'planned_output'])

        if actual_col is None or capacity_col is None:
            # Try alternative: uptime / planned_time
            uptime_col = self._find_column(df, ['uptime', 'operating_time'])
            planned_col = self._find_column(df, ['planned_time', 'available_time'])

            if uptime_col is not None and planned_col is not None:
                series = (df[uptime_col] / df[planned_col].replace(0, np.nan)) * 100
                series.name = 'capacity_util'
                return self._calculate_summary_stats(series, 'Capacity Utilization', '%')

            return {'kpi': 'Capacity Utilization', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = (df[actual_col] / df[capacity_col].replace(0, np.nan)) * 100
        series.name = 'capacity_util'

        return self._calculate_summary_stats(series, 'Capacity Utilization', '%')

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None

    def _has_uptime_data(self, df: pd.DataFrame) -> bool:
        """Check if uptime data is available."""
        return self._find_column(df, ['uptime', 'availability']) is not None

    def _has_production_data(self, df: pd.DataFrame) -> bool:
        """Check if production rate data is available."""
        return (self._find_column(df, ['units_produced', 'units', 'production']) is not None and
                self._find_column(df, ['production_hours', 'hours', 'time']) is not None)

    def _has_capacity_data(self, df: pd.DataFrame) -> bool:
        """Check if capacity data is available."""
        return ((self._find_column(df, ['units_produced', 'actual_output']) is not None and
                 self._find_column(df, ['capacity', 'max_capacity']) is not None) or
                (self._find_column(df, ['uptime']) is not None and
                 self._find_column(df, ['planned_time']) is not None))

