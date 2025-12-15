"""
Marketing KPIs

Metrics for marketing performance analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class MarketingKPIs:
    """
    Marketing-specific KPI calculations.
    
    KPIs:
    - Conversion Rate
    - Customer Acquisition Cost (CAC)
    - Marketing ROI
    - Lead-to-Customer Rate
    - Cost per Lead (CPL)
    """
    
    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all applicable marketing KPIs."""
        results = []
        
        # Try to calculate each KPI
        if self._has_conversion_data(df):
            results.append(self.conversion_rate(df))
        
        if self._has_cac_data(df):
            results.append(self.customer_acquisition_cost(df))
        
        if self._has_roi_data(df):
            results.append(self.marketing_roi(df))
        
        return results
    
    def conversion_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate conversion rate.
        
        Formula: (Conversions / Total Visitors) * 100
        """
        # Look for common column names
        conversions = self._find_column(df, ['conversions', 'converted', 'sales'])
        visitors = self._find_column(df, ['visitors', 'visits', 'traffic', 'leads'])
        
        if conversions is None or visitors is None:
            return {'kpi': 'Conversion Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}
        
        total_conversions = df[conversions].sum()
        total_visitors = df[visitors].sum()
        
        if total_visitors == 0:
            rate = 0
        else:
            rate = (total_conversions / total_visitors) * 100
        
        return {
            'kpi': 'Conversion Rate',
            'value': round(rate, 2),
            'unit': '%',
            'total_conversions': total_conversions,
            'total_visitors': total_visitors
        }
    
    def customer_acquisition_cost(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Customer Acquisition Cost (CAC).
        
        Formula: Total Marketing Spend / New Customers Acquired
        """
        spend = self._find_column(df, ['marketing_spend', 'ad_spend', 'cost'])
        customers = self._find_column(df, ['new_customers', 'acquisitions', 'conversions'])
        
        if spend is None or customers is None:
            return {'kpi': 'CAC', 'value': None, 'unit': '$', 'error': 'Missing data'}
        
        total_spend = df[spend].sum()
        total_customers = df[customers].sum()
        
        if total_customers == 0:
            cac = 0
        else:
            cac = total_spend / total_customers
        
        return {
            'kpi': 'Customer Acquisition Cost',
            'value': round(cac, 2),
            'unit': '$',
            'total_spend': total_spend,
            'total_customers': total_customers
        }
    
    def marketing_roi(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Marketing ROI.
        
        Formula: ((Revenue - Marketing Spend) / Marketing Spend) * 100
        """
        revenue = self._find_column(df, ['revenue', 'sales', 'income'])
        spend = self._find_column(df, ['marketing_spend', 'ad_spend', 'cost'])
        
        if revenue is None or spend is None:
            return {'kpi': 'Marketing ROI', 'value': None, 'unit': '%', 'error': 'Missing data'}
        
        total_revenue = df[revenue].sum()
        total_spend = df[spend].sum()
        
        if total_spend == 0:
            roi = 0
        else:
            roi = ((total_revenue - total_spend) / total_spend) * 100
        
        return {
            'kpi': 'Marketing ROI',
            'value': round(roi, 2),
            'unit': '%',
            'total_revenue': total_revenue,
            'total_spend': total_spend
        }
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None
    
    def _has_conversion_data(self, df: pd.DataFrame) -> bool:
        """Check if conversion data is available."""
        return (self._find_column(df, ['conversions', 'converted']) is not None and
                self._find_column(df, ['visitors', 'visits']) is not None)
    
    def _has_cac_data(self, df: pd.DataFrame) -> bool:
        """Check if CAC data is available."""
        return (self._find_column(df, ['marketing_spend', 'ad_spend']) is not None and
                self._find_column(df, ['new_customers', 'acquisitions']) is not None)
    
    def _has_roi_data(self, df: pd.DataFrame) -> bool:
        """Check if ROI data is available."""
        return (self._find_column(df, ['revenue', 'sales']) is not None and
                self._find_column(df, ['marketing_spend', 'ad_spend']) is not None)

