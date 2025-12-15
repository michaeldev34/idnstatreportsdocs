"""
Stationarity Tests

Tests for stationarity in time series data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.stattools import adfuller, kpss
except ImportError:
    adfuller = None
    kpss = None


class StationarityTests:
    """
    Tests for stationarity in time series.
    
    Tests:
    - Augmented Dickey-Fuller (ADF) test
    - KPSS test
    - Trend detection
    - Drift detection
    - Order of integration
    """
    
    def __init__(self, significance_level: float = 0.05):
        """
        Args:
            significance_level: Significance level for tests (default: 0.05)
        """
        self.significance_level = significance_level
    
    def run_all_tests(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Run all stationarity tests.
        
        Args:
            df: Input DataFrame
            
        Returns:
            List of test results
        """
        results = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # ADF test
            adf_result = self.adf_test(df[col])
            results.append({
                'test': f'ADF Test - {col}',
                'result': adf_result,
                'passed': adf_result.get('is_stationary', False)
            })
            
            # KPSS test
            kpss_result = self.kpss_test(df[col])
            results.append({
                'test': f'KPSS Test - {col}',
                'result': kpss_result,
                'passed': kpss_result.get('is_stationary', False)
            })
            
            # Trend detection
            trend_result = self.detect_trend(df[col])
            results.append({
                'test': f'Trend Detection - {col}',
                'result': trend_result,
                'passed': not trend_result.get('has_trend', True)
            })
        
        return results
    
    def adf_test(self, series: pd.Series) -> Dict[str, Any]:
        """
        Augmented Dickey-Fuller test for unit root.
        
        H0: Series has a unit root (non-stationary)
        H1: Series is stationary
        """
        if adfuller is None:
            return {'error': 'statsmodels not installed'}
        
        series_clean = series.dropna()
        
        if len(series_clean) < 3:
            return {'error': 'Insufficient data'}
        
        try:
            result = adfuller(series_clean, autolag='AIC')
            
            return {
                'test_statistic': result[0],
                'p_value': result[1],
                'n_lags': result[2],
                'n_obs': result[3],
                'critical_values': result[4],
                'is_stationary': result[1] < self.significance_level
            }
        except Exception as e:
            return {'error': str(e)}
    
    def kpss_test(self, series: pd.Series) -> Dict[str, Any]:
        """
        KPSS test for stationarity.
        
        H0: Series is stationary
        H1: Series has a unit root (non-stationary)
        """
        if kpss is None:
            return {'error': 'statsmodels not installed'}
        
        series_clean = series.dropna()
        
        if len(series_clean) < 3:
            return {'error': 'Insufficient data'}
        
        try:
            result = kpss(series_clean, regression='c', nlags='auto')
            
            return {
                'test_statistic': result[0],
                'p_value': result[1],
                'n_lags': result[2],
                'critical_values': result[3],
                'is_stationary': result[1] > self.significance_level
            }
        except Exception as e:
            return {'error': str(e)}
    
    def detect_trend(self, series: pd.Series) -> Dict[str, Any]:
        """
        Detect linear trend in series.
        """
        series_clean = series.dropna()

        if len(series_clean) < 2:
            return {'has_trend': False, 'error': 'Insufficient data'}

        # Simple linear regression
        x = np.arange(len(series_clean))
        y = series_clean.values

        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]

        # Normalize by series std
        std = series_clean.std()
        normalized_slope = slope / std if std > 0 else 0

        # Consider significant if normalized slope > 0.01
        has_trend = abs(normalized_slope) > 0.01

        return {
            'has_trend': has_trend,
            'slope': slope,
            'normalized_slope': normalized_slope,
            'direction': 'increasing' if slope > 0 else 'decreasing'
        }

    def order_of_integration(self, series: pd.Series, max_diff: int = 3) -> Dict[str, Any]:
        """
        Determine the order of integration I(d) for a time series.

        Tests if series is I(0), I(1), I(2), etc. by differencing until stationary.

        Args:
            series: Time series to test
            max_diff: Maximum number of differences to try (default: 3)

        Returns:
            Dictionary with order of integration and test results
        """
        if adfuller is None:
            return {'order': None, 'error': 'statsmodels not installed'}

        series_clean = series.dropna()

        if len(series_clean) < 10:
            return {'order': None, 'error': 'Insufficient data'}

        current_series = series_clean.copy()

        for d in range(max_diff + 1):
            # Test stationarity with ADF
            adf_result = self.adf_test(current_series)

            if 'error' in adf_result:
                return {'order': None, 'error': adf_result['error']}

            # If stationary, we found the order
            if adf_result['is_stationary']:
                return {
                    'order': d,
                    'notation': f'I({d})',
                    'is_stationary': True,
                    'adf_statistic': adf_result['test_statistic'],
                    'adf_pvalue': adf_result['p_value'],
                    'interpretation': self._interpret_integration_order(d)
                }

            # If not stationary and we haven't reached max_diff, difference the series
            if d < max_diff:
                current_series = current_series.diff().dropna()

                # Check if we have enough data after differencing
                if len(current_series) < 10:
                    return {
                        'order': None,
                        'notation': f'I(>{d})',
                        'is_stationary': False,
                        'error': 'Insufficient data after differencing'
                    }

        # If still not stationary after max_diff differences
        return {
            'order': None,
            'notation': f'I(>{max_diff})',
            'is_stationary': False,
            'interpretation': f'Series requires more than {max_diff} differences to achieve stationarity'
        }

    def _interpret_integration_order(self, d: int) -> str:
        """Generate interpretation for order of integration."""
        if d == 0:
            return "Stationary in levels - no differencing needed"
        elif d == 1:
            return "Stationary in first differences - has unit root"
        elif d == 2:
            return "Stationary in second differences - has two unit roots"
        else:
            return f"Stationary after {d} differences"

