# AutoStat Setup Guide

Complete guide to setting up and using the AutoStat framework.

---

## 📋 Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Architecture Overview](#architecture-overview)
4. [Module Documentation](#module-documentation)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation

```python
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor

print("✅ All dependencies installed successfully!")
```

### Step 3: Add AutoStat to Python Path

**Option A: Install as package (recommended)**
```bash
cd /path/to/idnproducts
pip install -e .
```

**Option B: Add to PYTHONPATH**
```python
import sys
sys.path.append('/path/to/idnproducts')
```

---

## 🚀 Quick Start

### Minimal Example

```python
from autostat import generate_report
import pandas as pd

# Load your data
df = pd.read_csv('your_data.csv')

# Generate report
report = generate_report(df, label="My Analysis")
print(f"Report saved to: {report}")
```

### Run Example Script

```bash
python example_usage.py
```

---

## 🏗️ Architecture Overview

### Pipeline Flow

```
Input DataFrame
    ↓
1. Metadata Detection
    ↓
2. KPI Calculation
    ↓
3. Preprocessing & Tests
    ↓
4. Statistical Modeling
    ↓
5. Explanation & Forecasting
    ↓
6. PDF Report Generation
    ↓
Output: HTML/PDF Report
```

### Module Responsibilities

| Module | Responsibility | Key Files |
|--------|---------------|-----------|
| `metadata/` | Data type detection | `detector.py`, `type_detection.py`, `linearity.py` |
| `kpis/` | Business metrics | `kpi_runner.py`, `marketing.py`, `operations.py`, etc. |
| `preprocessing/` | Data cleaning & tests | `preprocessing_runner.py`, `mco_assumptions.py` |
| `modeling/` | Statistical models | `model_runner.py`, `linear_models.py`, `time_series_models.py` |
| `explanation/` | Interpretation | `plain_language.py`, `forecasting.py` |
| `report/` | PDF generation | `pdf_builder.py` |
| `pipeline/` | Orchestration | `auto_report.py` |

---

## 📚 Module Documentation

### 1. Metadata Detection

**Purpose**: Automatically detect data characteristics

```python
from autostat.metadata.detector import MetadataDetector

detector = MetadataDetector()
metadata = detector.detect(df)

print(metadata)
# {
#   'data_type': 'time_series',
#   'panel_type': None,
#   'size_category': 'small',
#   'is_linear': True,
#   'has_missing': False
# }
```

### 2. KPI Calculation

**Purpose**: Calculate business KPIs by domain

```python
from autostat.kpis.kpi_runner import KPIsRunner

runner = KPIsRunner(label="Q4 KPIs")
kpis = runner.run(df, metadata)

print(kpis)
# DataFrame with columns: category, kpi, value, unit
```

**Supported Domains**:
- Marketing (CAC, Conversion Rate, ROI)
- Operations (OEE, Throughput)
- Product (Yield, Defect Rate)
- Customer (CSAT, Retention, Churn)
- Finance, HR, Sales, Legal

### 3. Preprocessing

**Purpose**: Clean data and validate assumptions

```python
from autostat.preprocessing.preprocessing_runner import PreprocessingRunner

runner = PreprocessingRunner(metadata, label="Preprocessing")
results = runner.run(df)

processed_df = results['processed_df']
test_results = results['test_results']
```

**Tests Performed**:
- Missing data analysis
- MCO assumptions (6 tests)
- Stationarity (ADF, KPSS)
- Scaling/normalization

### 4. Modeling

**Purpose**: Fit appropriate statistical models

```python
from autostat.modeling.model_runner import ModelsRunner

runner = ModelsRunner(metadata, label="Models")
results = runner.run(processed_df)

best_model = results['best_model']
all_models = results['results']
```

**Model Selection Logic**:

| Data Type | Size | Models |
|-----------|------|--------|
| Time Series | Small | ECM, VECM, Granger |
| Time Series | Big | ARIMA, GARCH, VARIMA |
| Cross-Section | Small | OLS |
| Cross-Section | Big | Random Forest, XGBoost |
| Panel | Any | Fixed/Random Effects |

### 5. Explanation

**Purpose**: Interpret results and forecast

```python
from autostat.explanation.explanation_runner import ExplanationRunner

runner = ExplanationRunner(label="Explanation")
results = runner.run(df, model_results, metadata)

interpretation = results['interpretation']
forecast = results['forecast']
charts = results['charts']
```

### 6. Report Generation

**Purpose**: Create professional PDF reports

```python
from autostat.report.pdf_builder import PDFReportBuilder

builder = PDFReportBuilder(label="Q4 Report")
report_path = builder.build(
    metadata=metadata,
    kpis=kpis,
    preprocessing=preprocessing_results,
    models=model_results,
    explanation=explanation_results
)
```

---

## 🎓 Advanced Usage

### Custom KPI Module

Create `autostat/kpis/custom.py`:

```python
import pandas as pd
from typing import List, Dict, Any

class CustomKPIs:
    def calculate_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        results = []
        
        # Your custom KPI logic
        results.append({
            'kpi': 'My Custom Metric',
            'value': df['column'].mean(),
            'unit': 'units'
        })
        
        return results
```

Register in `kpi_runner.py`:
```python
from autostat.kpis.custom import CustomKPIs

self.custom = CustomKPIs()
```

### Custom Model

Create `autostat/modeling/custom_models.py`:

```python
import pandas as pd
from typing import Dict, Any

class CustomModels:
    def my_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        # Your model logic
        return {
            'model': 'My Custom Model',
            'r_squared': 0.85,
            # ... other metrics
        }
```

### Selective Pipeline Execution

```python
pipeline = AutoStatReport(label="Selective")

# Skip KPIs and explanations
report = pipeline.run(
    df,
    skip_kpis=True,
    skip_explanation=True
)
```

---

## 🐛 Troubleshooting

### Issue: "statsmodels not installed"

```bash
pip install statsmodels scipy
```

### Issue: "No module named 'autostat'"

Add to Python path:
```python
import sys
sys.path.append('/path/to/idnproducts')
```

Or install as package:
```bash
pip install -e .
```

### Issue: "Insufficient numeric columns"

Ensure your DataFrame has at least 2 numeric columns for modeling.

### Issue: Charts not generating

```bash
pip install matplotlib
```

---

## 📞 Support

For issues or questions:
1. Check `example_usage.py` for working examples
2. Review module docstrings
3. Check `StatsReportsDocs.py` for original logic

---

## 🎯 Next Steps

1. ✅ Run `example_usage.py`
2. ✅ Try with your own data
3. ✅ Customize KPIs for your domain
4. ✅ Add custom models if needed
5. ✅ Integrate into your workflow

---

**Happy Analyzing! 📊**

