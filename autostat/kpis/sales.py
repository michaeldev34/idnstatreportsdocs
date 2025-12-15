"""
Sales KPIs

Metrics for sales performance analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class SalesKPIs:
    """
    Sales-specific KPI calculations.

    KPIs:
    - Average Order Value (AOV)
    - Sales Growth Rate
    - Win Rate
    - Average Deal Size
    - Sales per Rep
    """

    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all applicable sales KPIs."""
        results = []

        if self._has_aov_data(df):
            results.append(self.average_order_value(df))

        if self._has_growth_data(df):
            results.append(self.sales_growth_rate(df))

        if self._has_win_rate_data(df):
            results.append(self.win_rate(df))

        return results

    def average_order_value(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Average Order Value.

        Formula: Total Revenue / Number of Orders
        """
        revenue = self._find_column(df, ['revenue', 'sales', 'total_sales'])
        orders = self._find_column(df, ['orders', 'transactions', 'deals'])

        if revenue is None or orders is None:
            return {'kpi': 'Average Order Value', 'value': None, 'unit': '$', 'error': 'Missing data'}

        total_revenue = df[revenue].sum()
        total_orders = df[orders].sum()

        if total_orders == 0:
            aov = 0
        else:
            aov = total_revenue / total_orders

        return {
            'kpi': 'Average Order Value',
            'value': round(aov, 2),
            'unit': '$',
            'total_revenue': total_revenue,
            'total_orders': total_orders
        }

    def sales_growth_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Sales Growth Rate.

        Formula: ((Current Period - Previous Period) / Previous Period) * 100
        """
        sales = self._find_column(df, ['sales', 'revenue', 'total_sales'])

        if sales is None or len(df) < 2:
            return {'kpi': 'Sales Growth Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        # Calculate growth between first and last period
        first_period = df[sales].iloc[:len(df)//2].sum()
        last_period = df[sales].iloc[len(df)//2:].sum()

        if first_period == 0:
            growth = 0
        else:
            growth = ((last_period - first_period) / first_period) * 100

        return {
            'kpi': 'Sales Growth Rate',
            'value': round(growth, 2),
            'unit': '%',
            'first_period_sales': first_period,
            'last_period_sales': last_period
        }

    def win_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Win Rate.

        Formula: (Deals Won / Total Opportunities) * 100
        """
        won = self._find_column(df, ['won', 'deals_won', 'closed_won'])
        opportunities = self._find_column(df, ['opportunities', 'leads', 'prospects'])

        if won is None or opportunities is None:
            return {'kpi': 'Win Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_won = df[won].sum()
        total_opportunities = df[opportunities].sum()

        if total_opportunities == 0:
            rate = 0
        else:
            rate = (total_won / total_opportunities) * 100

        return {
            'kpi': 'Win Rate',
            'value': round(rate, 2),
            'unit': '%',
            'total_won': total_won,
            'total_opportunities': total_opportunities
        }

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
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

