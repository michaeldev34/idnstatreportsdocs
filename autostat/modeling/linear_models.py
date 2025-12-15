"""
Linear Models

Classical linear regression models.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

try:
    import statsmodels.api as sm
except ImportError:
    sm = None


class LinearModels:
    """
    Linear regression models.
    
    Models:
    - Multiple Linear Regression (OLS)
    - Weighted Least Squares (WLS)
    - Generalized Least Squares (GLS)
    """
    
    def run_models(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Run all applicable linear models.
        
        Args:
            df: Input DataFrame
            
        Returns:
            List of model results
        """
        results = []
        
        # Try OLS
        ols_result = self.multiple_linear_regression(df)
        if 'error' not in ols_result:
            results.append(ols_result)
        
        return results
    
    def multiple_linear_regression(self, df: pd.DataFrame, 
                                   target_col: str = None) -> Dict[str, Any]:
        """
        Fit Multiple Linear Regression (OLS).
        
        Args:
            df: Input DataFrame
            target_col: Target variable column name (auto-detected if None)
            
        Returns:
            Dictionary with model results
        """
        if sm is None:
            return {'model': 'OLS', 'error': 'statsmodels not installed'}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {'model': 'OLS', 'error': 'Insufficient numeric columns'}
        
        # Auto-detect target (last column by default)
        if target_col is None:
            target_col = numeric_cols[-1]
        
        if target_col not in numeric_cols:
            return {'model': 'OLS', 'error': f'Target column {target_col} not found'}
        
        # Prepare X and y
        feature_cols = [col for col in numeric_cols if col != target_col]
        
        if len(feature_cols) == 0:
            return {'model': 'OLS', 'error': 'No feature columns available'}
        
        X = df[feature_cols].dropna()
        y = df.loc[X.index, target_col]
        
        if len(X) < len(feature_cols) + 1:
            return {'model': 'OLS', 'error': 'Insufficient observations'}
        
        try:
            # Add constant
            X_with_const = sm.add_constant(X)
            
            # Fit model
            model = sm.OLS(y, X_with_const)
            fitted = model.fit()
            
            # Extract results
            return {
                'model': 'Multiple Linear Regression (OLS)',
                'target': target_col,
                'features': feature_cols,
                'n_obs': int(fitted.nobs),
                'r_squared': round(fitted.rsquared, 4),
                'adj_r_squared': round(fitted.rsquared_adj, 4),
                'f_statistic': round(fitted.fvalue, 4),
                'f_pvalue': round(fitted.f_pvalue, 6),
                'aic': round(fitted.aic, 2),
                'bic': round(fitted.bic, 2),
                'coefficients': {
                    name: round(coef, 4) 
                    for name, coef in fitted.params.items()
                },
                'pvalues': {
                    name: round(pval, 6) 
                    for name, pval in fitted.pvalues.items()
                },
                'residuals_std': round(np.std(fitted.resid), 4),
                'fitted_model': fitted  # Store for predictions
            }
        except Exception as e:
            return {'model': 'OLS', 'error': str(e)}

