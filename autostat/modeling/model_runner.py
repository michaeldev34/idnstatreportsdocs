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


class ModelsRunner:
    """
    Orchestrates model selection and execution.
    
    Automatically selects appropriate models based on:
    - Data type (time_series, cross_section, panel)
    - Data size (small <5000, big >=5000)
    - Linearity (linear vs non-linear)
    """
    
    def __init__(self, metadata: Dict[str, Any], label: str = "default"):
        """
        Args:
            metadata: Metadata about the dataset
            label: Identifier for this modeling run
        """
        self.metadata = metadata
        self.label = label
        self.results = []
        
        # Initialize model modules
        self.linear_models = LinearModels()
        self.nonlinear_models = NonlinearModels()
        self.time_series_models = TimeSeriesModels()
        self.panel_models = PanelModels()
        self.bigdata_models = BigDataModels()
    
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
        
        return {
            'models_run': len(self.results),
            'results': self.results,
            'best_model': self._select_best_model()
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
    
    def _select_best_model(self) -> Dict[str, Any]:
        """Select best model based on performance metrics."""
        if not self.results:
            return {}
        
        # Simple selection: highest R² or lowest error
        best = max(self.results, key=lambda x: x.get('r_squared', 0))
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

