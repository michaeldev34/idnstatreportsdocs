"""
Marketing Department Report Example

This example demonstrates generating a marketing-specific report using
the department filtering feature of the AutoStat framework.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from autostat import generate_report

# Set random seed for reproducibility
np.random.seed(42)

# Generate 200 time periods (e.g., daily data for ~6-7 months)
n_periods = 200
dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(n_periods)]

# Create comprehensive marketing data
data = {
    # Time index
    'date': dates,
    
    # MARKETING METRICS - Core
    'visitors': np.random.poisson(5000, n_periods) + np.arange(n_periods) * 10,
    'conversions': np.random.poisson(100, n_periods) + np.arange(n_periods) * 0.5,
    'marketing_spend': np.random.normal(1000, 100, n_periods),
    'revenue': np.random.normal(5000, 500, n_periods) + np.arange(n_periods) * 15,
    
    # MARKETING METRICS - Traffic & Engagement
    'leads': np.random.poisson(200, n_periods) + np.arange(n_periods) * 1.2,
    'traffic': np.random.poisson(8000, n_periods) + np.arange(n_periods) * 20,
    'ad_spend': np.random.normal(500, 50, n_periods),
    'cost': np.random.normal(800, 80, n_periods),
    
    # OTHER DEPARTMENT DATA (will be filtered out)
    'orders': np.random.poisson(80, n_periods),
    'deals_won': np.random.poisson(15, n_periods),
    'cogs': np.random.normal(2000, 200, n_periods),
    'expenses': np.random.normal(1500, 150, n_periods),
    'satisfaction_score': np.random.uniform(3.5, 5.0, n_periods),
    'nps': np.random.randint(30, 80, n_periods),
}

# Create DataFrame
df = pd.DataFrame(data)
df.set_index('date', inplace=True)

print("=" * 70)
print("MARKETING DEPARTMENT REPORT")
print("=" * 70)
print(f"\nOriginal Dataset: {df.shape[0]} periods × {df.shape[1]} metrics")
print(f"Date Range: {df.index[0].date()} to {df.index[-1].date()}")
print("\nMarketing columns that will be included:")
print("  📊 visitors, conversions, marketing_spend, revenue")
print("  📈 leads, traffic, ad_spend, cost")
print("\nOther columns (will be filtered out):")
print("  ❌ orders, deals_won, cogs, expenses, satisfaction_score, nps")
print("\n" + "=" * 70)

# Generate marketing-specific report using department filter
print("\n🚀 Generating Marketing Department Report...")
print("=" * 70)

report_path = generate_report(df, label="Marketing Department Analysis", department="marketing")

print("\n" + "=" * 70)
print(f"✅ MARKETING REPORT GENERATED: {report_path}")
print("=" * 70)

print("\nThe report includes:")
print("  ✅ Marketing-specific KPIs only")
print("  ✅ Conversion Rate, ROI, Cost Per Acquisition")
print("  ✅ Time series analysis for marketing metrics")
print("  ✅ Stationarity tests with majority voting")
print("  ✅ Forecasts for marketing performance")
print("  ✅ Marketing correlation heatmap")
print("  ✅ Marketing distribution plots")
print("\n" + "=" * 70)

