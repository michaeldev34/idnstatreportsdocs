"""
AutoStat Example Usage

Demonstrates how to use the AutoStat framework for automated statistical analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import AutoStat
from autostat import generate_report
from autostat.pipeline.auto_report import AutoStatReport


def create_sample_time_series_data():
    """Create sample time series data for demonstration."""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    df = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 100, 100) + np.arange(100) * 5,  # Trend
        'marketing_spend': np.random.normal(500, 50, 100),
        'visitors': np.random.normal(5000, 500, 100),
        'conversions': np.random.normal(100, 10, 100)
    })
    
    df.set_index('date', inplace=True)
    return df


def create_sample_cross_section_data():
    """Create sample cross-section data for demonstration."""
    np.random.seed(42)
    
    df = pd.DataFrame({
        'company_id': range(1, 201),
        'revenue': np.random.normal(1000000, 200000, 200),
        'employees': np.random.randint(10, 500, 200),
        'marketing_budget': np.random.normal(50000, 10000, 200),
        'customer_satisfaction': np.random.uniform(3.0, 5.0, 200),
        'defect_rate': np.random.uniform(0.01, 0.10, 200)
    })
    
    return df


def example_1_one_line_usage():
    """Example 1: Simplest usage - one line."""
    print("\n" + "="*60)
    print("EXAMPLE 1: One-Line Usage")
    print("="*60)
    
    # Create sample data
    df = create_sample_time_series_data()
    
    # Generate report in one line
    report_path = generate_report(df, label="Time Series Analysis Example")
    
    print(f"\n✅ Report generated: {report_path}")


def example_2_full_pipeline_control():
    """Example 2: Full pipeline with access to intermediate results."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Full Pipeline Control")
    print("="*60)
    
    # Create sample data
    df = create_sample_cross_section_data()
    
    # Create pipeline
    pipeline = AutoStatReport(label="Cross-Section Analysis Example")
    
    # Run pipeline
    report_path = pipeline.run(df)
    
    # Access intermediate results
    results = pipeline.get_results()
    
    print("\n📊 Metadata:")
    print(f"   Data type: {results['metadata']['data_type']}")
    print(f"   Size: {results['metadata']['n_rows']} rows")
    print(f"   Linearity: {'Linear' if results['metadata']['is_linear'] else 'Non-linear'}")
    
    print("\n📈 KPIs:")
    if not results['kpis'].empty:
        print(results['kpis'].head())
    
    print("\n🤖 Models:")
    if results['models']['results']:
        for model in results['models']['results']:
            print(f"   - {model.get('model', 'Unknown')}: R² = {model.get('r_squared', 'N/A')}")
    
    print(f"\n✅ Report generated: {report_path}")


def example_3_selective_execution():
    """Example 3: Skip certain pipeline steps."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Selective Execution")
    print("="*60)
    
    # Create sample data
    df = create_sample_time_series_data()
    
    # Create pipeline
    pipeline = AutoStatReport(label="Selective Analysis")
    
    # Run only metadata, preprocessing, and modeling (skip KPIs and explanation)
    report_path = pipeline.run(
        df,
        skip_kpis=True,
        skip_explanation=True
    )
    
    print(f"\n✅ Report generated: {report_path}")


def example_4_custom_kpis():
    """Example 4: Add custom KPIs."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom KPIs")
    print("="*60)
    
    from autostat.kpis.kpi_runner import KPIsRunner
    
    # Create sample data
    df = create_sample_cross_section_data()
    
    # Create KPI runner
    kpi_runner = KPIsRunner(label="Custom KPIs")
    
    # Calculate standard KPIs
    kpis = kpi_runner.run(df)
    
    # Add custom KPI
    kpi_runner.add({
        'category': 'Custom',
        'kpi': 'Revenue per Employee',
        'value': df['revenue'].sum() / df['employees'].sum(),
        'unit': '$/employee'
    })
    
    # Get summary
    summary = kpi_runner.summary_table()
    print("\n📊 KPI Summary:")
    print(summary)


def example_5_individual_modules():
    """Example 5: Use individual modules separately."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Individual Module Usage")
    print("="*60)
    
    from autostat.metadata.detector import MetadataDetector
    from autostat.preprocessing.missing import MissingDataHandler
    from autostat.modeling.linear_models import LinearModels
    
    # Create sample data
    df = create_sample_cross_section_data()
    
    # 1. Detect metadata
    print("\n1️⃣ Detecting metadata...")
    detector = MetadataDetector()
    metadata = detector.detect(df)
    print(detector.summary(metadata))
    
    # 2. Handle missing data
    print("\n2️⃣ Analyzing missing data...")
    missing_handler = MissingDataHandler()
    missing_report = missing_handler.analyze(df)
    print(f"   Missing: {missing_report['missing_percentage']:.2f}%")
    
    # 3. Fit linear model
    print("\n3️⃣ Fitting linear model...")
    linear_models = LinearModels()
    model_result = linear_models.multiple_linear_regression(df, target_col='revenue')
    
    if 'error' not in model_result:
        print(f"   Model: {model_result['model']}")
        print(f"   R²: {model_result['r_squared']:.4f}")
        print(f"   Observations: {model_result['n_obs']}")


def main():
    """Run all examples."""
    print("\n" + "🚀 " * 20)
    print("AutoStat Framework - Example Usage")
    print("🚀 " * 20)
    
    # Run examples
    example_1_one_line_usage()
    example_2_full_pipeline_control()
    example_3_selective_execution()
    example_4_custom_kpis()
    example_5_individual_modules()
    
    print("\n" + "✅ " * 20)
    print("All examples completed successfully!")
    print("✅ " * 20 + "\n")


if __name__ == "__main__":
    main()

