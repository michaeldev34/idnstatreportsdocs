"""
Legal & Compliance KPIs

Metrics for legal department and compliance performance analysis.
Calculates KPIs per observation for time series, panel, and cross-sectional data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class LegalKPIs:
    """
    Legal-specific KPI calculations.

    Calculates per-observation KPIs:
    - Contract Compliance Rate (per period)
    - Dispute Resolution Time (per period)
    - Legal Cost per Case (per period)
    - Contract Cycle Time (per period)
    - Open Cases Count (per period)
    - Settlement Rate (per period)
    """

    def calculate_all(self, df: pd.DataFrame, data_type: str = 'time_series') -> List[Dict[str, Any]]:
        """Calculate all applicable legal KPIs per observation."""
        results = []

        if self._has_compliance_data(df):
            results.append(self.contract_compliance_rate(df, data_type))

        if self._has_resolution_data(df):
            results.append(self.dispute_resolution_time(df, data_type))

        if self._has_cost_data(df):
            results.append(self.legal_cost_per_case(df, data_type))

        if self._has_cycle_data(df):
            results.append(self.contract_cycle_time(df, data_type))

        if self._has_cases_data(df):
            results.append(self.open_cases_count(df, data_type))

        if self._has_settlement_data(df):
            results.append(self.settlement_rate(df, data_type))

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

    def contract_compliance_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Contract Compliance Rate per observation.

        Formula: (Compliant Contracts / Total Contracts) * 100 per period
        """
        compliant_col = self._find_column(df, ['compliant_contracts', 'compliant', 'contracts_compliant'])
        total_col = self._find_column(df, ['total_contracts', 'contracts', 'contract_count'])

        if compliant_col is None or total_col is None:
            return {'kpi': 'Contract Compliance Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = (df[compliant_col] / df[total_col].replace(0, np.nan)) * 100
        series.name = 'contract_compliance_rate'

        return self._calculate_summary_stats(series, 'Contract Compliance Rate', '%')

    def dispute_resolution_time(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Dispute Resolution Time per observation.

        Formula: Days to resolve disputes per period
        """
        time_col = self._find_column(df, ['resolution_time', 'dispute_days', 'time_to_resolve', 'case_duration'])

        if time_col is None:
            return {'kpi': 'Dispute Resolution Time', 'value': None, 'unit': 'days', 'error': 'Missing data'}

        series = df[time_col].copy()
        series.name = 'dispute_resolution_time'

        return self._calculate_summary_stats(series, 'Dispute Resolution Time', 'days')

    def legal_cost_per_case(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Legal Cost per Case per observation.

        Formula: Legal Costs / Number of Cases per period
        """
        cost_col = self._find_column(df, ['legal_cost', 'legal_fees', 'case_cost', 'legal_expenses'])
        cases_col = self._find_column(df, ['cases', 'case_count', 'disputes', 'legal_cases'])

        if cost_col is None:
            return {'kpi': 'Legal Cost per Case', 'value': None, 'unit': '$', 'error': 'Missing data'}

        if cases_col is not None:
            series = df[cost_col] / df[cases_col].replace(0, np.nan)
        else:
            series = df[cost_col].copy()

        series.name = 'legal_cost_per_case'

        return self._calculate_summary_stats(series, 'Legal Cost per Case', '$')

    def contract_cycle_time(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Contract Cycle Time per observation.

        Formula: Days from contract initiation to signature per period
        """
        cycle_col = self._find_column(df, ['cycle_time', 'contract_days', 'time_to_sign', 'contract_cycle'])

        if cycle_col is None:
            return {'kpi': 'Contract Cycle Time', 'value': None, 'unit': 'days', 'error': 'Missing data'}

        series = df[cycle_col].copy()
        series.name = 'contract_cycle_time'

        return self._calculate_summary_stats(series, 'Contract Cycle Time', 'days')

    def open_cases_count(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Open/Active Legal Cases per observation.
        """
        cases_col = self._find_column(df, ['open_cases', 'active_cases', 'pending_cases'])

        if cases_col is None:
            return {'kpi': 'Open Cases', 'value': None, 'unit': 'cases', 'error': 'Missing data'}

        series = df[cases_col].copy()
        series.name = 'open_cases'

        return self._calculate_summary_stats(series, 'Open Cases', 'cases')

    def settlement_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Settlement Rate per observation.

        Formula: (Settled Cases / Total Resolved Cases) * 100 per period
        """
        settled_col = self._find_column(df, ['settlements', 'settled_cases', 'cases_settled'])
        total_col = self._find_column(df, ['resolved_cases', 'closed_cases', 'total_resolved'])

        if settled_col is None or total_col is None:
            return {'kpi': 'Settlement Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        series = (df[settled_col] / df[total_col].replace(0, np.nan)) * 100
        series.name = 'settlement_rate'

        return self._calculate_summary_stats(series, 'Settlement Rate', '%')

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None

    def _has_compliance_data(self, df: pd.DataFrame) -> bool:
        return (self._find_column(df, ['compliant_contracts', 'compliant']) is not None and
                self._find_column(df, ['total_contracts', 'contracts']) is not None)

    def _has_resolution_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['resolution_time', 'dispute_days', 'time_to_resolve']) is not None

    def _has_cost_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['legal_cost', 'legal_fees', 'case_cost']) is not None

    def _has_cycle_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['cycle_time', 'contract_days', 'time_to_sign']) is not None

    def _has_cases_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['open_cases', 'active_cases', 'pending_cases']) is not None

    def _has_settlement_data(self, df: pd.DataFrame) -> bool:
        return (self._find_column(df, ['settlements', 'settled_cases']) is not None and
                self._find_column(df, ['resolved_cases', 'closed_cases']) is not None)

