"""
Legal & Compliance KPIs

Metrics for legal department and compliance performance analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class LegalKPIs:
    """
    Legal-specific KPI calculations.

    KPIs:
    - Contract Compliance Rate
    - Dispute Resolution Time
    - Legal Cost per Case
    - Contract Cycle Time
    - Open Cases Count
    - Settlement Rate
    """

    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all applicable legal KPIs."""
        results = []

        # Try to calculate each KPI
        if self._has_compliance_data(df):
            results.append(self.contract_compliance_rate(df))

        if self._has_resolution_data(df):
            results.append(self.dispute_resolution_time(df))

        if self._has_cost_data(df):
            results.append(self.legal_cost_per_case(df))

        if self._has_cycle_data(df):
            results.append(self.contract_cycle_time(df))

        if self._has_cases_data(df):
            results.append(self.open_cases_count(df))

        if self._has_settlement_data(df):
            results.append(self.settlement_rate(df))

        return results

    def contract_compliance_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Contract Compliance Rate.

        Formula: (Compliant Contracts / Total Contracts) * 100
        """
        compliant_col = self._find_column(df, ['compliant_contracts', 'compliant', 'contracts_compliant'])
        total_col = self._find_column(df, ['total_contracts', 'contracts', 'contract_count'])

        if compliant_col is None or total_col is None:
            return {'kpi': 'Contract Compliance Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_compliant = df[compliant_col].sum()
        total_contracts = df[total_col].sum()

        if total_contracts == 0:
            rate = 0
        else:
            rate = (total_compliant / total_contracts) * 100

        return {
            'kpi': 'Contract Compliance Rate',
            'value': round(rate, 2),
            'unit': '%',
            'compliant_contracts': total_compliant,
            'total_contracts': total_contracts
        }

    def dispute_resolution_time(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Average Dispute Resolution Time.

        Formula: Average days to resolve disputes
        """
        time_col = self._find_column(df, ['resolution_time', 'dispute_days', 'time_to_resolve', 'case_duration'])

        if time_col is None:
            return {'kpi': 'Dispute Resolution Time', 'value': None, 'unit': 'days', 'error': 'Missing data'}

        avg_time = df[time_col].mean()
        median_time = df[time_col].median()

        return {
            'kpi': 'Dispute Resolution Time',
            'value': round(avg_time, 1),
            'unit': 'days',
            'median_days': round(median_time, 1),
            'min_days': df[time_col].min(),
            'max_days': df[time_col].max()
        }

    def legal_cost_per_case(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Average Legal Cost per Case.

        Formula: Total Legal Costs / Number of Cases
        """
        cost_col = self._find_column(df, ['legal_cost', 'legal_fees', 'case_cost', 'legal_expenses'])
        cases_col = self._find_column(df, ['cases', 'case_count', 'disputes', 'legal_cases'])

        if cost_col is None:
            return {'kpi': 'Legal Cost per Case', 'value': None, 'unit': '$', 'error': 'Missing data'}

        total_cost = df[cost_col].sum()

        if cases_col is not None:
            total_cases = df[cases_col].sum()
            if total_cases == 0:
                cost_per_case = 0
            else:
                cost_per_case = total_cost / total_cases
        else:
            # Use number of rows as proxy for cases
            cost_per_case = total_cost / len(df) if len(df) > 0 else 0

        return {
            'kpi': 'Legal Cost per Case',
            'value': round(cost_per_case, 2),
            'unit': '$',
            'total_legal_cost': round(total_cost, 2)
        }

    def contract_cycle_time(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Average Contract Cycle Time.

        Formula: Average days from contract initiation to signature
        """
        cycle_col = self._find_column(df, ['cycle_time', 'contract_days', 'time_to_sign', 'contract_cycle'])

        if cycle_col is None:
            return {'kpi': 'Contract Cycle Time', 'value': None, 'unit': 'days', 'error': 'Missing data'}

        avg_cycle = df[cycle_col].mean()

        return {
            'kpi': 'Contract Cycle Time',
            'value': round(avg_cycle, 1),
            'unit': 'days',
            'median_days': round(df[cycle_col].median(), 1)
        }

    def open_cases_count(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Open/Active Legal Cases.
        """
        cases_col = self._find_column(df, ['open_cases', 'active_cases', 'pending_cases'])

        if cases_col is not None:
            # If we have a column tracking open cases, use the latest value
            current_open = df[cases_col].iloc[-1] if len(df) > 0 else 0
            avg_open = df[cases_col].mean()

            return {
                'kpi': 'Open Cases',
                'value': int(current_open),
                'unit': 'cases',
                'average_open': round(avg_open, 1)
            }

        return {'kpi': 'Open Cases', 'value': None, 'unit': 'cases', 'error': 'Missing data'}

    def settlement_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Settlement Rate.

        Formula: (Settled Cases / Total Resolved Cases) * 100
        """
        settled_col = self._find_column(df, ['settlements', 'settled_cases', 'cases_settled'])
        total_col = self._find_column(df, ['resolved_cases', 'closed_cases', 'total_resolved'])

        if settled_col is None or total_col is None:
            return {'kpi': 'Settlement Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_settled = df[settled_col].sum()
        total_resolved = df[total_col].sum()

        if total_resolved == 0:
            rate = 0
        else:
            rate = (total_settled / total_resolved) * 100

        return {
            'kpi': 'Settlement Rate',
            'value': round(rate, 2),
            'unit': '%',
            'settled_cases': total_settled,
            'total_resolved': total_resolved
        }

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
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

