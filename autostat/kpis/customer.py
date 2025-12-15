"""
Customer KPIs

Metrics for customer satisfaction and retention.
Calculates KPIs per observation for time series, panel, and cross-sectional data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class CustomerKPIs:
    """
    Customer-specific KPI calculations.

    Calculates per-observation KPIs:
    - Customer Satisfaction Score (CSAT) (per period)
    - NPS (per period)
    - Churn Rate (per period)
    - Customer Growth Rate (period-over-period)
    """

    def calculate_all(self, df: pd.DataFrame, data_type: str = 'time_series') -> List[Dict[str, Any]]:
        """Calculate all applicable customer KPIs per observation."""
        results = []

        if self._has_satisfaction_data(df):
            results.append(self.customer_satisfaction(df, data_type))

        if self._has_nps_data(df):
            results.append(self.nps_score(df, data_type))

        if self._has_churn_data(df):
            results.append(self.churn_rate(df, data_type))

        if self._has_growth_data(df):
            results.append(self.customer_growth(df, data_type))

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

    def customer_satisfaction(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Customer Satisfaction Score per observation.

        This is already a per-observation metric (each row has a score).
        """
        satisfaction_col = self._find_column(df, ['satisfaction', 'csat', 'satisfaction_score'])

        if satisfaction_col is None:
            return {'kpi': 'CSAT', 'value': None, 'unit': 'score', 'error': 'Missing data'}

        series = df[satisfaction_col].copy()
        series.name = 'csat'

        return self._calculate_summary_stats(series, 'Customer Satisfaction (CSAT)', 'score')

    def nps_score(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Net Promoter Score per observation.

        This is already a per-observation metric.
        """
        nps_col = self._find_column(df, ['nps', 'net_promoter'])

        if nps_col is None:
            return {'kpi': 'NPS', 'value': None, 'unit': 'score', 'error': 'Missing data'}

        series = df[nps_col].copy()
        series.name = 'nps'

        return self._calculate_summary_stats(series, 'Net Promoter Score (NPS)', 'score')

    def churn_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Churn Rate per observation.

        This is already a per-observation metric if provided directly.
        """
        churn_col = self._find_column(df, ['churn_rate', 'churn', 'attrition'])

        if churn_col is None:
            return {'kpi': 'Churn Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = df[churn_col].copy()
        series.name = 'churn_rate'

        return self._calculate_summary_stats(series, 'Churn Rate', '%')

    def customer_growth(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Customer Growth Rate per observation (period-over-period).

        Formula: ((Current - Previous) / Previous) * 100
        """
        customers_col = self._find_column(df, ['active_customers', 'customers', 'total_customers'])

        if customers_col is None or len(df) < 2:
            return {'kpi': 'Customer Growth', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = df[customers_col].pct_change() * 100
        series.name = 'customer_growth'

        return self._calculate_summary_stats(series, 'Customer Growth Rate', '%')

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None

    def _has_satisfaction_data(self, df: pd.DataFrame) -> bool:
        """Check if satisfaction data is available."""
        return self._find_column(df, ['satisfaction', 'csat', 'satisfaction_score']) is not None

    def _has_nps_data(self, df: pd.DataFrame) -> bool:
        """Check if NPS data is available."""
        return self._find_column(df, ['nps', 'net_promoter']) is not None

    def _has_churn_data(self, df: pd.DataFrame) -> bool:
        """Check if churn data is available."""
        return self._find_column(df, ['churn_rate', 'churn', 'attrition']) is not None

    def _has_growth_data(self, df: pd.DataFrame) -> bool:
        """Check if customer growth data is available."""
        return self._find_column(df, ['active_customers', 'customers', 'total_customers']) is not None

