"""
Production KPIs

Metrics for production and manufacturing performance analysis.
Calculates KPIs per observation for time series, panel, and cross-sectional data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class ProductionKPIs:
    """
    Production-specific KPI calculations.

    Calculates per-observation KPIs:
    - Production Volume (per period)
    - Production Efficiency (OEE) (per period)
    - Capacity Utilization (per period)
    - Yield Rate (per period)
    - Scrap Rate (per period)
    - Downtime Percentage (per period)
    """

    def calculate_all(self, df: pd.DataFrame, data_type: str = 'time_series') -> List[Dict[str, Any]]:
        """Calculate all applicable production KPIs per observation."""
        results = []

        # Try to calculate each KPI
        if self._has_volume_data(df):
            results.append(self.production_volume(df, data_type))

        if self._has_efficiency_data(df):
            results.append(self.production_efficiency(df, data_type))

        if self._has_utilization_data(df):
            results.append(self.capacity_utilization(df, data_type))

        if self._has_downtime_data(df):
            results.append(self.downtime_percentage(df, data_type))

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

    def production_volume(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate production volume per observation.

        Formula: Units produced per period
        """
        volume_col = self._find_column(df, ['units_produced', 'production_volume', 'output', 'units', 'quantity_produced'])

        if volume_col is None:
            return {'kpi': 'Production Volume', 'value': None, 'unit': 'units', 'error': 'Missing data'}

        series = df[volume_col].copy()
        series.name = 'production_volume'

        return self._calculate_summary_stats(series, 'Production Volume', 'units')

    def production_efficiency(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate OEE per observation.

        Formula: (Actual Output / Theoretical Maximum Output) * 100 per period
        """
        actual_col = self._find_column(df, ['units_produced', 'actual_output', 'output', 'units'])
        max_col = self._find_column(df, ['capacity', 'max_output', 'planned_output', 'theoretical_output'])

        if actual_col is None or max_col is None:
            prod_hours = self._find_column(df, ['production_hours', 'actual_hours', 'working_hours'])
            planned_hours = self._find_column(df, ['planned_time', 'planned_hours', 'available_time'])

            if prod_hours is not None and planned_hours is not None:
                series = (df[prod_hours] / df[planned_hours].replace(0, np.nan)) * 100
                series.name = 'production_efficiency'
                return self._calculate_summary_stats(series, 'Production Efficiency', '%')

            return {'kpi': 'Production Efficiency', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = (df[actual_col] / df[max_col].replace(0, np.nan)) * 100
        series.name = 'production_efficiency'

        return self._calculate_summary_stats(series, 'Production Efficiency', '%')

    def capacity_utilization(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Capacity Utilization per observation.

        Formula: (Actual Production / Maximum Capacity) * 100 per period
        """
        utilization_col = self._find_column(df, ['utilization', 'capacity_utilization', 'utilization_rate'])

        if utilization_col is not None:
            series = df[utilization_col].copy()
            series.name = 'capacity_utilization'
            return self._calculate_summary_stats(series, 'Capacity Utilization', '%')

        uptime_col = self._find_column(df, ['uptime', 'operating_time', 'run_time'])
        planned_col = self._find_column(df, ['planned_time', 'available_time', 'scheduled_time'])

        if uptime_col is not None and planned_col is not None:
            series = (df[uptime_col] / df[planned_col].replace(0, np.nan)) * 100
            series.name = 'capacity_utilization'
            return self._calculate_summary_stats(series, 'Capacity Utilization', '%')

        return {'kpi': 'Capacity Utilization', 'value': None, 'unit': '%', 'error': 'Missing data'}

    def downtime_percentage(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Downtime Percentage per observation.

        Formula: (Downtime / Total Available Time) * 100 per period
        """
        downtime_col = self._find_column(df, ['downtime', 'unplanned_downtime', 'maintenance_time'])
        total_col = self._find_column(df, ['planned_time', 'available_time', 'total_time'])

        if downtime_col is None or total_col is None:
            return {'kpi': 'Downtime Percentage', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = (df[downtime_col] / df[total_col].replace(0, np.nan)) * 100
        series.name = 'downtime_percentage'

        return self._calculate_summary_stats(series, 'Downtime Percentage', '%')

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None

    def _has_volume_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['units_produced', 'production_volume', 'output']) is not None

    def _has_efficiency_data(self, df: pd.DataFrame) -> bool:
        has_output = self._find_column(df, ['units_produced', 'actual_output']) is not None
        has_capacity = self._find_column(df, ['capacity', 'max_output', 'planned_output']) is not None
        has_hours = self._find_column(df, ['production_hours']) is not None and \
                    self._find_column(df, ['planned_time']) is not None
        return (has_output and has_capacity) or has_hours

    def _has_utilization_data(self, df: pd.DataFrame) -> bool:
        has_direct = self._find_column(df, ['utilization', 'capacity_utilization']) is not None
        has_calculated = self._find_column(df, ['uptime']) is not None and \
                        self._find_column(df, ['planned_time']) is not None
        return has_direct or has_calculated

    def _has_downtime_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['downtime', 'unplanned_downtime']) is not None

