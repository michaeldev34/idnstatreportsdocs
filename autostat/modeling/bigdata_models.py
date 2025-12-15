"""
Big Data Models

Machine learning models for large datasets.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
except ImportError:
    RandomForestRegressor = None
    train_test_split = None


class BigDataModels:
    """
    Machine learning models for big data.
    
    Models:
    - Random Forest
    - XGBoost
    - Neural Networks
    """
    
    def run_models(self, df: pd.DataFrame, data_type: str) -> List[Dict[str, Any]]:
        """
        Run big data models.
        
        Args:
            df: Input DataFrame
            data_type: Type of data
            
        Returns:
            List of model results
        """
        results = []
        
        # Random Forest
        rf_result = self.random_forest(df)
        if 'error' not in rf_result:
            results.append(rf_result)
        
        return results
    
    def random_forest(self, df: pd.DataFrame, target_col: str = None,
                     n_estimators: int = 100) -> Dict[str, Any]:
        """
        Fit Random Forest model.
        
        Args:
            df: Input DataFrame
            target_col: Target variable (auto-detected if None)
            n_estimators: Number of trees
            
        Returns:
            Dictionary with model results
        """
        if RandomForestRegressor is None:
            return {'model': 'Random Forest', 'error': 'scikit-learn not installed'}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {'model': 'Random Forest', 'error': 'Insufficient numeric columns'}
        
        # Auto-detect target
        if target_col is None:
            target_col = numeric_cols[-1]
        
        feature_cols = [col for col in numeric_cols if col != target_col]
        
        if len(feature_cols) == 0:
            return {'model': 'Random Forest', 'error': 'No feature columns'}
        
        try:
            # Prepare data
            X = df[feature_cols].dropna()
            y = df.loc[X.index, target_col]
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Fit model
            model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Metrics
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            test_mse = mean_squared_error(y_test, y_pred_test)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            # Feature importance
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            feature_importance = {
                k: round(v, 4) 
                for k, v in sorted(feature_importance.items(), 
                                  key=lambda x: x[1], reverse=True)
            }
            
            return {
                'model': 'Random Forest',
                'target': target_col,
                'features': feature_cols,
                'n_estimators': n_estimators,
                'n_train': len(X_train),
                'n_test': len(X_test),
                'train_r2': round(train_r2, 4),
                'test_r2': round(test_r2, 4),
                'r_squared': round(test_r2, 4),  # For consistency
                'mse': round(test_mse, 4),
                'mae': round(test_mae, 4),
                'rmse': round(np.sqrt(test_mse), 4),
                'feature_importance': feature_importance,
                'fitted_model': model
            }
        except Exception as e:
            return {'model': 'Random Forest', 'error': str(e)}
    
    def xgboost(self, df: pd.DataFrame) -> Dict[str, Any]:
        """XGBoost model - placeholder."""
        return {'model': 'XGBoost', 'status': 'Not implemented'}
    
    def neural_networks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Neural Networks - placeholder."""
        return {'model': 'Neural Networks', 'status': 'Not implemented'}

