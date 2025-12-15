"""
Preprocessing Runner

Orchestrates all preprocessing steps and statistical tests.
"""

import pandas as pd
from typing import Dict, Any, List
from autostat.preprocessing.missing import MissingDataHandler
from autostat.preprocessing.scaling import ScalingHandler
from autostat.preprocessing.stationarity import StationarityTests
from autostat.preprocessing.mco_assumptions import MCOAssumptionTests


class PreprocessingRunner:
    """
    Orchestrates preprocessing pipeline.
    
    Steps:
    1. Handle missing data
    2. Test MCO assumptions
    3. Test stationarity (for time series)
    4. Scale/normalize data
    5. Generate preprocessing report
    """
    
    def __init__(self, metadata: Dict[str, Any], label: str = "default"):
        """
        Args:
            metadata: Metadata about the dataset
            label: Identifier for this preprocessing run
        """
        self.metadata = metadata
        self.label = label
        self.results = []
        
        # Initialize handlers
        self.missing_handler = MissingDataHandler()
        self.scaling_handler = ScalingHandler()
        self.stationarity_tests = StationarityTests()
        self.mco_tests = MCOAssumptionTests(
            data_type=metadata.get('data_type', 'cross_section'),
            panel_type=metadata.get('panel_type', 'unfixed')
        )
    
    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute full preprocessing pipeline.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary containing:
            - processed_df: Preprocessed DataFrame
            - test_results: All test results
            - transformations: Applied transformations
        """
        processed_df = df.copy()
        
        # 1. Handle missing data
        missing_report = self.missing_handler.analyze(processed_df)
        if missing_report['has_missing']:
            processed_df = self.missing_handler.handle(processed_df)
        
        self.results.append({
            'test': 'Missing Data Analysis',
            'result': missing_report
        })
        
        # 2. Test MCO assumptions
        mco_results = self.mco_tests.run_all_tests(processed_df)
        self.results.extend(mco_results)
        
        # 3. Test stationarity (if time series or panel)
        integration_orders = {}
        if self.metadata['data_type'] in ['time_series', 'panel']:
            stationarity_results = self.stationarity_tests.run_all_tests(processed_df)
            self.results.extend(stationarity_results)

            # Calculate order of integration for each numeric variable
            import numpy as np
            numeric_cols = processed_df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                integration_result = self.stationarity_tests.order_of_integration(processed_df[col])
                integration_orders[col] = integration_result
                self.results.append({
                    'test': f'Order of Integration - {col}',
                    'result': integration_result,
                    'passed': integration_result.get('is_stationary', False)
                })
        
        # 4. Scale data (optional, based on metadata)
        if self.metadata.get('size_category') == 'big':
            processed_df = self.scaling_handler.scale(processed_df)
            self.results.append({
                'test': 'Data Scaling',
                'result': 'Applied StandardScaler'
            })
        
        return {
            'processed_df': processed_df,
            'test_results': self.results,
            'transformations': self._get_transformations(),
            'integration_orders': integration_orders
        }
    
    def summary_table(self) -> pd.DataFrame:
        """
        Generate summary table of all preprocessing tests.
        
        Returns:
            DataFrame with test results
        """
        if not self.results:
            return pd.DataFrame(columns=['test', 'result', 'passed'])
        
        summary_data = []
        for result in self.results:
            if isinstance(result.get('result'), dict):
                summary_data.append({
                    'test': result['test'],
                    'result': str(result['result']),
                    'passed': result.get('passed', None)
                })
            else:
                summary_data.append({
                    'test': result['test'],
                    'result': result.get('result', 'N/A'),
                    'passed': result.get('passed', None)
                })
        
        return pd.DataFrame(summary_data)
    
    def _get_transformations(self) -> List[str]:
        """Get list of applied transformations."""
        transformations = []
        for result in self.results:
            if 'transformation' in result:
                transformations.append(result['transformation'])
        return transformations
    
    def add(self, value: Dict[str, Any]):
        """Add a custom test result."""
        self.results.append(value)

