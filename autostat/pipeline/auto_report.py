"""
Auto Report Pipeline

Main orchestration for automated statistical reporting.
"""

import pandas as pd
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

from autostat.metadata.detector import MetadataDetector
from autostat.kpis.kpi_runner import KPIsRunner
from autostat.preprocessing.preprocessing_runner import PreprocessingRunner
from autostat.modeling.model_runner import ModelsRunner
from autostat.explanation.explanation_runner import ExplanationRunner
from autostat.report.pdf_builder import PDFReportBuilder
from autostat.utils.validators import DataValidator


class AutoStatReport:
    """
    Main pipeline for automated statistical analysis and reporting.

    This class orchestrates the entire analysis workflow:
    1. Metadata detection
    2. KPI calculation
    3. Data preprocessing
    4. Statistical modeling
    5. Result interpretation
    6. PDF report generation

    Example:
        >>> from autostat.pipeline.auto_report import AutoStatReport
        >>> import pandas as pd
        >>>
        >>> df = pd.read_csv('data.csv')
        >>> pipeline = AutoStatReport(label="Q4 Analysis")
        >>> report_path = pipeline.run(df)
        >>> print(f"Report generated: {report_path}")

        # Department-specific analysis
        >>> pipeline = AutoStatReport(label="Marketing Analysis", department="marketing")
        >>> report_path = pipeline.run(df)
    """

    # Department column mappings - columns that belong to each department
    DEPARTMENT_COLUMNS = {
        'marketing': ['visitors', 'conversions', 'marketing_spend', 'ad_spend', 'cost', 'leads', 'traffic', 'cac', 'cpl', 'cpa', 'clicks', 'impressions', 'ctr', 'cpm', 'campaigns'],
        'sales': ['orders', 'deals_won', 'opportunities', 'sales', 'revenue', 'total_sales', 'deal_size', 'win_rate', 'pipeline', 'quota', 'bookings'],
        'finance': ['cogs', 'expenses', 'net_profit', 'profit', 'income', 'cost_of_goods', 'margin', 'ebitda', 'cashflow', 'assets', 'liabilities', 'equity'],
        'operations': ['units_produced', 'production_hours', 'uptime', 'planned_time', 'units', 'production', 'output', 'hours', 'efficiency', 'throughput', 'cycle_time', 'defects', 'yield'],
        'customer': ['satisfaction_score', 'nps', 'churn_rate', 'active_customers', 'satisfaction', 'csat', 'rating', 'ltv', 'retention', 'support_tickets', 'response_time'],
        'hr': ['employees', 'headcount', 'turnover', 'hiring', 'attrition', 'engagement', 'training', 'salary', 'benefits', 'overtime'],
        'product': ['features', 'bugs', 'releases', 'sprints', 'velocity', 'backlog', 'adoption', 'usage', 'dau', 'mau', 'retention'],
        'production': ['production_volume', 'capacity', 'utilization', 'downtime', 'maintenance', 'quality_rate', 'oee', 'scrap_rate', 'inventory'],
        'legal': ['contracts', 'disputes', 'compliance', 'cases', 'settlements', 'legal_cost', 'risk', 'patents', 'trademarks']
    }

    def __init__(self, label: str = "Statistical Analysis Report", department: str = None):
        """
        Initialize the pipeline.

        Args:
            label: Label/title for the analysis
            department: Optional department filter (e.g., 'marketing', 'sales', 'finance', 'operations', 'customer', 'hr', 'product', 'production', 'legal')
                       If None, all departments are analyzed.
        """
        self.label = label
        self.department = department.lower() if department else None
        self.metadata = None
        self.kpis = None
        self.preprocessing_results = None
        self.model_results = None
        self.explanation_results = None

    def _filter_by_department(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter DataFrame to only include columns relevant to the specified department.

        Args:
            df: Input DataFrame

        Returns:
            Filtered DataFrame with only department-relevant columns
        """
        if self.department is None:
            return df

        if self.department not in self.DEPARTMENT_COLUMNS:
            print(f"⚠️  Unknown department '{self.department}'. Available: {list(self.DEPARTMENT_COLUMNS.keys())}")
            return df

        # Get keywords for this department
        dept_keywords = self.DEPARTMENT_COLUMNS[self.department]

        # Find matching columns
        matching_cols = []

        # Always keep date/time columns
        for col in df.columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in ['date', 'time', 'period', 'month', 'year', 'week', 'day', 'index']):
                matching_cols.append(col)
                continue

            # Check if column matches any department keyword
            if any(kw in col_lower for kw in dept_keywords):
                matching_cols.append(col)

        if not matching_cols:
            print(f"⚠️  No columns found for department '{self.department}'. Using all columns.")
            return df

        print(f"   📁 Filtered to {len(matching_cols)} columns for {self.department.capitalize()} department")
        return df[matching_cols]
    
    def run(self, df: pd.DataFrame, 
            skip_kpis: bool = False,
            skip_preprocessing: bool = False,
            skip_modeling: bool = False,
            skip_explanation: bool = False) -> str:
        """
        Execute the complete analysis pipeline.
        
        Args:
            df: Input DataFrame
            skip_kpis: Skip KPI calculation
            skip_preprocessing: Skip preprocessing
            skip_modeling: Skip modeling
            skip_explanation: Skip explanation generation
            
        Returns:
            Path to generated report file
        """
        # Validate input
        DataValidator.validate_dataframe(df)

        print(f"🚀 Starting AutoStat Pipeline: {self.label}")
        print("=" * 60)

        # Apply department filter if specified
        if self.department:
            print(f"\n🎯 Department Filter: {self.department.capitalize()}")
            df = self._filter_by_department(df)

        # Step 1: Detect metadata
        print("\n📊 Step 1/6: Detecting metadata...")
        metadata_detector = MetadataDetector()
        self.metadata = metadata_detector.detect(df)
        self.metadata['department'] = self.department  # Add department to metadata
        print(f"   Data type: {self.metadata['data_type']}")
        print(f"   Size: {self.metadata['n_rows']} rows × {self.metadata['n_cols']} columns")
        print(f"   Category: {self.metadata['size_category']}")
        
        # Step 2: Calculate KPIs
        kpi_series_dict = {}
        if not skip_kpis:
            print("\n📈 Step 2/6: Calculating KPIs...")
            kpi_runner = KPIsRunner(label=self.label)
            self.kpis = kpi_runner.run(df, self.metadata)
            kpi_series_dict = kpi_runner.get_kpi_series()
            print(f"   Calculated {len(self.kpis)} KPIs")

            # Add KPI series to DataFrame for full analysis
            if kpi_series_dict:
                print(f"   Adding {len(kpi_series_dict)} KPI series to analysis")
                df_with_kpis = df.copy()
                for kpi_name, kpi_series in kpi_series_dict.items():
                    # Clean column name for DataFrame
                    col_name = f"KPI_{kpi_name.replace(' ', '_')}"
                    df_with_kpis[col_name] = kpi_series.values
                df = df_with_kpis
        else:
            print("\n⏭️  Step 2/6: Skipping KPIs")
            self.kpis = pd.DataFrame()

        # Step 3: Preprocessing (now includes KPI series)
        if not skip_preprocessing:
            print("\n🔧 Step 3/6: Preprocessing data...")
            preprocessing_runner = PreprocessingRunner(self.metadata, label=self.label)
            self.preprocessing_results = preprocessing_runner.run(df)
            processed_df = self.preprocessing_results['processed_df']
            print(f"   Ran {len(self.preprocessing_results['test_results'])} tests")
        else:
            print("\n⏭️  Step 3/6: Skipping preprocessing")
            processed_df = df
            self.preprocessing_results = {'test_results': [], 'processed_df': df}
        
        # Step 4: Statistical modeling
        if not skip_modeling:
            print("\n🤖 Step 4/6: Running statistical models...")
            model_runner = ModelsRunner(self.metadata, label=self.label)
            self.model_results = model_runner.run(processed_df)
            print(f"   Fitted {self.model_results['models_run']} models")
            if self.model_results.get('best_model'):
                best = self.model_results['best_model']
                print(f"   Best model: {best.get('model', 'Unknown')}")
        else:
            print("\n⏭️  Step 4/6: Skipping modeling")
            self.model_results = {'results': [], 'models_run': 0}
        
        # Step 5: Generate explanations
        if not skip_explanation:
            print("\n💡 Step 5/6: Generating explanations...")
            explanation_runner = ExplanationRunner(label=self.label)
            self.explanation_results = explanation_runner.run(
                processed_df, self.model_results, self.metadata,
                preprocessing_results=self.preprocessing_results.get('test_results', []),
                kpis=self.kpis
            )
            print("   Generated interpretations and forecasts")
        else:
            print("\n⏭️  Step 5/6: Skipping explanations")
            self.explanation_results = {}
        
        # Step 6: Generate PDF report
        print("\n📄 Step 6/6: Generating PDF report...")
        pdf_builder = PDFReportBuilder(label=self.label)
        report_path = pdf_builder.build(
            metadata=self.metadata,
            kpis=self.kpis,
            preprocessing=self.preprocessing_results,
            models=self.model_results,
            explanation=self.explanation_results
        )
        
        print("\n" + "=" * 60)
        print(f"✅ Pipeline complete! Report saved to: {report_path}")
        print("=" * 60)
        
        return report_path
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get all analysis results.
        
        Returns:
            Dictionary with all results
        """
        return {
            'metadata': self.metadata,
            'kpis': self.kpis,
            'preprocessing': self.preprocessing_results,
            'models': self.model_results,
            'explanation': self.explanation_results
        }


def generate_report(df: pd.DataFrame, label: str = "Statistical Analysis",
                    department: str = None) -> str:
    """
    Convenience function to generate a report in one line.

    Args:
        df: Input DataFrame
        label: Report label/title
        department: Optional department filter ('marketing', 'sales', 'finance',
                   'operations', 'customer', 'hr', 'product', 'production', 'legal')

    Returns:
        Path to generated report

    Example:
        >>> import pandas as pd
        >>> from autostat import generate_report
        >>>
        >>> df = pd.read_csv('sales_data.csv')
        >>> report = generate_report(df, label="Q4 Sales Analysis")

        # Department-specific analysis
        >>> report = generate_report(df, label="Marketing Report", department="marketing")
    """
    pipeline = AutoStatReport(label=label, department=department)
    return pipeline.run(df)

