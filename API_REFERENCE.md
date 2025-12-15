# AutoStat API Reference

Complete API documentation for all public classes and methods.

---

## 📦 Main Entry Point

### `generate_report()`

```python
from autostat import generate_report

report_path = generate_report(df, label="Analysis")
```

**Parameters**:
- `df` (pd.DataFrame): Input data
- `label` (str): Report title

**Returns**: `str` - Path to generated report

---

## 🎯 Pipeline Module

### `AutoStatReport`

Main pipeline orchestrator.

```python
from autostat.pipeline.auto_report import AutoStatReport

pipeline = AutoStatReport(label="My Analysis")
report_path = pipeline.run(df)
results = pipeline.get_results()
```

#### Methods

**`__init__(label: str)`**
- Initialize pipeline with label

**`run(df, skip_kpis=False, skip_preprocessing=False, skip_modeling=False, skip_explanation=False)`**
- Execute complete pipeline
- Returns: Path to report

**`get_results()`**
- Get all intermediate results
- Returns: Dict with metadata, kpis, preprocessing, models, explanation

---

## 🔍 Metadata Module

### `MetadataDetector`

Detects data characteristics.

```python
from autostat.metadata.detector import MetadataDetector

detector = MetadataDetector()
metadata = detector.detect(df)
summary = detector.summary(metadata)
```

#### Methods

**`detect(df: pd.DataFrame)`**
- Detect all metadata
- Returns: Dict with data_type, panel_type, size_category, is_linear, etc.

**`summary(metadata: Dict)`**
- Generate human-readable summary
- Returns: str

### `DataTypeDetector`

```python
from autostat.metadata.type_detection import DataTypeDetector

detector = DataTypeDetector()
data_type = detector.detect_data_type(df)  # 'time_series', 'cross_section', 'panel'
panel_type = detector.detect_panel_type(df)  # 'fixed', 'unfixed', None
```

### `LinearityDetector`

```python
from autostat.metadata.linearity import LinearityDetector

detector = LinearityDetector(threshold=0.85)
is_linear = detector.test_linearity(df)
detailed = detector.detailed_linearity_test(df)
```

---

## 📊 KPI Module

### `KPIsRunner`

Orchestrates KPI calculation.

```python
from autostat.kpis.kpi_runner import KPIsRunner

runner = KPIsRunner(label="Q4 KPIs")
kpis_df = runner.run(df, metadata)
runner.add({'category': 'Custom', 'kpi': 'My KPI', 'value': 42, 'unit': '%'})
summary = runner.summary_table()
```

### Individual KPI Modules

All KPI modules follow the same interface:

```python
from autostat.kpis.marketing import MarketingKPIs

kpis = MarketingKPIs()
results = kpis.calculate_all(df)  # Returns List[Dict]

# Individual KPIs
conversion = kpis.conversion_rate(df)
cac = kpis.customer_acquisition_cost(df)
roi = kpis.marketing_roi(df)
```

**Available Modules**:
- `MarketingKPIs`: Conversion Rate, CAC, ROI
- `OperationsKPIs`: OEE, Units per Hour, Throughput
- `ProductKPIs`: Yield Rate, Defect Rate, Scrap Rate
- `CustomerKPIs`: CSAT, Retention Rate, Churn Rate
- `FinanceKPIs`, `SalesKPIs`, `HRKPIs`, `LegalKPIs`, `ProductionKPIs`

---

## 🔧 Preprocessing Module

### `PreprocessingRunner`

```python
from autostat.preprocessing.preprocessing_runner import PreprocessingRunner

runner = PreprocessingRunner(metadata, label="Preprocessing")
results = runner.run(df)

processed_df = results['processed_df']
test_results = results['test_results']
summary = runner.summary_table()
```

### `MissingDataHandler`

```python
from autostat.preprocessing.missing import MissingDataHandler

handler = MissingDataHandler(threshold=0.5)
report = handler.analyze(df)
cleaned_df = handler.handle(df, strategy='auto')  # 'auto', 'drop', 'mean', 'median', 'mode'
```

### `ScalingHandler`

```python
from autostat.preprocessing.scaling import ScalingHandler

scaler = ScalingHandler(method='standard')  # 'standard', 'minmax', 'robust'
scaled_df = scaler.scale(df)
original_df = scaler.inverse_transform(scaled_df)
```

### `StationarityTests`

```python
from autostat.preprocessing.stationarity import StationarityTests

tests = StationarityTests(significance_level=0.05)
all_results = tests.run_all_tests(df)
adf_result = tests.adf_test(df['column'])
kpss_result = tests.kpss_test(df['column'])
trend = tests.detect_trend(df['column'])
```

### `MCOAssumptionTests`

