"""
Production KPIs

Metrics for production and manufacturing performance analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class ProductionKPIs:
    """
    Production-specific KPI calculations.

    KPIs:
    - Production Volume
    - Production Efficiency (OEE)
    - Capacity Utilization
    - Yield Rate
    - Scrap Rate
    - Downtime Percentage
    """

    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all applicable production KPIs."""
        results = []

        # Try to calculate each KPI
        if self._has_volume_data(df):
            results.append(self.production_volume(df))

        if self._has_efficiency_data(df):
            results.append(self.production_efficiency(df))

        if self._has_utilization_data(df):
            results.append(self.capacity_utilization(df))

        if self._has_yield_data(df):
            results.append(self.yield_rate(df))

        if self._has_scrap_data(df):
            results.append(self.scrap_rate(df))

        if self._has_downtime_data(df):
            results.append(self.downtime_percentage(df))

        return results

    def production_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate total production volume.

        Formula: Sum of units produced
        """
        volume_col = self._find_column(df, ['units_produced', 'production_volume', 'output', 'units', 'quantity_produced'])

        if volume_col is None:
            return {'kpi': 'Production Volume', 'value': None, 'unit': 'units', 'error': 'Missing data'}

        total_volume = df[volume_col].sum()
        avg_volume = df[volume_col].mean()

        return {
            'kpi': 'Production Volume',
            'value': round(total_volume, 0),
            'unit': 'units',
            'average_per_period': round(avg_volume, 2),
            'periods': len(df)
        }

    def production_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Overall Equipment Effectiveness (OEE).

        Formula: (Actual Output / Theoretical Maximum Output) * 100
        """
        actual_col = self._find_column(df, ['units_produced', 'actual_output', 'output', 'units'])
        max_col = self._find_column(df, ['capacity', 'max_output', 'planned_output', 'theoretical_output'])

        if actual_col is None or max_col is None:
            # Alternative: use production_hours vs planned_time
            prod_hours = self._find_column(df, ['production_hours', 'actual_hours', 'working_hours'])
            planned_hours = self._find_column(df, ['planned_time', 'planned_hours', 'available_time'])

            if prod_hours is not None and planned_hours is not None:
                total_prod = df[prod_hours].sum()
                total_planned = df[planned_hours].sum()

                if total_planned == 0:
                    efficiency = 0
                else:
                    efficiency = (total_prod / total_planned) * 100

                return {
                    'kpi': 'Production Efficiency',
                    'value': round(efficiency, 2),
                    'unit': '%',
                    'production_hours': total_prod,
                    'planned_hours': total_planned
                }

            return {'kpi': 'Production Efficiency', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_actual = df[actual_col].sum()
        total_max = df[max_col].sum()

        if total_max == 0:
            efficiency = 0
        else:
            efficiency = (total_actual / total_max) * 100

        return {
            'kpi': 'Production Efficiency',
            'value': round(efficiency, 2),
            'unit': '%',
            'actual_output': total_actual,
            'theoretical_max': total_max
        }

    def capacity_utilization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Capacity Utilization Rate.

        Formula: (Actual Production / Maximum Capacity) * 100
        """
        utilization_col = self._find_column(df, ['utilization', 'capacity_utilization', 'utilization_rate'])

        if utilization_col is not None:
            avg_utilization = df[utilization_col].mean()
            return {
                'kpi': 'Capacity Utilization',
                'value': round(avg_utilization, 2),
                'unit': '%'
            }

        # Calculate from uptime and planned time
        uptime_col = self._find_column(df, ['uptime', 'operating_time', 'run_time'])
        planned_col = self._find_column(df, ['planned_time', 'available_time', 'scheduled_time'])

        if uptime_col is not None and planned_col is not None:
            total_uptime = df[uptime_col].sum()
            total_planned = df[planned_col].sum()

            if total_planned == 0:
                utilization = 0
            else:
                utilization = (total_uptime / total_planned) * 100

            return {
                'kpi': 'Capacity Utilization',
                'value': round(utilization, 2),
                'unit': '%',
                'total_uptime': total_uptime,
                'total_planned_time': total_planned
            }

        return {'kpi': 'Capacity Utilization', 'value': None, 'unit': '%', 'error': 'Missing data'}

    def yield_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Yield Rate (First Pass Yield).

        Formula: (Good Units / Total Units Produced) * 100
        """
        good_col = self._find_column(df, ['good_units', 'passed_units', 'quality_passed'])
        total_col = self._find_column(df, ['units_produced', 'total_units', 'production_volume'])

        if good_col is None or total_col is None:
            return {'kpi': 'Yield Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_good = df[good_col].sum()
        total_produced = df[total_col].sum()

        if total_produced == 0:
            yield_rate = 0
        else:
            yield_rate = (total_good / total_produced) * 100

        return {
            'kpi': 'Yield Rate',
            'value': round(yield_rate, 2),
            'unit': '%',
            'good_units': total_good,
            'total_produced': total_produced
        }

    def scrap_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Scrap Rate.

        Formula: (Scrap Units / Total Units Produced) * 100
        """
        scrap_col = self._find_column(df, ['scrap', 'scrap_units', 'defects', 'rejected_units'])
        total_col = self._find_column(df, ['units_produced', 'total_units', 'production_volume'])

        if scrap_col is None or total_col is None:
            return {'kpi': 'Scrap Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_scrap = df[scrap_col].sum()
        total_produced = df[total_col].sum()

        if total_produced == 0:
            scrap_rate = 0
        else:
            scrap_rate = (total_scrap / total_produced) * 100

        return {
            'kpi': 'Scrap Rate',
            'value': round(scrap_rate, 2),
            'unit': '%',
            'scrap_units': total_scrap,
            'total_produced': total_produced
        }

    def downtime_percentage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Downtime Percentage.

        Formula: (Downtime / Total Available Time) * 100
        """
        downtime_col = self._find_column(df, ['downtime', 'unplanned_downtime', 'maintenance_time'])
        total_col = self._find_column(df, ['planned_time', 'available_time', 'total_time'])

        if downtime_col is None or total_col is None:
            return {'kpi': 'Downtime Percentage', 'value': None, 'unit': '%', 'error': 'Missing data'}

        total_downtime = df[downtime_col].sum()
        total_available = df[total_col].sum()

        if total_available == 0:
            downtime_pct = 0
        else:
            downtime_pct = (total_downtime / total_available) * 100

        return {
            'kpi': 'Downtime Percentage',
            'value': round(downtime_pct, 2),
            'unit': '%',
            'total_downtime': total_downtime,
            'total_available_time': total_available
        }

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
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

    def _has_yield_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['good_units', 'passed_units']) is not None

    def _has_scrap_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['scrap', 'scrap_units', 'defects']) is not None

    def _has_downtime_data(self, df: pd.DataFrame) -> bool:
        return self._find_column(df, ['downtime', 'unplanned_downtime']) is not None

