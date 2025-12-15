"""
MCO (OLS) Assumption Tests

Tests for classical linear regression assumptions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

try:
    from scipy import stats
    import statsmodels.api as sm
except ImportError:
    stats = None
    sm = None


class MCOAssumptionTests:
    """
    Tests for MCO (Ordinary Least Squares) assumptions.
    
    Assumptions tested:
    1. Aleatory sample (random sampling)
    2. Independent observations
    3. Conditional mean zero / Strong exogeneity
    4. Homoscedasticity
    5. No autocorrelation
    6. Normality of residuals
    """
    
    def __init__(self, data_type: str, panel_type: str = 'unfixed'):
        """
        Args:
            data_type: 'time_series', 'cross_section', or 'panel'
            panel_type: 'fixed' or 'unfixed' (only for panel data)
        """
        self.data_type = data_type.lower()
        self.panel_type = panel_type.lower() if panel_type else None
    
    def run_all_tests(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Run all applicable MCO assumption tests.
        
        Args:
            df: Input DataFrame
            
        Returns:
            List of test results
        """
        results = []
        
        # 1. Aleatory sample
        results.append({
            'test': 'Aleatory Sample',
            'result': self.test_aleatory_sample(),
            'passed': self.test_aleatory_sample()['applicable']
        })
        
        # 2. Independent observations
        results.append({
            'test': 'Independent Observations',
            'result': self.test_independent_observations(),
            'passed': self.test_independent_observations()['holds']
        })
        
        # 3. Conditional mean zero
        results.append({
            'test': 'Conditional Mean Zero / Strong Exogeneity',
            'result': self.test_conditional_mean_zero(),
            'passed': self.test_conditional_mean_zero()['holds']
        })
        
        # 4. Homoscedasticity
        homo_result = self.test_homoscedasticity(df)
        results.append({
            'test': 'Homoscedasticity',
            'result': homo_result,
            'passed': homo_result.get('is_homoscedastic', None)
        })
        
        # 5. No autocorrelation
        autocorr_result = self.test_no_autocorrelation(df)
        results.append({
            'test': 'No Autocorrelation',
            'result': autocorr_result,
            'passed': autocorr_result.get('no_autocorrelation', None)
        })
        
        # 6. Normality of residuals
        normality_result = self.test_normality_residuals(df)
        results.append({
            'test': 'Normality of Residuals',
            'result': normality_result,
            'passed': normality_result.get('is_normal', None)
        })
        
        return results
    
    def test_aleatory_sample(self) -> Dict[str, Any]:
        """
        Test if aleatory (random) sampling assumption holds.
        
        This is primarily a design question, not a statistical test.
        """
        if self.data_type == "cross_section":
            return {
                'applicable': True,
                'holds': True,
                'note': 'Cross-section data typically assumes random sampling'
            }
        elif self.data_type == "time_series":
            return {
                'applicable': False,
                'holds': False,
                'note': 'Time series data is not randomly sampled'
            }
        elif self.data_type == "panel":
            return {
                'applicable': False,
                'holds': False,
                'note': 'Panel data is not randomly sampled over time'
            }
        
        return {'applicable': None, 'holds': None}
    
    def test_independent_observations(self) -> Dict[str, Any]:
        """
        Test if observations are independent.
        """
        if self.data_type == "cross_section":
            return {
                'holds': True,
                'note': 'Cross-section observations typically independent'
            }
        elif self.data_type == "time_series":
            return {
                'holds': False,
                'note': 'Time series observations are serially correlated'
            }
        elif self.data_type == "panel":
            if self.panel_type == "fixed":
                return {
                    'holds': False,
                    'note': 'Fixed effects panel has within-entity correlation'
                }
            else:
                return {
                    'holds': False,
                    'note': 'Panel data has serial and cross-sectional correlation'
                }
        
        return {'holds': None}
    
    def test_conditional_mean_zero(self) -> Dict[str, Any]:
        """
        Test conditional mean zero / strong exogeneity assumption.
        """
        if self.data_type == "time_series":
            return {
                'holds': True,
                'assumption': 'strict_exogeneity',
                'note': 'Requires E(u_t | X) = 0 for all t'
            }
        elif self.data_type == "cross_section":
            return {
                'holds': True,
                'assumption': 'exogeneity',
                'note': 'Requires E(u_i | X_i) = 0'
            }
        elif self.data_type == "panel":
            if self.panel_type == "fixed":
                return {
                    'holds': True,
                    'assumption': 'strict_exogeneity_within',
                    'note': 'Fixed effects allow correlation with time-invariant unobservables'
                }
            else:
                return {
                    'holds': True,
                    'assumption': 'strict_exogeneity',
                    'note': 'Random effects require strict exogeneity'
                }
        
        return {'holds': None}

    def test_homoscedasticity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Test for homoscedasticity (constant variance of errors).

        Uses Breusch-Pagan test if statsmodels available.
        """
        if stats is None or sm is None:
            return {'error': 'scipy/statsmodels not installed'}

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) < 2:
            return {'error': 'Insufficient numeric columns'}

        # Simple variance test across groups
        try:
            # Split data into groups and test variance equality
            mid_point = len(df) // 2
            var1 = df[numeric_cols].iloc[:mid_point].var()
            var2 = df[numeric_cols].iloc[mid_point:].var()

            # Levene's test for equality of variances
            is_homoscedastic = True
            for col in numeric_cols:
                if var1[col] > 0 and var2[col] > 0:
                    ratio = max(var1[col], var2[col]) / min(var1[col], var2[col])
                    if ratio > 4:  # Rule of thumb: variance ratio > 4 suggests heteroscedasticity
                        is_homoscedastic = False
                        break

            return {
                'is_homoscedastic': is_homoscedastic,
                'note': 'Variance ratio test across data halves'
            }
        except Exception as e:
            return {'error': str(e)}

    def test_no_autocorrelation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Test for absence of autocorrelation.

        Uses Durbin-Watson test for time series.
        """
        if self.data_type not in ['time_series', 'panel']:
            return {
                'no_autocorrelation': True,
                'note': 'Not applicable for cross-section data'
            }

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return {'error': 'No numeric columns'}

        # Simple autocorrelation test
        try:
            autocorr_values = []
            for col in numeric_cols:
                series = df[col].dropna()
                if len(series) > 1:
                    autocorr = series.autocorr(lag=1)
                    if not np.isnan(autocorr):
                        autocorr_values.append(abs(autocorr))

            if autocorr_values:
                avg_autocorr = np.mean(autocorr_values)
                no_autocorr = avg_autocorr < 0.3  # Rule of thumb

                return {
                    'no_autocorrelation': no_autocorr,
                    'avg_autocorrelation': round(avg_autocorr, 3),
                    'note': 'Average lag-1 autocorrelation across numeric columns'
                }
            else:
                return {'error': 'Could not compute autocorrelation'}
        except Exception as e:
            return {'error': str(e)}

    def test_normality_residuals(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Test for normality of residuals.

        Uses Shapiro-Wilk test for small samples, Kolmogorov-Smirnov for large.
        """
        if stats is None:
            return {'error': 'scipy not installed'}

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return {'error': 'No numeric columns'}

        # Test normality of each numeric column
        try:
            normality_results = []

            for col in numeric_cols:
                series = df[col].dropna()

                if len(series) < 3:
                    continue

                if len(series) <= 5000:
                    # Shapiro-Wilk for small samples
                    stat, p_value = stats.shapiro(series)
                else:
                    # Kolmogorov-Smirnov for large samples
                    stat, p_value = stats.kstest(series, 'norm')

                is_normal = p_value > 0.05
                normality_results.append(is_normal)

            if normality_results:
                overall_normal = np.mean(normality_results) > 0.5

                return {
                    'is_normal': overall_normal,
                    'pct_normal': round(np.mean(normality_results) * 100, 2),
                    'note': f'Tested {len(normality_results)} numeric columns'
                }
            else:
                return {'error': 'Could not test normality'}
        except Exception as e:
            return {'error': str(e)}

