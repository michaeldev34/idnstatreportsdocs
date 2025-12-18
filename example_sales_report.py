"""
Sales Department Report Example

This example demonstrates generating a sales-specific report using
the department filtering feature of the AutoStat framework.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from autostat import generate_report

# Set random seed for reproducibility
np.random.seed(123)

# Generate 200 time periods (e.g., daily data for ~6-7 months)
n_periods = 200
dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(n_periods)]

# Create comprehensive sales data
data = {
    # Time index
    'date': dates,
    
    # SALES METRICS - Core
    'orders': np.random.poisson(150, n_periods) + np.arange(n_periods) * 0.8,
    'revenue': np.random.normal(50000, 5000, n_periods) + np.arange(n_periods) * 200,
    'deals_won': np.random.poisson(25, n_periods) + np.arange(n_periods) * 0.15,
    'opportunities': np.random.poisson(80, n_periods) + np.arange(n_periods) * 0.3,
    
    # SALES METRICS - Pipeline
    'pipeline': np.random.normal(200000, 20000, n_periods) + np.arange(n_periods) * 500,
    'bookings': np.random.normal(45000, 4500, n_periods) + np.arange(n_periods) * 180,
    'total_sales': np.random.normal(48000, 4800, n_periods) + np.arange(n_periods) * 190,
    
    # OTHER DEPARTMENT DATA (will be filtered out for sales)
    'visitors': np.random.poisson(5000, n_periods),
    'conversions': np.random.poisson(100, n_periods),
    'marketing_spend': np.random.normal(1000, 100, n_periods),
    'cogs': np.random.normal(20000, 2000, n_periods),
    'expenses': np.random.normal(15000, 1500, n_periods),
    'satisfaction_score': np.random.uniform(3.5, 5.0, n_periods),
}

# Create DataFrame
df = pd.DataFrame(data)
df.set_index('date', inplace=True)

print("=" * 70)
print("SALES DEPARTMENT REPORT")
print("=" * 70)
print(f"\nOriginal Dataset: {df.shape[0]} periods × {df.shape[1]} metrics")
print(f"Date Range: {df.index[0].date()} to {df.index[-1].date()}")
print("\nSales columns that will be included:")
print("  📊 orders, revenue, deals_won, opportunities")
print("  📈 pipeline, bookings, total_sales")
print("\nOther columns (will be filtered out):")
print("  ❌ visitors, conversions, marketing_spend, cogs, expenses, satisfaction_score")
print("\n" + "=" * 70)

# Generate sales-specific report using department filter
print("\n🚀 Generating Sales Department Report...")
print("=" * 70)

report_path = generate_report(df, label="Sales Department Analysis", department="sales")

print("\n" + "=" * 70)
print(f"✅ SALES REPORT GENERATED: {report_path}")
print("=" * 70)

print("\nThe report includes:")
print("  ✅ Sales-specific KPIs only")
print("  ✅ Average Order Value (AOV), Sales Growth Rate, Win Rate")
print("  ✅ Time series analysis for sales metrics")
print("  ✅ Stationarity tests with majority voting")
print("  ✅ Forecasts for sales performance")
print("  ✅ Sales correlation heatmap")
print("  ✅ Sales distribution plots")
print("\n" + "=" * 70)

