"""
Sales KPIs

Metrics for sales performance analysis.
Calculates KPIs per observation for time series, panel, and cross-sectional data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class SalesKPIs:
    """
    Sales-specific KPI calculations.

    Calculates per-observation KPIs:
    - Average Order Value (AOV) (per period)
    - Sales Growth Rate (period-over-period)
    - Win Rate (per period)
    - Revenue per Order (per period)
    """

    def calculate_all(self, df: pd.DataFrame, data_type: str = 'time_series') -> List[Dict[str, Any]]:
        """Calculate all applicable sales KPIs per observation."""
        results = []

        if self._has_aov_data(df):
            results.append(self.average_order_value(df, data_type))

        if self._has_growth_data(df):
            results.append(self.sales_growth_rate(df, data_type))

        if self._has_win_rate_data(df):
            results.append(self.win_rate(df, data_type))

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

    def average_order_value(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Average Order Value per observation.

        Formula: Revenue / Orders for each row
        """
        revenue_col = self._find_column(df, ['revenue', 'sales', 'total_sales'])
        orders_col = self._find_column(df, ['orders', 'transactions', 'deals'])

        if revenue_col is None or orders_col is None:
            return {'kpi': 'Average Order Value', 'value': None, 'unit': '$', 'error': 'Missing data'}

        # Calculate per-observation AOV
        series = df[revenue_col] / df[orders_col].replace(0, np.nan)
        series.name = 'aov'

        return self._calculate_summary_stats(series, 'Average Order Value (AOV)', '$')

    def sales_growth_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Sales Growth Rate per observation (period-over-period).

        Formula: ((Current - Previous) / Previous) * 100 for each row
        """
        sales_col = self._find_column(df, ['sales', 'revenue', 'total_sales'])

        if sales_col is None or len(df) < 2:
            return {'kpi': 'Sales Growth Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        # Calculate period-over-period growth
        series = df[sales_col].pct_change() * 100
        series.name = 'sales_growth'

        return self._calculate_summary_stats(series, 'Sales Growth Rate', '%')

    def win_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Win Rate per observation.

        Formula: (Deals Won / Opportunities) * 100 for each row
        """
        won_col = self._find_column(df, ['won', 'deals_won', 'closed_won'])
        opps_col = self._find_column(df, ['opportunities', 'leads', 'prospects'])

        if won_col is None or opps_col is None:
            return {'kpi': 'Win Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        # Calculate per-observation win rate
        series = (df[won_col] / df[opps_col].replace(0, np.nan)) * 100
        series.name = 'win_rate'

        return self._calculate_summary_stats(series, 'Win Rate', '%')

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None

    def _has_aov_data(self, df: pd.DataFrame) -> bool:
        """Check if AOV data is available."""
        return (self._find_column(df, ['revenue', 'sales']) is not None and
                self._find_column(df, ['orders', 'transactions']) is not None)

    def _has_growth_data(self, df: pd.DataFrame) -> bool:
        """Check if growth data is available."""
        return self._find_column(df, ['sales', 'revenue']) is not None

    def _has_win_rate_data(self, df: pd.DataFrame) -> bool:
        """Check if win rate data is available."""
        return (self._find_column(df, ['won', 'deals_won']) is not None and
                self._find_column(df, ['opportunities', 'leads']) is not None)

