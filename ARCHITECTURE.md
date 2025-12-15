# AutoStat Architecture Documentation

**Enterprise-grade statistical automation framework** - Complete technical architecture.

---

## 🎯 Design Principles

### 1. Single Responsibility Principle (SRP)
Each module has **one clear responsibility**:
- `metadata/` → Data detection only
- `kpis/` → KPI calculation only
- `preprocessing/` → Data cleaning & tests only
- `modeling/` → Statistical models only
- `explanation/` → Interpretation only
- `report/` → PDF generation only
- `pipeline/` → Orchestration only

### 2. Zero Circular Dependencies
Clean import hierarchy:
```
pipeline → explanation → modeling → preprocessing → metadata
                ↓
              kpis
                ↓
              utils
```

### 3. Plug-and-Play Extensibility
- Add new KPIs: Drop file in `kpis/`
- Add new models: Drop file in `modeling/`
- Add new tests: Drop file in `preprocessing/`

### 4. Single Entry Point
```python
from autostat import generate_report
report = generate_report(df, label="Analysis")
```

---

## 📁 Directory Structure

```
autostat/
│
├── __init__.py                      # Package entry point
│
├── pipeline/                        # 🎯 ORCHESTRATION LAYER
│   ├── __init__.py
│   └── auto_report.py              # Main pipeline class
│
├── metadata/                        # 🔍 DETECTION LAYER
│   ├── __init__.py
│   ├── detector.py                 # Main detector orchestrator
│   ├── type_detection.py           # Time series/cross-section/panel
│   └── linearity.py                # Linear vs non-linear
│
├── kpis/                           # 📊 KPI LAYER
│   ├── __init__.py
│   ├── kpi_runner.py               # KPI orchestrator
│   ├── marketing.py                # Marketing KPIs
│   ├── operations.py               # Operations KPIs
│   ├── product.py                  # Product KPIs
│   ├── customer.py                 # Customer KPIs
│   ├── finance.py                  # Finance KPIs
│   ├── sales.py                    # Sales KPIs
│   ├── hr.py                       # HR KPIs
│   ├── legal.py                    # Legal KPIs
│   └── production.py               # Production KPIs
│
├── preprocessing/                   # 🔧 PREPROCESSING LAYER
│   ├── __init__.py
│   ├── preprocessing_runner.py     # Preprocessing orchestrator
│   ├── missing.py                  # Missing data handling
│   ├── scaling.py                  # Normalization/scaling
│   ├── stationarity.py             # Stationarity tests
│   └── mco_assumptions.py          # MCO/OLS assumption tests
│
├── modeling/                        # 🤖 MODELING LAYER
│   ├── __init__.py
│   ├── model_runner.py             # Model orchestrator
│   ├── linear_models.py            # OLS, WLS, GLS
│   ├── nonlinear_models.py         # Nonlinear regression
│   ├── time_series_models.py       # ARIMA, ECM, VECM, Granger
│   ├── panel_models.py             # Fixed/Random effects
│   └── bigdata_models.py           # Random Forest, XGBoost, NN
│
├── explanation/                     # 💡 INTERPRETATION LAYER
│   ├── __init__.py
│   ├── explanation_runner.py       # Explanation orchestrator
│   ├── plain_language.py           # Human-readable explanations
│   ├── forecasting.py              # 30-period forecasts
│   └── charts.py                   # Visualization generation
│
├── report/                          # 📄 REPORTING LAYER
│   ├── __init__.py
│   └── pdf_builder.py              # HTML/PDF report builder
│
└── utils/                           # 🛠️ UTILITIES LAYER
    ├── __init__.py
    ├── validators.py               # Input validation
    ├── io.py                       # Data I/O
    └── formatter.py                # Result formatting
```

---

## 🔄 Data Flow

### Complete Pipeline Flow

```
┌─────────────────┐
│  Input DataFrame │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────┐
│  1. Metadata Detection  │  ← metadata/detector.py
│  - Data type            │
│  - Size category        │
│  - Linearity            │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  2. KPI Calculation     │  ← kpis/kpi_runner.py
│  - Marketing KPIs       │
│  - Operations KPIs      │
│  - Product KPIs         │
│  - Customer KPIs        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  3. Preprocessing       │  ← preprocessing/preprocessing_runner.py
│  - Missing data         │
│  - MCO assumptions      │
│  - Stationarity         │
│  - Scaling              │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  4. Model Selection     │  ← modeling/model_runner.py
│  - Small data models    │
│  - Big data models      │
│  - Time series models   │
│  - Panel models         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  5. Explanation         │  ← explanation/explanation_runner.py
│  - Plain language       │
│  - Forecasting          │
│  - Charts               │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  6. Report Generation   │  ← report/pdf_builder.py
│  - HTML template        │
│  - PDF conversion       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│  Output Report  │
└─────────────────┘
```

