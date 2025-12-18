"""
Model Runner

Orchestrates model selection and execution based on metadata.
"""

import pandas as pd
from typing import Dict, Any, List
from autostat.modeling.linear_models import LinearModels
from autostat.modeling.nonlinear_models import NonlinearModels
from autostat.modeling.time_series_models import TimeSeriesModels
from autostat.modeling.panel_models import PanelModels
from autostat.modeling.bigdata_models import BigDataModels
from autostat.modeling.department_regressions import DepartmentRegressionRunner


class ModelsRunner:
    """
    Orchestrates model selection and execution.
    
    Automatically selects appropriate models based on:
    - Data type (time_series, cross_section, panel)
    - Data size (small <5000, big >=5000)
    - Linearity (linear vs non-linear)
    """
    
    def __init__(self, metadata: Dict[str, Any], label: str = "default", department: str = None):
        """
        Args:
            metadata: Metadata about the dataset
            label: Identifier for this modeling run
            department: Optional department filter for regressions
        """
        self.metadata = metadata
        self.label = label
        self.department = department
        self.results = []
        self.department_regression_results = []

        # Initialize model modules
        self.linear_models = LinearModels()
        self.nonlinear_models = NonlinearModels()
        self.time_series_models = TimeSeriesModels()
        self.panel_models = PanelModels()
        self.bigdata_models = BigDataModels()
        self.department_regressions = DepartmentRegressionRunner(department)
    
    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute appropriate models based on metadata.
        
        Args:
            df: Input DataFrame (preprocessed)
            
        Returns:
            Dictionary with model results
        """
        data_type = self.metadata.get('data_type', 'cross_section')
        size_category = self.metadata.get('size_category', 'small')
        is_linear = self.metadata.get('is_linear', True)
        
        # Select models based on data characteristics
        if size_category == 'small':
            # Small data: classical statistical models
            if data_type == 'time_series':
                self._run_small_time_series(df)
            elif data_type == 'panel':
                self._run_panel_models(df)
            else:  # cross_section
                self._run_small_cross_section(df, is_linear)
        else:
            # Big data: machine learning models
            self._run_big_data_models(df, data_type)

        # Run department-specific regressions (always)
        self._run_department_regressions(df)

        return {
            'models_run': len(self.results),
            'results': self.results,
            'best_model': self._select_best_model(),
            'department_regressions': self.department_regression_results
        }
    
    def _run_small_time_series(self, df: pd.DataFrame):
        """Run models for small time series data."""
        # ECM, VECM, Granger causality
        results = self.time_series_models.run_small_data_models(df)
        self.results.extend(results)
    
    def _run_panel_models(self, df: pd.DataFrame):
        """Run panel data models."""
        panel_type = self.metadata.get('panel_type', 'unfixed')
        results = self.panel_models.run_models(df, panel_type)
        self.results.extend(results)
    
    def _run_small_cross_section(self, df: pd.DataFrame, is_linear: bool):
        """Run models for small cross-section data."""
        if is_linear:
            results = self.linear_models.run_models(df)
        else:
            results = self.nonlinear_models.run_models(df)
        self.results.extend(results)
    
    def _run_big_data_models(self, df: pd.DataFrame, data_type: str):
        """Run machine learning models for big data."""
        results = self.bigdata_models.run_models(df, data_type)
        self.results.extend(results)

    def _run_department_regressions(self, df: pd.DataFrame):
        """Run department-specific regression models from metrics document."""
        results = self.department_regressions.run(df, self.metadata)
        self.department_regression_results = results
        # Also add to main results for best model selection
        for r in results:
            # Add to main results with standardized format
            self.results.append({
                'model': r['model_name'],
                'department': r['department'],
                'r_squared': r['r_squared'],
                'adj_r_squared': r['adj_r_squared'],
                'mae': r['mae'],
                'n_obs': r['n_observations'],
                'f_statistic': r['f_statistic'],
                'f_pvalue': r['f_pvalue'],
                'interpretation': r['interpretation']
            })

    def _select_best_model(self) -> Dict[str, Any]:
        """Select best model based on Mean Absolute Error (MAE).

        Lower MAE is better, indicating more accurate predictions.
        """
        if not self.results:
            return {}

        # Filter results that have MAE values
        results_with_mae = [r for r in self.results if 'mae' in r and r['mae'] is not None]

        if results_with_mae:
            # Select model with lowest MAE (lower is better)
            best = min(results_with_mae, key=lambda x: x.get('mae', float('inf')))
        else:
            # Fallback: if no MAE available, use MSE as alternative
            results_with_mse = [r for r in self.results if 'mse' in r and r['mse'] is not None]
            if results_with_mse:
                best = min(results_with_mse, key=lambda x: x.get('mse', float('inf')))
            else:
                # Last resort: use first result
                best = self.results[0] if self.results else {}

        return best
    
    def summary_table(self) -> pd.DataFrame:
        """
        Generate summary table of all models.
        
        Returns:
            DataFrame with model results
        """
        if not self.results:
            return pd.DataFrame(columns=['model', 'r_squared', 'mse', 'mae'])
        
        return pd.DataFrame(self.results)

