"""
KPI Runner

Orchestrates KPI calculation across all business units.
Calculates per-observation KPIs for time series, panel, and cross-sectional data.
"""

import pandas as pd
from typing import Dict, List, Any
from autostat.kpis.production import ProductionKPIs
from autostat.kpis.marketing import MarketingKPIs
from autostat.kpis.sales import SalesKPIs
from autostat.kpis.finance import FinanceKPIs
from autostat.kpis.operations import OperationsKPIs
from autostat.kpis.hr import HRKPIs
from autostat.kpis.product import ProductKPIs
from autostat.kpis.customer import CustomerKPIs
from autostat.kpis.legal import LegalKPIs


class KPIsRunner:
    """
    Orchestrates KPI calculation across all business units.

    Automatically detects applicable KPIs based on data structure
    and calculates per-observation metrics with summary statistics.
    """

    def __init__(self, label: str = "default"):
        """
        Args:
            label: Identifier for this KPI run
        """
        self.label = label
        self.results = []
        self.kpi_series = {}  # Store per-observation KPI series

        # Initialize all KPI modules
        self.production = ProductionKPIs()
        self.marketing = MarketingKPIs()
        self.sales = SalesKPIs()
        self.finance = FinanceKPIs()
        self.operations = OperationsKPIs()
        self.hr = HRKPIs()
        self.product = ProductKPIs()
        self.customer = CustomerKPIs()
        self.legal = LegalKPIs()

    def run(self, df: pd.DataFrame, metadata: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Calculate all applicable KPIs per observation.

        Args:
            df: Input DataFrame
            metadata: Optional metadata about the dataset (includes data_type)

        Returns:
            DataFrame with KPI summary statistics
        """
        self.results = []
        self.kpi_series = {}

        # Determine data type from metadata
        data_type = 'time_series'  # default
        if metadata and 'data_type' in metadata:
            data_type = metadata['data_type']

        # Try each KPI module
        self._run_module(self.production, df, "Production", data_type)
        self._run_module(self.marketing, df, "Marketing", data_type)
        self._run_module(self.sales, df, "Sales", data_type)
        self._run_module(self.finance, df, "Finance", data_type)
        self._run_module(self.operations, df, "Operations", data_type)
        self._run_module(self.hr, df, "HR", data_type)
        self._run_module(self.product, df, "Product", data_type)
        self._run_module(self.customer, df, "Customer", data_type)
        self._run_module(self.legal, df, "Legal", data_type)

        return self.summary_table()

    def _run_module(self, module, df: pd.DataFrame, module_name: str, data_type: str):
        """Run a single KPI module and collect results."""
        try:
            # Pass data_type to calculate_all
            module_results = module.calculate_all(df, data_type)
            for result in module_results:
                result['category'] = module_name

                # Extract series data if present and store separately
                if 'series' in result and result['series'] is not None:
                    kpi_name = result['kpi']
                    self.kpi_series[f"{module_name}_{kpi_name}"] = result['series']
                    # Remove series from result dict for the summary table
                    result_copy = {k: v for k, v in result.items() if k != 'series'}
                    self.results.append(result_copy)
                else:
                    self.results.append(result)
        except Exception as e:
            # Log error but continue with other modules
            self.results.append({
                'category': module_name,
                'kpi': 'Error',
                'value': None,
                'error': str(e)
            })

    def summary_table(self) -> pd.DataFrame:
        """
        Generate summary table of all KPIs.

        Returns:
            DataFrame with columns: category, kpi, mean, median, std, min, max, current, unit
        """
        if not self.results:
            return pd.DataFrame(columns=['category', 'kpi', 'mean', 'median', 'std', 'min', 'max', 'unit'])

        # Create summary DataFrame
        df = pd.DataFrame(self.results)

        # Reorder columns for clarity
        desired_order = ['category', 'kpi', 'mean', 'median', 'current', 'std', 'min', 'max', 'n_observations', 'unit']
        available_cols = [col for col in desired_order if col in df.columns]
        other_cols = [col for col in df.columns if col not in desired_order]
        df = df[available_cols + other_cols]

        return df

    def get_kpi_series(self) -> Dict[str, pd.Series]:
        """Get all per-observation KPI series."""
        return self.kpi_series

    def add(self, value: Dict[str, Any]):
        """Add a custom KPI result."""
        self.results.append(value)

