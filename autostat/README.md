# AutoStat - Enterprise Statistical Automation Engine

**Production-grade statistical analysis and reporting framework** for automated data analysis, KPI tracking, preprocessing, modeling, and PDF report generation.

Based on the architecture from `StatsReportsDocs.py` but refactored into a clean, modular, enterprise-ready structure.

---

## 🎯 Features

- **Automatic Metadata Detection**: Detects data type (time series, cross-section, panel), size category, and linearity
- **Multi-Domain KPIs**: Pre-built KPIs for Marketing, Operations, Product, Customer, Finance, HR, and more
- **Comprehensive Preprocessing**: Missing data handling, scaling, stationarity tests, MCO assumption validation
- **Intelligent Model Selection**: Automatically selects appropriate models based on data characteristics
- **Plain Language Explanations**: Converts statistical results to human-readable interpretations
- **Forecasting**: 30-period forecasts for time series data
- **PDF Reports**: Professional HTML/PDF reports with all results

---

## 📁 Architecture

```
autostat/
├── __init__.py                 # Main package entry point
├── pipeline/                   # Orchestration
│   ├── auto_report.py         # Main pipeline (single function call)
├── metadata/                   # Data type & linearity detection
│   ├── detector.py
│   ├── type_detection.py
│   └── linearity.py
├── kpis/                       # Business KPIs by domain
│   ├── kpi_runner.py
│   ├── marketing.py
│   ├── operations.py
│   ├── product.py
│   ├── customer.py
│   └── ... (9 modules total)
├── preprocessing/              # Data preprocessing & tests
│   ├── preprocessing_runner.py
│   ├── missing.py
│   ├── scaling.py
│   ├── stationarity.py
│   └── mco_assumptions.py
├── modeling/                   # Statistical models
│   ├── model_runner.py
│   ├── linear_models.py
│   ├── time_series_models.py
│   ├── bigdata_models.py
│   └── panel_models.py
├── explanation/                # Interpretation & forecasting
│   ├── explanation_runner.py
│   ├── plain_language.py
│   ├── forecasting.py
│   └── charts.py
├── report/                     # PDF generation
│   └── pdf_builder.py
└── utils/                      # Utilities
    ├── validators.py
    ├── io.py
    └── formatter.py
```

---

## 🚀 Quick Start

### One-Line Usage

```python
from autostat import generate_report
import pandas as pd

df = pd.read_csv('your_data.csv')
report_path = generate_report(df, label="Q4 Analysis")
```

### Full Pipeline Control

```python
from autostat.pipeline.auto_report import AutoStatReport
import pandas as pd

# Load data
df = pd.read_csv('sales_data.csv')

# Create pipeline
pipeline = AutoStatReport(label="Sales Analysis 2024")

# Run complete analysis
report_path = pipeline.run(df)

# Access individual results
results = pipeline.get_results()
print(results['metadata'])
print(results['kpis'])
print(results['models'])
```

---

## 📊 Data Type Support

AutoStat automatically detects and handles:

1. **Time Series**: Sequential observations over time
   - Models: ARIMA, ECM, VECM, Granger Causality
   
2. **Cross-Section**: Single snapshot across entities
   - Models: OLS, Random Forest, XGBoost
   
3. **Panel Data**: Multiple entities over time
   - Models: Fixed Effects, Random Effects

---

## 🔧 Size-Based Model Selection

- **Small Data** (<5,000 rows): Classical statistical models
  - Multiple Linear Regression
  - ECM, VECM
  - Granger Causality

- **Big Data** (≥5,000 rows): Machine learning models
  - Random Forest
  - XGBoost
  - Neural Networks
  - ARIMA, GARCH, VARIMA

---

## 📈 Built-in KPIs

### Marketing
- Conversion Rate
- Customer Acquisition Cost (CAC)
- Marketing ROI

### Operations
- Overall Equipment Effectiveness (OEE)
- Units per Hour
- Throughput

### Product
- Yield Rate
- Defect Rate
- Scrap Rate

### Customer
- Customer Satisfaction (CSAT)
- Retention Rate
- Churn Rate

*Plus Finance, HR, Sales, Legal, and more...*

---

## 🧪 Preprocessing Tests

- **MCO Assumptions**:
  - Aleatory sample
  - Independent observations
  - Conditional mean zero
  - Homoscedasticity
  - No autocorrelation
  - Normality of residuals

- **Stationarity Tests**:
  - Augmented Dickey-Fuller (ADF)
  - KPSS
  - Trend detection

- **Data Quality**:
  - Missing data analysis
  - Outlier detection
  - Scaling/normalization

---

## 📄 Report Output

Generated reports include:

1. **Dataset Metadata**: Type, size, characteristics
2. **KPI Dashboard**: All calculated metrics
3. **Preprocessing Results**: Test results and transformations
4. **Model Performance**: Fitted models with metrics
5. **Interpretation**: Plain language explanations
6. **Forecast**: 30-period predictions (for time series)
7. **Visualizations**: Charts and plots

---

## 🔌 Extensibility

### Add Custom KPIs

```python
from autostat.kpis.kpi_runner import KPIsRunner

runner = KPIsRunner()
runner.add({
    'category': 'Custom',
    'kpi': 'My Metric',
    'value': 42.5,
    'unit': '%'
})
```

### Add Custom Models

Create a new file in `autostat/modeling/` and register it in `model_runner.py`.

---

## 📦 Dependencies

**Core**:
- pandas
- numpy

**Statistical**:
- statsmodels
- scipy

**Machine Learning**:
- scikit-learn
- (optional) xgboost

**Visualization**:
- matplotlib

---

## 🎓 Example Use Cases

1. **SaaS Analytics**: Pricing optimization, churn prediction
2. **Manufacturing**: OEE tracking, quality control
3. **Marketing**: Campaign ROI, conversion analysis
4. **Finance**: Time series forecasting, risk modeling
5. **Operations**: Throughput optimization, capacity planning

---

## 📝 License

Enterprise use - IDN Products

---

## 🤝 Original Source

Refactored from `StatsReportsDocs.py` with enterprise architecture patterns.

