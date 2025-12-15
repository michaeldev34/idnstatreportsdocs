"""
Explanation Runner

Orchestrates model interpretation and forecasting.
"""

import pandas as pd
from typing import Dict, Any
from autostat.explanation.plain_language import PlainLanguageExplainer
from autostat.explanation.forecasting import Forecaster
from autostat.explanation.charts import ChartGenerator


class ExplanationRunner:
    """
    Orchestrates explanation generation.
    
    Components:
    - Plain language interpretation
    - Forecasting
    - Visualization
    """
    
    def __init__(self, label: str = "default"):
        """
        Args:
            label: Identifier for this explanation run
        """
        self.label = label
        self.explainer = PlainLanguageExplainer()
        self.forecaster = Forecaster()
        self.chart_generator = ChartGenerator()
    
    def run(self, df: pd.DataFrame, models: Dict[str, Any],
            metadata: Dict[str, Any] = None, preprocessing_results: list = None,
            kpis: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Generate explanations and forecasts.

        Args:
            df: Input DataFrame
            models: Model results from ModelsRunner
            metadata: Optional metadata
            preprocessing_results: Optional preprocessing test results
            kpis: Optional KPI DataFrame

        Returns:
            Dictionary with explanations and forecasts
        """
        results = {}

        # Generate plain language explanation with recommendations
        if models.get('results'):
            best_model = models.get('best_model', {})
            results['interpretation'] = self.explainer.explain_model(best_model, preprocessing_results)

        # Generate forecast
        if metadata and metadata.get('data_type') in ['time_series', 'panel']:
            forecast = self.forecaster.forecast_next_periods(df, models, periods=30)
            results['forecast'] = forecast
            # Add forecast to models for chart generation
            models['forecast'] = forecast

        # Generate charts with metadata and KPIs
        charts = self.chart_generator.generate_charts(df, models, metadata, kpis)
        results['charts'] = charts

        return results
    
    def summary_table(self, results: Dict[str, Any]) -> pd.DataFrame:
        """
        Generate summary table of explanations.
        
        Args:
            results: Results from run()
            
        Returns:
            DataFrame with summary
        """
        summary_data = []
        
        if 'interpretation' in results:
            summary_data.append({
                'component': 'Interpretation',
                'status': 'Complete',
                'details': results['interpretation'][:100] + '...' if len(results['interpretation']) > 100 else results['interpretation']
            })
        
        if 'forecast' in results:
            summary_data.append({
                'component': 'Forecast',
                'status': 'Complete',
                'details': f"{results['forecast'].get('periods', 0)} periods forecasted"
            })
        
        if 'charts' in results:
            summary_data.append({
                'component': 'Charts',
                'status': 'Complete',
                'details': f"{len(results['charts'])} charts generated"
            })
        
        return pd.DataFrame(summary_data)

