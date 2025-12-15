"""
Customer KPIs

Metrics for customer satisfaction and retention.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class CustomerKPIs:
    """
    Customer-specific KPI calculations.
    
    KPIs:
    - Customer Satisfaction Score (CSAT)
    - Customer Retention Rate
    - Churn Rate
    - Net Promoter Score (NPS)
    - Customer Lifetime Value (CLV)
    """
    
    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all applicable customer KPIs."""
        results = []
        
        if self._has_satisfaction_data(df):
            results.append(self.customer_satisfaction(df))
        
        if self._has_retention_data(df):
            results.append(self.customer_retention(df))
        
        if self._has_churn_data(df):
            results.append(self.churn_rate(df))
        
        return results
    
    def customer_satisfaction(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Customer Satisfaction Score.
        
        Formula: Average of satisfaction ratings
        """
        satisfaction = self._find_column(df, ['satisfaction', 'csat', 'rating', 'score'])
        
        if satisfaction is None:
            return {'kpi': 'CSAT', 'value': None, 'unit': 'score', 'error': 'Missing data'}
        
        avg_satisfaction = df[satisfaction].mean()
        
        return {
            'kpi': 'Customer Satisfaction Score',
            'value': round(avg_satisfaction, 2),
            'unit': 'score',
            'n_responses': df[satisfaction].count()
        }
    
    def customer_retention(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Customer Retention Rate.
        
        Formula: ((Customers End - New Customers) / Customers Start) * 100
        """
        start = self._find_column(df, ['customers_start', 'beginning_customers'])
        end = self._find_column(df, ['customers_end', 'ending_customers'])
        new = self._find_column(df, ['new_customers', 'acquired'])
        
        if start is None or end is None:
            return {'kpi': 'Retention Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}
        
        customers_start = df[start].iloc[0] if len(df) > 0 else 0
        customers_end = df[end].iloc[-1] if len(df) > 0 else 0
        new_customers = df[new].sum() if new is not None else 0
        
        if customers_start == 0:
            rate = 0
        else:
            rate = ((customers_end - new_customers) / customers_start) * 100
        
        return {
            'kpi': 'Customer Retention Rate',
            'value': round(rate, 2),
            'unit': '%',
            'customers_start': customers_start,
            'customers_end': customers_end
        }
    
    def churn_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Churn Rate.
        
        Formula: (Customers Lost / Total Customers at Start) * 100
        """
        lost = self._find_column(df, ['churned', 'lost', 'cancelled'])
        total = self._find_column(df, ['total_customers', 'customers_start'])
        
        if lost is None or total is None:
            return {'kpi': 'Churn Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}
        
        customers_lost = df[lost].sum()
        total_customers = df[total].iloc[0] if len(df) > 0 else df[total].mean()
        
        if total_customers == 0:
            rate = 0
        else:
            rate = (customers_lost / total_customers) * 100
        
        return {
            'kpi': 'Churn Rate',
            'value': round(rate, 2),
            'unit': '%',
            'customers_lost': customers_lost,
            'total_customers': total_customers
        }
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None
    
    def _has_satisfaction_data(self, df: pd.DataFrame) -> bool:
        """Check if satisfaction data is available."""
        return self._find_column(df, ['satisfaction', 'csat', 'rating']) is not None
    
    def _has_retention_data(self, df: pd.DataFrame) -> bool:
        """Check if retention data is available."""
        return (self._find_column(df, ['customers_start', 'beginning']) is not None and
                self._find_column(df, ['customers_end', 'ending']) is not None)
    
    def _has_churn_data(self, df: pd.DataFrame) -> bool:
        """Check if churn data is available."""
        return (self._find_column(df, ['churned', 'lost']) is not None and
                self._find_column(df, ['total_customers']) is not None)