```python
from autostat.preprocessing.mco_assumptions import MCOAssumptionTests

tests = MCOAssumptionTests(data_type='time_series', panel_type='fixed')
all_results = tests.run_all_tests(df)

# Individual tests
aleatory = tests.test_aleatory_sample()
independence = tests.test_independent_observations()
exogeneity = tests.test_conditional_mean_zero()
homoscedasticity = tests.test_homoscedasticity(df)
autocorr = tests.test_no_autocorrelation(df)
normality = tests.test_normality_residuals(df)
```

---

## 🤖 Modeling Module

### `ModelsRunner`

```python
from autostat.modeling.model_runner import ModelsRunner

runner = ModelsRunner(metadata, label="Models")
results = runner.run(df)

models_run = results['models_run']
all_results = results['results']
best_model = results['best_model']
summary = runner.summary_table()
```

### `LinearModels`

```python
from autostat.modeling.linear_models import LinearModels

models = LinearModels()
results = models.run_models(df)
ols_result = models.multiple_linear_regression(df, target_col='revenue')
```

### `TimeSeriesModels`

```python
from autostat.modeling.time_series_models import TimeSeriesModels

models = TimeSeriesModels()
small_results = models.run_small_data_models(df)
big_results = models.run_big_data_models(df)

# Individual models
granger = models.granger_causality(df, maxlag=4)
arima = models.arima(df, target_col='sales', order=(1,1,1))
```

### `BigDataModels`

```python
from autostat.modeling.bigdata_models import BigDataModels

models = BigDataModels()
results = models.run_models(df, data_type='cross_section')
rf_result = models.random_forest(df, target_col='revenue', n_estimators=100)
```

---

## 💡 Explanation Module

### `ExplanationRunner`

```python
from autostat.explanation.explanation_runner import ExplanationRunner

runner = ExplanationRunner(label="Explanation")
results = runner.run(df, model_results, metadata)

interpretation = results['interpretation']
forecast = results['forecast']
charts = results['charts']
summary = runner.summary_table(results)
```

### `PlainLanguageExplainer`

```python
from autostat.explanation.plain_language import PlainLanguageExplainer

explainer = PlainLanguageExplainer()
explanation = explainer.explain_model(model_result)
```

### `Forecaster`

```python
from autostat.explanation.forecasting import Forecaster

forecaster = Forecaster()
forecast = forecaster.forecast_next_periods(df, model_results, periods=30)
```

### `ChartGenerator`

```python
from autostat.explanation.charts import ChartGenerator

generator = ChartGenerator()
charts = generator.generate_charts(df, model_results)
heatmap = generator.correlation_heatmap(df)
ts_plot = generator.time_series_plot(df)
dist_plots = generator.distribution_plots(df)
```

---

## 📄 Report Module

### `PDFReportBuilder`

```python
from autostat.report.pdf_builder import PDFReportBuilder

builder = PDFReportBuilder(label="Q4 Report")
report_path = builder.build(
    metadata=metadata,
    kpis=kpis_df,
    preprocessing=preprocessing_results,
    models=model_results,
    explanation=explanation_results
)
```

---

## 🛠️ Utils Module

### `DataValidator`

```python
from autostat.utils.validators import DataValidator

DataValidator.validate_dataframe(df)  # Raises error if invalid
```

### `DataIO`

```python
from autostat.utils.io import DataIO

df = DataIO.load_csv('data.csv')
DataIO.save_csv(df, 'output.csv')
```

### `ResultFormatter`

```python
from autostat.utils.formatter import ResultFormatter

formatted = ResultFormatter.format_dict(results_dict, indent=0)
print(formatted)
```

---

## 📊 Return Value Structures

### Metadata Dict
```python
{
    'data_type': 'time_series',  # or 'cross_section', 'panel'
    'panel_type': 'fixed',  # or 'unfixed', None
    'size_category': 'small',  # or 'big'
    'n_rows': 1000,
    'n_cols': 10,
    'is_linear': True,
    'has_missing': False,
    'missing_pct': 0.0
}
```

### KPI Result Dict
```python
{
    'category': 'Marketing',
    'kpi': 'Conversion Rate',
    'value': 2.5,
    'unit': '%',
    'total_conversions': 250,
    'total_visitors': 10000
}
```

### Model Result Dict
```python
{
    'model': 'Multiple Linear Regression (OLS)',
    'target': 'revenue',
    'features': ['employees', 'marketing_budget'],
    'n_obs': 200,
    'r_squared': 0.8542,
    'adj_r_squared': 0.8498,
    'f_statistic': 192.45,
    'f_pvalue': 0.000001,
    'aic': 2845.32,
    'bic': 2858.91,
    'coefficients': {'const': 50000, 'employees': 1200, 'marketing_budget': 2.5},
    'pvalues': {'const': 0.001, 'employees': 0.000, 'marketing_budget': 0.002}
}
```

---

**Complete API coverage for all public interfaces.** ✅