---

## 🧩 Module Interactions

### Dependency Graph

```
pipeline/auto_report.py
    │
    ├─→ metadata/detector.py
    │       └─→ type_detection.py
    │       └─→ linearity.py
    │
    ├─→ kpis/kpi_runner.py
    │       └─→ marketing.py, operations.py, etc.
    │
    ├─→ preprocessing/preprocessing_runner.py
    │       └─→ missing.py
    │       └─→ scaling.py
    │       └─→ stationarity.py
    │       └─→ mco_assumptions.py
    │
    ├─→ modeling/model_runner.py
    │       └─→ linear_models.py
    │       └─→ time_series_models.py
    │       └─→ bigdata_models.py
    │       └─→ panel_models.py
    │
    ├─→ explanation/explanation_runner.py
    │       └─→ plain_language.py
    │       └─→ forecasting.py
    │       └─→ charts.py
    │
    └─→ report/pdf_builder.py
```

**Key**: No circular dependencies. Clean top-down flow.

---

## 🎨 Design Patterns

### 1. Strategy Pattern
**Used in**: Model selection

```python
class ModelsRunner:
    def run(self, df):
        if size == 'small':
            return self._run_small_data_models(df)
        else:
            return self._run_big_data_models(df)
```

### 2. Template Method Pattern
**Used in**: KPI calculation

```python
class KPIsRunner:
    def run(self, df):
        for module in [marketing, operations, product]:
            results.extend(module.calculate_all(df))
```

### 3. Facade Pattern
**Used in**: Main pipeline

```python
def generate_report(df, label):
    # Hides complexity of 6-step pipeline
    pipeline = AutoStatReport(label)
    return pipeline.run(df)
```

### 4. Builder Pattern
**Used in**: PDF generation

```python
builder = PDFReportBuilder(label)
builder.build(metadata, kpis, preprocessing, models, explanation)
```

---

## 🔐 Error Handling Strategy

### Graceful Degradation

Each module handles errors independently:

```python
def calculate_kpi(df):
    try:
        return {'kpi': 'Metric', 'value': 42}
    except Exception as e:
        return {'kpi': 'Metric', 'error': str(e)}
```

Pipeline continues even if individual components fail.

---

## 📊 Model Selection Logic

### Decision Tree

```
Is data size >= 5000?
├─ YES → Big Data Models
│   ├─ Time Series? → ARIMA, GARCH, VARIMA
│   ├─ Cross-Section? → Random Forest, XGBoost
│   └─ Panel? → Advanced panel models
│
└─ NO → Small Data Models
    ├─ Time Series? → ECM, VECM, Granger
    ├─ Cross-Section? → OLS
    └─ Panel? → Fixed/Random Effects
```

---

## 🧪 Testing Strategy

### Unit Tests (Recommended)

```python
# tests/test_metadata.py
def test_metadata_detection():
    df = create_sample_df()
    detector = MetadataDetector()
    metadata = detector.detect(df)
    assert metadata['data_type'] in ['time_series', 'cross_section', 'panel']

# tests/test_kpis.py
def test_marketing_kpis():
    df = create_marketing_df()
    kpis = MarketingKPIs()
    results = kpis.calculate_all(df)
    assert len(results) > 0
```

---

## 🚀 Performance Considerations

### Optimization Points

1. **Lazy Loading**: Import heavy libraries only when needed
2. **Caching**: Cache metadata detection results
3. **Parallel Processing**: Run independent KPI modules in parallel
4. **Chunking**: Process large datasets in chunks

---

## 📝 Comparison with Original

### StatsReportsDocs.py vs AutoStat

| Aspect | Original | AutoStat |
|--------|----------|----------|
| Structure | Single file, nested classes | Modular, 40+ files |
| Imports | Clean, single entry | Clean, per-module |
| Testing | Difficult | Easy, isolated |
| Extensibility | Hard | Plug-and-play |
| Maintenance | Monolithic | Modular |
| Dependencies | Circular possible | Zero circular |

---

## 🎓 Best Practices

### Adding New Features

1. **New KPI**: Add file to `kpis/`, register in `kpi_runner.py`
2. **New Model**: Add file to `modeling/`, register in `model_runner.py`
3. **New Test**: Add to `preprocessing/`, register in `preprocessing_runner.py`

### Code Style

- Type hints for all public methods
- Docstrings for all classes and methods
- Return dictionaries with consistent keys
- Handle errors gracefully

---

**This architecture is production-ready and enterprise-grade.** ✅

