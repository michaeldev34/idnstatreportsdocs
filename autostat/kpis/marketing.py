"""
Marketing KPIs

Metrics for marketing performance analysis.
Calculates KPIs per observation for time series, panel, and cross-sectional data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class MarketingKPIs:
    """
    Marketing-specific KPI calculations.

    Calculates per-observation KPIs:
    - Conversion Rate (per period)
    - Customer Acquisition Cost (CAC) (per period)
    - Marketing ROI (per period)
    - Cost per Lead (CPL) (per period)
    - Return on Ad Spend (ROAS) (per period)
    """

    def calculate_all(self, df: pd.DataFrame, data_type: str = 'time_series') -> List[Dict[str, Any]]:
        """
        Calculate all applicable marketing KPIs per observation.

        Args:
            df: Input DataFrame
            data_type: One of 'time_series', 'cross_section', 'panel'

        Returns:
            List of KPI dictionaries with series and summary stats
        """
        results = []

        # Try to calculate each KPI
        if self._has_conversion_data(df):
            results.append(self.conversion_rate(df, data_type))

        if self._has_cac_data(df):
            results.append(self.customer_acquisition_cost(df, data_type))

        if self._has_roi_data(df):
            results.append(self.marketing_roi(df, data_type))

        if self._has_cpl_data(df):
            results.append(self.cost_per_lead(df, data_type))

        if self._has_roas_data(df):
            results.append(self.return_on_ad_spend(df, data_type))

        return results

    def _calculate_summary_stats(self, series: pd.Series, kpi_name: str, unit: str) -> Dict[str, Any]:
        """Calculate summary statistics for a KPI series."""
        clean_series = series.replace([np.inf, -np.inf], np.nan).dropna()

        if len(clean_series) == 0:
            return {
                'kpi': kpi_name,
                'unit': unit,
                'series': series,
                'mean': None,
                'median': None,
                'std': None,
                'min': None,
                'max': None,
                'n_observations': 0,
                'error': 'No valid observations'
            }

        return {
            'kpi': kpi_name,
            'unit': unit,
            'series': series,
            'mean': round(clean_series.mean(), 2),
            'median': round(clean_series.median(), 2),
            'std': round(clean_series.std(), 2),
            'min': round(clean_series.min(), 2),
            'max': round(clean_series.max(), 2),
            'n_observations': len(clean_series),
            'current': round(clean_series.iloc[-1], 2) if len(clean_series) > 0 else None
        }

    def conversion_rate(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate conversion rate per observation.

        Formula: (Conversions / Visitors) * 100 for each row
        """
        conversions_col = self._find_column(df, ['conversions', 'converted', 'sales'])
        visitors_col = self._find_column(df, ['visitors', 'visits', 'traffic'])

        if conversions_col is None or visitors_col is None:
            return {'kpi': 'Conversion Rate', 'value': None, 'unit': '%', 'error': 'Missing data'}

        # Calculate per-observation conversion rate
        series = (df[conversions_col] / df[visitors_col].replace(0, np.nan)) * 100
        series.name = 'conversion_rate'

        return self._calculate_summary_stats(series, 'Conversion Rate', '%')

    def customer_acquisition_cost(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Customer Acquisition Cost (CAC) per observation.

        Formula: Marketing Spend / Customers Acquired for each row
        """
        spend_col = self._find_column(df, ['marketing_spend', 'ad_spend', 'cost'])
        customers_col = self._find_column(df, ['new_customers', 'acquisitions', 'conversions'])

        if spend_col is None or customers_col is None:
            return {'kpi': 'CAC', 'value': None, 'unit': '$', 'error': 'Missing data'}

        # Calculate per-observation CAC
        series = df[spend_col] / df[customers_col].replace(0, np.nan)
        series.name = 'cac'

        return self._calculate_summary_stats(series, 'Customer Acquisition Cost (CAC)', '$')

    def marketing_roi(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Marketing ROI per observation.

        Formula: ((Revenue - Marketing Spend) / Marketing Spend) * 100 for each row
        """
        revenue_col = self._find_column(df, ['revenue', 'sales', 'income'])
        spend_col = self._find_column(df, ['marketing_spend', 'ad_spend', 'cost'])

        if revenue_col is None or spend_col is None:
            return {'kpi': 'Marketing ROI', 'value': None, 'unit': '%', 'error': 'Missing data'}

        # Calculate per-observation ROI
        series = ((df[revenue_col] - df[spend_col]) / df[spend_col].replace(0, np.nan)) * 100
        series.name = 'marketing_roi'

        return self._calculate_summary_stats(series, 'Marketing ROI', '%')

    def cost_per_lead(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Cost per Lead (CPL) per observation.

        Formula: Marketing Spend / Leads for each row
        """
        spend_col = self._find_column(df, ['marketing_spend', 'ad_spend', 'cost'])
        leads_col = self._find_column(df, ['leads', 'lead_count'])

        if spend_col is None or leads_col is None:
            return {'kpi': 'Cost per Lead', 'value': None, 'unit': '$', 'error': 'Missing data'}

        # Calculate per-observation CPL
        series = df[spend_col] / df[leads_col].replace(0, np.nan)
        series.name = 'cpl'

        return self._calculate_summary_stats(series, 'Cost per Lead (CPL)', '$')

    def return_on_ad_spend(self, df: pd.DataFrame, data_type: str = 'time_series') -> Dict[str, Any]:
        """
        Calculate Return on Ad Spend (ROAS) per observation.

        Formula: Revenue / Ad Spend for each row
        """
        revenue_col = self._find_column(df, ['revenue', 'sales', 'income'])
        ad_spend_col = self._find_column(df, ['ad_spend', 'marketing_spend'])

        if revenue_col is None or ad_spend_col is None:
            return {'kpi': 'ROAS', 'value': None, 'unit': 'x', 'error': 'Missing data'}

        # Calculate per-observation ROAS
        series = df[revenue_col] / df[ad_spend_col].replace(0, np.nan)
        series.name = 'roas'

        return self._calculate_summary_stats(series, 'Return on Ad Spend (ROAS)', 'x')

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by checking multiple possible names."""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None

    def _has_conversion_data(self, df: pd.DataFrame) -> bool:
        """Check if conversion data is available."""
        return (self._find_column(df, ['conversions', 'converted']) is not None and
                self._find_column(df, ['visitors', 'visits', 'traffic']) is not None)

    def _has_cac_data(self, df: pd.DataFrame) -> bool:
        """Check if CAC data is available."""
        return (self._find_column(df, ['marketing_spend', 'ad_spend', 'cost']) is not None and
                self._find_column(df, ['new_customers', 'acquisitions', 'conversions']) is not None)

    def _has_roi_data(self, df: pd.DataFrame) -> bool:
        """Check if ROI data is available."""
        return (self._find_column(df, ['revenue', 'sales']) is not None and
                self._find_column(df, ['marketing_spend', 'ad_spend', 'cost']) is not None)

    def _has_cpl_data(self, df: pd.DataFrame) -> bool:
        """Check if CPL data is available."""
        return (self._find_column(df, ['marketing_spend', 'ad_spend', 'cost']) is not None and
                self._find_column(df, ['leads']) is not None)

    def _has_roas_data(self, df: pd.DataFrame) -> bool:
        """Check if ROAS data is available."""
        return (self._find_column(df, ['revenue', 'sales']) is not None and
                self._find_column(df, ['ad_spend', 'marketing_spend']) is not None)

