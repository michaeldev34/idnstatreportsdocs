"""
Comprehensive Time Series Example with All KPIs

This example demonstrates the AutoStat framework with a complete time series dataset
that includes columns for calculating KPIs across multiple business domains.
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

# Create comprehensive time series data with columns for all KPIs
data = {
    # Time index
    'date': dates,
    
    # MARKETING KPIs
    'visitors': np.random.poisson(5000, n_periods) + np.arange(n_periods) * 10,  # Growing traffic
    'conversions': np.random.poisson(100, n_periods) + np.arange(n_periods) * 0.5,  # Growing conversions
    'marketing_spend': np.random.normal(1000, 100, n_periods),  # Stable marketing spend
    'revenue': np.random.normal(5000, 500, n_periods) + np.arange(n_periods) * 15,  # Growing revenue
    
    # SALES KPIs
    'orders': np.random.poisson(80, n_periods) + np.arange(n_periods) * 0.3,  # Growing orders
    'deals_won': np.random.poisson(15, n_periods),  # Deals closed
    'opportunities': np.random.poisson(50, n_periods),  # Sales opportunities
    
    # FINANCE KPIs
    'cogs': np.random.normal(2000, 200, n_periods) + np.arange(n_periods) * 5,  # Cost of goods sold
    'expenses': np.random.normal(1500, 150, n_periods),  # Operating expenses
    'net_profit': np.random.normal(1500, 300, n_periods) + np.arange(n_periods) * 8,  # Growing profit
    
    # OPERATIONS KPIs
    'units_produced': np.random.poisson(500, n_periods) + np.arange(n_periods) * 2,  # Production volume
    'production_hours': np.random.normal(160, 20, n_periods),  # Hours worked
    'uptime': np.random.uniform(85, 98, n_periods),  # Equipment uptime %
    'planned_time': np.full(n_periods, 100.0),  # Planned production time
    
    # CUSTOMER KPIs
    'satisfaction_score': np.random.uniform(3.5, 5.0, n_periods),  # CSAT score
    'nps': np.random.randint(30, 80, n_periods),  # Net Promoter Score
    'churn_rate': np.random.uniform(2, 8, n_periods),  # Monthly churn %
    'active_customers': np.random.poisson(1000, n_periods) + np.arange(n_periods) * 5,  # Growing customer base
}

# Create DataFrame
df = pd.DataFrame(data)

# Set date as index for time series
df.set_index('date', inplace=True)

print("=" * 70)
print("COMPREHENSIVE TIME SERIES ANALYSIS")
print("=" * 70)
print(f"\nDataset Shape: {df.shape[0]} periods × {df.shape[1]} metrics")
print(f"Date Range: {df.index[0].date()} to {df.index[-1].date()}")
print("\nColumns included for KPI calculation:")
print("  📊 Marketing: visitors, conversions, marketing_spend, revenue")
print("  💰 Sales: orders, deals_won, opportunities")
print("  💵 Finance: revenue, cogs, expenses, net_profit")
print("  ⚙️  Operations: units_produced, production_hours, uptime")
print("  👥 Customer: satisfaction_score, nps, churn_rate, active_customers")
print("\n" + "=" * 70)

# Generate comprehensive report
print("\n🚀 Generating comprehensive statistical report...")
print("=" * 70)

report_path = generate_report(df, label="Comprehensive Time Series Analysis")

print("\n" + "=" * 70)
print(f"✅ REPORT GENERATED: {report_path}")
print("=" * 70)
print("\nThe report includes:")
print("  ✅ Metadata detection (time series, 200 periods)")
print("  ✅ KPIs across 5 business domains")
print("  ✅ 19+ preprocessing tests")
print("  ✅ Statistical models (Granger causality)")
print("  ✅ 30-period forecast with confidence intervals")
print("  ✅ Embedded visualizations:")
print("     - Time series plots with trend lines")
print("     - Correlation heatmap")
print("     - Distribution plots")
print("  ✅ Plain language interpretation")
print("  ✅ Actionable recommendations")
print("\n" + "=" * 70)
print(f"\n📂 Open the report: {report_path}")
print("=" * 70)

# Display sample of the data
print("\n📊 Sample Data (first 5 periods):")
print(df.head())

print("\n📈 Summary Statistics:")
print(df.describe().round(2))

