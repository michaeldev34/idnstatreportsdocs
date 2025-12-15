"""
KPI Runner

Orchestrates KPI calculation across all business units.
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
    and calculates relevant metrics.
    """
    
    def __init__(self, label: str = "default"):
        """
        Args:
            label: Identifier for this KPI run
        """
        self.label = label
        self.results = []
        
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
        Calculate all applicable KPIs.
        
        Args:
            df: Input DataFrame
            metadata: Optional metadata about the dataset
            
        Returns:
            DataFrame with KPI results
        """
        self.results = []
        
        # Try each KPI module
        self._run_module(self.production, df, "Production")
        self._run_module(self.marketing, df, "Marketing")
        self._run_module(self.sales, df, "Sales")
        self._run_module(self.finance, df, "Finance")
        self._run_module(self.operations, df, "Operations")
        self._run_module(self.hr, df, "HR")
        self._run_module(self.product, df, "Product")
        self._run_module(self.customer, df, "Customer")
        self._run_module(self.legal, df, "Legal")
        
        return self.summary_table()
    
    def _run_module(self, module, df: pd.DataFrame, module_name: str):
        """Run a single KPI module and collect results."""
        try:
            module_results = module.calculate_all(df)
            for result in module_results:
                result['category'] = module_name
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
            DataFrame with columns: category, kpi, value, unit
        """
        if not self.results:
            return pd.DataFrame(columns=['category', 'kpi', 'value', 'unit'])
        
        return pd.DataFrame(self.results)
    
    def add(self, value: Dict[str, Any]):
        """Add a custom KPI result."""
        self.results.append(value)

