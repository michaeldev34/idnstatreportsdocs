"""
Finance KPIs

Metrics for financial performance analysis.
Calculates KPIs per observation for time series, panel, and cross-sectional data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class FinanceKPIs:
    """
    Finance-specific KPI calculations.

    Calculates per-observation KPIs:
    - Gross Profit Margin (per period)
    - Net Profit Margin (per period)
    - Revenue Growth (period-over-period)
    - Operating Expense Ratio (per period)
    """

    def calculate_all(self, df: pd.DataFrame, data_type: str = 'time_series') -> List[Dict[str, Any]]:
        """Calculate all applicable finance KPIs per observation."""
        results = []

        if self._has_gross_margin_data(df):
            results.append(self.gross_profit_margin(df, data_type))

        if self._has_net_margin_data(df):
            results.append(self.net_profit_margin(df, data_type))

        if self._has_revenue_growth_data(df):
            results.append(self.revenue_growth(df, data_type))

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

    def gross_profit_margin(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Gross Profit Margin per observation.

        Formula: ((Revenue - COGS) / Revenue) * 100 for each row
        """
        revenue_col = self._find_column(df, ['revenue', 'sales', 'income'])
        cogs_col = self._find_column(df, ['cogs', 'cost_of_goods', 'cost_of_sales'])

        if revenue_col is None or cogs_col is None:
            return {'kpi': 'Gross Profit Margin', 'value': None, 'unit': '%', 'error': 'Missing data'}

        # Calculate per-observation gross margin
        series = ((df[revenue_col] - df[cogs_col]) / df[revenue_col].replace(0, np.nan)) * 100
        series.name = 'gross_margin'

        return self._calculate_summary_stats(series, 'Gross Profit Margin', '%')

    def net_profit_margin(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Net Profit Margin per observation.

        Formula: (Net Profit / Revenue) * 100 for each row
        """
        revenue_col = self._find_column(df, ['revenue', 'sales', 'income'])
        profit_col = self._find_column(df, ['net_profit', 'net_income', 'profit'])

        if revenue_col is None:
            return {'kpi': 'Net Profit Margin', 'value': None, 'unit': '%', 'error': 'Missing data'}

        if profit_col is not None:
            # Direct profit column available
            series = (df[profit_col] / df[revenue_col].replace(0, np.nan)) * 100
        else:
            # Calculate profit from revenue - expenses
            expenses_col = self._find_column(df, ['expenses', 'costs', 'total_expenses'])
            if expenses_col is None:
                return {'kpi': 'Net Profit Margin', 'value': None, 'unit': '%', 'error': 'Missing data'}
            series = ((df[revenue_col] - df[expenses_col]) / df[revenue_col].replace(0, np.nan)) * 100

        series.name = 'net_margin'
        return self._calculate_summary_stats(series, 'Net Profit Margin', '%')

    def revenue_growth(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Revenue Growth Rate per observation (period-over-period).

        Formula: ((Current - Previous) / Previous) * 100 for each row
        """
        revenue_col = self._find_column(df, ['revenue', 'sales', 'income'])

        if revenue_col is None or len(df) < 2:
            return {'kpi': 'Revenue Growth', 'value': None, 'unit': '%', 'error': 'Missing data'}

        # Calculate period-over-period growth
        series = df[revenue_col].pct_change() * 100
        series.name = 'revenue_growth'

        return self._calculate_summary_stats(series, 'Revenue Growth', '%')

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None

    def _has_gross_margin_data(self, df: pd.DataFrame) -> bool:
        """Check if gross margin data is available."""
        return (self._find_column(df, ['revenue', 'sales']) is not None and
                self._find_column(df, ['cogs', 'cost_of_goods']) is not None)

    def _has_net_margin_data(self, df: pd.DataFrame) -> bool:
        """Check if net margin data is available."""
        revenue = self._find_column(df, ['revenue', 'sales'])
        profit = self._find_column(df, ['net_profit', 'profit'])
        expenses = self._find_column(df, ['expenses', 'costs'])
        return revenue is not None and (profit is not None or expenses is not None)

    def _has_revenue_growth_data(self, df: pd.DataFrame) -> bool:
        """Check if revenue growth data is available."""
        return self._find_column(df, ['revenue', 'sales']) is not None

