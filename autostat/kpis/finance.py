"""
Finance KPIs

Metrics for financial performance analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class FinanceKPIs:
    """
    Finance-specific KPI calculations.

    KPIs:
    - Gross Profit Margin
    - Net Profit Margin
    - Operating Margin
    - Revenue Growth
    - EBITDA Margin
    """

    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all applicable finance KPIs."""
        results = []

        if self._has_gross_margin_data(df):
            results.append(self.gross_profit_margin(df))

        if self._has_net_margin_data(df):
            results.append(self.net_profit_margin(df))

        if self._has_revenue_growth_data(df):
            results.append(self.revenue_growth(df))

        return results

    def gross_profit_margin(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Gross Profit Margin.

        Formula: ((Revenue - COGS) / Revenue) * 100
        """
        revenue = self._find_column(df, ['revenue', 'sales', 'income'])
        cogs = self._find_column(df, ['cogs', 'cost_of_goods', 'cost_of_sales'])

        if revenue is None or cogs is None:
            return {'kpi': 'Gross Profit Margin', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_revenue = df[revenue].sum()
        total_cogs = df[cogs].sum()

        if total_revenue == 0:
            margin = 0
        else:
            margin = ((total_revenue - total_cogs) / total_revenue) * 100

        return {
            'kpi': 'Gross Profit Margin',
            'value': round(margin, 2),
            'unit': '%',
            'total_revenue': total_revenue,
            'total_cogs': total_cogs,
            'gross_profit': total_revenue - total_cogs
        }

    def net_profit_margin(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Net Profit Margin.

        Formula: (Net Profit / Revenue) * 100
        """
        revenue = self._find_column(df, ['revenue', 'sales', 'income'])
        net_profit = self._find_column(df, ['net_profit', 'net_income', 'profit'])

        if revenue is None or net_profit is None:
            # Try to calculate from revenue and expenses
            expenses = self._find_column(df, ['expenses', 'costs', 'total_expenses'])
            if revenue and expenses:
                total_revenue = df[revenue].sum()
                total_expenses = df[expenses].sum()
                calculated_profit = total_revenue - total_expenses

                if total_revenue == 0:
                    margin = 0
                else:
                    margin = (calculated_profit / total_revenue) * 100

                return {
                    'kpi': 'Net Profit Margin',
                    'value': round(margin, 2),
                    'unit': '%',
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'net_profit': calculated_profit
                }
            else:
                return {'kpi': 'Net Profit Margin', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_revenue = df[revenue].sum()
        total_profit = df[net_profit].sum()

        if total_revenue == 0:
            margin = 0
        else:
            margin = (total_profit / total_revenue) * 100

        return {
            'kpi': 'Net Profit Margin',
            'value': round(margin, 2),
            'unit': '%',
            'total_revenue': total_revenue,
            'net_profit': total_profit
        }

    def revenue_growth(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Revenue Growth Rate.

        Formula: ((Current Period - Previous Period) / Previous Period) * 100
        """
        revenue = self._find_column(df, ['revenue', 'sales', 'income'])

        if revenue is None or len(df) < 2:
            return {'kpi': 'Revenue Growth', 'value': None, 'unit': '%', 'error': 'Missing data'}

        # Calculate growth between first half and second half
        first_half = df[revenue].iloc[:len(df)//2].sum()
        second_half = df[revenue].iloc[len(df)//2:].sum()

        if first_half == 0:
            growth = 0
        else:
            growth = ((second_half - first_half) / first_half) * 100

        return {
            'kpi': 'Revenue Growth',
            'value': round(growth, 2),
            'unit': '%',
            'first_period_revenue': first_half,
            'second_period_revenue': second_half
        }

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
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

