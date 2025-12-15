"""
Stationarity Tests

Tests for stationarity in time series data.
Uses majority voting system for robust stationarity determination:
- Group 1 (Unit Root tests): ADF, DF, PP - require 2/3 consensus
- Group 2 (Stationarity test): KPSS
- Both groups must agree for definitive conclusion
- If inconclusive after 5 differencing attempts: I(?)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.stattools import adfuller, kpss
    from arch.unitroot import PhillipsPerron
    HAS_PP = True
except ImportError:
    adfuller = None
    kpss = None
    HAS_PP = False
    try:
        from statsmodels.tsa.stattools import adfuller, kpss
    except ImportError:
        pass


class StationarityTests:
    """
    Tests for stationarity in time series.

    Tests:
    - Augmented Dickey-Fuller (ADF) test - H0: has unit root
    - Dickey-Fuller (DF) test - H0: has unit root
    - Phillips-Perron (PP) test - H0: has unit root
    - KPSS test - H0: is stationary (opposite hypothesis)
    - Trend detection
    - Drift detection
    - Order of integration (with majority voting)
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
    
    def df_test(self, series: pd.Series) -> Dict[str, Any]:
        """
        Simple Dickey-Fuller test for unit root (without augmentation).

        H0: Series has a unit root (non-stationary)
        H1: Series is stationary

        Uses ADF with fixed lag of 0 to simulate simple DF test.
        """
        if adfuller is None:
            return {'error': 'statsmodels not installed'}

        series_clean = series.dropna()

        if len(series_clean) < 3:
            return {'error': 'Insufficient data'}

        try:
            # Use maxlag=0 to get simple DF test (no augmentation)
            result = adfuller(series_clean, maxlag=0, autolag=None)

            return {
                'test_statistic': result[0],
                'p_value': result[1],
                'n_lags': 0,
                'n_obs': result[3],
                'critical_values': result[4],
                'is_stationary': result[1] < self.significance_level
            }
        except Exception as e:
            return {'error': str(e)}

    def pp_test(self, series: pd.Series) -> Dict[str, Any]:
        """
        Phillips-Perron test for unit root.

        H0: Series has a unit root (non-stationary)
        H1: Series is stationary
        """
        series_clean = series.dropna()

        if len(series_clean) < 10:
            return {'error': 'Insufficient data'}

        try:
            if HAS_PP:
                # Use arch package's PhillipsPerron
                pp = PhillipsPerron(series_clean)
                return {
                    'test_statistic': pp.stat,
                    'p_value': pp.pvalue,
                    'n_lags': pp.lags,
                    'n_obs': len(series_clean),
                    'is_stationary': pp.pvalue < self.significance_level
                }
            else:
                # Fallback: approximate PP with ADF using different settings
                result = adfuller(series_clean, regression='c', autolag='BIC')
                return {
                    'test_statistic': result[0],
                    'p_value': result[1],
                    'n_lags': result[2],
                    'n_obs': result[3],
                    'critical_values': result[4],
                    'is_stationary': result[1] < self.significance_level,
                    'note': 'Approximated using ADF (arch package not installed)'
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

    def _majority_vote_unit_root(self, series: pd.Series) -> Dict[str, Any]:
        """
        Perform majority voting for unit root tests.

        Group 1 (Unit Root tests - H0: has unit root): ADF, DF, PP
        - Need 2/3 consensus for Group 1 conclusion

        Returns dict with group 1 consensus on whether series is stationary.
        """
        results = {}
        votes_stationary = 0
        votes_nonstationary = 0
        valid_tests = 0

        # Run ADF test
        adf = self.adf_test(series)
        results['adf'] = adf
        if 'error' not in adf:
            valid_tests += 1
            if adf['is_stationary']:
                votes_stationary += 1
            else:
                votes_nonstationary += 1

        # Run DF test
        df = self.df_test(series)
        results['df'] = df
        if 'error' not in df:
            valid_tests += 1
            if df['is_stationary']:
                votes_stationary += 1
            else:
                votes_nonstationary += 1

        # Run PP test
        pp = self.pp_test(series)
        results['pp'] = pp
        if 'error' not in pp:
            valid_tests += 1
            if pp['is_stationary']:
                votes_stationary += 1
            else:
                votes_nonstationary += 1

        # Majority voting: need at least 2/3 for consensus
        if valid_tests >= 2:
            threshold = valid_tests * 2 / 3  # 2/3 majority
            if votes_stationary >= threshold:
                group1_conclusion = 'stationary'
                group1_consensus = True
            elif votes_nonstationary >= threshold:
                group1_conclusion = 'non-stationary'
                group1_consensus = True
            else:
                group1_conclusion = 'inconclusive'
                group1_consensus = False
        else:
            group1_conclusion = 'insufficient_tests'
            group1_consensus = False

        return {
            'results': results,
            'votes_stationary': votes_stationary,
            'votes_nonstationary': votes_nonstationary,
            'valid_tests': valid_tests,
            'conclusion': group1_conclusion,
            'has_consensus': group1_consensus
        }

    def order_of_integration(self, series: pd.Series, max_diff: int = 5) -> Dict[str, Any]:
        """
        Determine the order of integration I(d) for a time series using majority voting.

        Uses two groups of tests:
        - Group 1 (Unit Root tests): ADF, DF, PP - H0: has unit root
          Requires 2/3 consensus for conclusion
        - Group 2 (Stationarity test): KPSS - H0: is stationary (opposite)

        Both groups must agree for definitive conclusion.
        If inconclusive after 5 differencing attempts, returns I(?).

        Args:
            series: Time series to test
            max_diff: Maximum number of differences to try (default: 5)

        Returns:
            Dictionary with order of integration and test results
        """
        if adfuller is None:
            return {'order': None, 'error': 'statsmodels not installed'}

        series_clean = series.dropna()

        if len(series_clean) < 10:
            return {'order': None, 'error': 'Insufficient data'}

        current_series = series_clean.copy()
        inconclusive_count = 0

        for d in range(max_diff + 1):
            # Group 1: Unit root tests (ADF, DF, PP) with majority voting
            group1 = self._majority_vote_unit_root(current_series)

            # Group 2: KPSS test (opposite hypothesis)
            kpss_result = self.kpss_test(current_series)
            group2_stationary = kpss_result.get('is_stationary', None) if 'error' not in kpss_result else None

            # Check if both groups agree
            if group1['has_consensus'] and group2_stationary is not None:
                group1_says_stationary = (group1['conclusion'] == 'stationary')
                group2_says_stationary = group2_stationary

                # Both groups agree series is stationary
                if group1_says_stationary and group2_says_stationary:
                    return {
                        'order': d,
                        'notation': f'I({d})',
                        'is_stationary': True,
                        'group1_votes': f"{group1['votes_stationary']}/{group1['valid_tests']} stationary",
                        'kpss_stationary': True,
                        'interpretation': self._interpret_integration_order(d),
                        'confidence': 'high',
                        'method': 'majority_voting'
                    }

                # Groups disagree
                if group1_says_stationary != group2_says_stationary:
                    inconclusive_count += 1
            else:
                # No consensus in Group 1
                inconclusive_count += 1

            # If not stationary and we haven't reached max_diff, difference the series
            if d < max_diff:
                current_series = current_series.diff().dropna()

                # Check if we have enough data after differencing
                if len(current_series) < 10:
                    return {
                        'order': None,
                        'notation': 'I(?)',
                        'is_stationary': False,
                        'error': 'Insufficient data after differencing',
                        'interpretation': 'Unable to determine order - insufficient data'
                    }

        # If inconclusive after max_diff attempts
        return {
            'order': None,
            'notation': 'I(?)',
            'is_stationary': False,
            'inconclusive_attempts': inconclusive_count,
            'interpretation': f'Inconclusive after {max_diff} differencing attempts - tests disagree',
            'confidence': 'low',
            'method': 'majority_voting'
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

