"""
Time Series Models

Models for time series analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

try:
    import statsmodels.api as sm
    from statsmodels.tsa.api import VAR
    from statsmodels.tsa.stattools import grangercausalitytests
    from statsmodels.tsa.vector_ar.vecm import coint_johansen
except ImportError:
    sm = None
    VAR = None
    grangercausalitytests = None
    coint_johansen = None


class TimeSeriesModels:
    """
    Time series models.
    
    Small Data Models:
    - Error Correction Model (ECM)
    - Vector Error Correction Model (VECM)
    - Granger Causality
    
    Big Data Models:
    - ARIMA
    - GARCH
    - VARIMA
    """
    
    def run_small_data_models(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Run models for small time series data."""
        results = []
        
        # Granger causality
        granger_result = self.granger_causality(df)
        if 'error' not in granger_result:
            results.append(granger_result)
        
        return results
    
    def run_big_data_models(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Run models for big time series data."""
        results = []
        
        # ARIMA
        arima_result = self.arima(df)
        if 'error' not in arima_result:
            results.append(arima_result)
        
        return results
    
    def granger_causality(self, df: pd.DataFrame, maxlag: int = 4) -> Dict[str, Any]:
        """
        Test Granger causality between variables.
        
        Args:
            df: Input DataFrame
            maxlag: Maximum lag to test
            
        Returns:
            Dictionary with test results
        """
        if grangercausalitytests is None:
            return {'model': 'Granger Causality', 'error': 'statsmodels not installed'}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {'model': 'Granger Causality', 'error': 'Need at least 2 numeric columns'}
        
        try:
            # Test first two numeric columns
            col1, col2 = numeric_cols[0], numeric_cols[1]
            data = df[[col1, col2]].dropna()
            
            if len(data) < maxlag + 3:
                return {'model': 'Granger Causality', 'error': 'Insufficient observations'}
            
            # Test if col1 Granger-causes col2
            test_result = grangercausalitytests(data[[col2, col1]], maxlag=maxlag, verbose=False)
            
            # Extract p-values for each lag
            p_values = {}
            for lag in range(1, maxlag + 1):
                if lag in test_result:
                    # Get F-test p-value
                    p_val = test_result[lag][0]['ssr_ftest'][1]
                    p_values[f'lag_{lag}'] = round(p_val, 6)
            
            # Determine if there's Granger causality (any lag significant at 5%)
            has_causality = any(p < 0.05 for p in p_values.values())
            
            return {
                'model': 'Granger Causality Test',
                'cause': col1,
                'effect': col2,
                'maxlag': maxlag,
                'p_values': p_values,
                'has_causality': has_causality,
                'note': f'Tests if {col1} Granger-causes {col2}'
            }
        except Exception as e:
            return {'model': 'Granger Causality', 'error': str(e)}
    
    def arima(self, df: pd.DataFrame, target_col: str = None, 
              order: tuple = (1, 1, 1)) -> Dict[str, Any]:
        """
        Fit ARIMA model.
        
        Args:
            df: Input DataFrame
            target_col: Target column (auto-detected if None)
            order: ARIMA order (p, d, q)
            
        Returns:
            Dictionary with model results
        """
        if sm is None:
            return {'model': 'ARIMA', 'error': 'statsmodels not installed'}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            return {'model': 'ARIMA', 'error': 'No numeric columns'}
        
        # Auto-detect target
        if target_col is None:
            target_col = numeric_cols[0]
        
        try:
            series = df[target_col].dropna()
            
            if len(series) < 10:
                return {'model': 'ARIMA', 'error': 'Insufficient observations'}
            
            # Fit ARIMA
            model = sm.tsa.ARIMA(series, order=order)
            fitted = model.fit()
            
            return {
                'model': f'ARIMA{order}',
                'target': target_col,
                'n_obs': len(series),
                'aic': round(fitted.aic, 2),
                'bic': round(fitted.bic, 2),
                'log_likelihood': round(fitted.llf, 2),
                'fitted_model': fitted
            }
        except Exception as e:
            return {'model': 'ARIMA', 'error': str(e)}
    
    def ecm(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Error Correction Model - placeholder."""
        return {'model': 'ECM', 'status': 'Not implemented'}
    
    def vecm(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Vector Error Correction Model - placeholder."""
        return {'model': 'VECM', 'status': 'Not implemented'}
    
    def garch(self, df: pd.DataFrame) -> Dict[str, Any]:
        """GARCH model - placeholder."""
        return {'model': 'GARCH', 'status': 'Not implemented'}
    
    def varima(self, df: pd.DataFrame) -> Dict[str, Any]:
        """VARIMA model - placeholder."""
        return {'model': 'VARIMA', 'status': 'Not implemented'}

