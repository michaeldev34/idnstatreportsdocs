"""
Operations KPIs

Metrics for operational efficiency and performance.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class OperationsKPIs:
    """
    Operations-specific KPI calculations.
    
    KPIs:
    - Overall Equipment Effectiveness (OEE)
    - Units Produced per Hour
    - Cycle Time
    - Throughput
    - Capacity Utilization
    """
    
    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all applicable operations KPIs."""
        results = []
        
        if self._has_oee_data(df):
            results.append(self.oee(df))
        
        if self._has_production_data(df):
            results.append(self.units_produced_per_hour(df))
        
        if self._has_throughput_data(df):
            results.append(self.throughput(df))
        
        return results
    
    def oee(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Overall Equipment Effectiveness.
        
        Formula: Availability × Performance × Quality
        """
        availability = self._find_column(df, ['availability', 'uptime_pct'])
        performance = self._find_column(df, ['performance', 'performance_pct'])
        quality = self._find_column(df, ['quality', 'quality_pct', 'yield'])
        
        if availability and performance and quality:
            oee_value = (df[availability].mean() / 100) * \
                       (df[performance].mean() / 100) * \
                       (df[quality].mean() / 100) * 100
        else:
            # Try to calculate from raw data
            uptime = self._find_column(df, ['uptime', 'operating_time'])
            planned = self._find_column(df, ['planned_time', 'available_time'])
            
            if uptime and planned:
                availability_calc = (df[uptime].sum() / df[planned].sum()) * 100
                oee_value = availability_calc  # Simplified if other components missing
            else:
                return {'kpi': 'OEE', 'value': None, 'unit': '%', 'error': 'Missing data'}
        
        return {
            'kpi': 'Overall Equipment Effectiveness',
            'value': round(oee_value, 2),
            'unit': '%'
        }
    
    def units_produced_per_hour(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate production rate.
        
        Formula: Total Units / Total Hours
        """
        units = self._find_column(df, ['units', 'production', 'output', 'quantity'])
        hours = self._find_column(df, ['hours', 'time', 'duration'])
        
        if units is None or hours is None:
            return {'kpi': 'Units per Hour', 'value': None, 'unit': 'units/hr', 'error': 'Missing data'}
        
        total_units = df[units].sum()
        total_hours = df[hours].sum()
        
        if total_hours == 0:
            rate = 0
        else:
            rate = total_units / total_hours
        
        return {
            'kpi': 'Units Produced per Hour',
            'value': round(rate, 2),
            'unit': 'units/hr',
            'total_units': total_units,
            'total_hours': total_hours
        }
    
    def throughput(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate throughput (units completed per time period).
        """
        units = self._find_column(df, ['completed', 'finished', 'output'])
        
        if units is None:
            return {'kpi': 'Throughput', 'value': None, 'unit': 'units', 'error': 'Missing data'}
        
        avg_throughput = df[units].mean()
        total_throughput = df[units].sum()
        
        return {
            'kpi': 'Throughput',
            'value': round(avg_throughput, 2),
            'unit': 'units/period',
            'total': total_throughput
        }
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None
    
    def _has_oee_data(self, df: pd.DataFrame) -> bool:
        """Check if OEE data is available."""
        return (self._find_column(df, ['availability', 'uptime']) is not None or
                self._find_column(df, ['performance']) is not None)
    
    def _has_production_data(self, df: pd.DataFrame) -> bool:
        """Check if production data is available."""
        return (self._find_column(df, ['units', 'production']) is not None and
                self._find_column(df, ['hours', 'time']) is not None)
    
    def _has_throughput_data(self, df: pd.DataFrame) -> bool:
        """Check if throughput data is available."""
        return self._find_column(df, ['completed', 'finished', 'output']) is not None

