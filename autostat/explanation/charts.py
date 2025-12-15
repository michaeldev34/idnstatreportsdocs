"""
Chart Generator

Generate visualizations for reports.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import warnings
import base64
from io import BytesIO
warnings.filterwarnings('ignore')

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("whitegrid")
except ImportError as e:
    print(f"Warning: Could not import matplotlib/seaborn: {e}")
    plt = None
    sns = None
except Exception as e:
    print(f"Warning: Error setting up matplotlib: {e}")
    plt = None
    sns = None


class ChartGenerator:
    """
    Generates charts for statistical reports with base64 encoding.
    """

    def __init__(self):
        self.charts = []
        # Department mapping for variables
        self.department_mapping = {
            'Marketing': ['visitors', 'conversions', 'marketing_spend', 'ad_spend', 'cost', 'leads', 'traffic'],
            'Sales': ['orders', 'deals_won', 'opportunities', 'sales', 'revenue', 'total_sales'],
            'Finance': ['cogs', 'expenses', 'net_profit', 'profit', 'income', 'cost_of_goods'],
            'Operations': ['units_produced', 'production_hours', 'uptime', 'planned_time', 'units', 'production', 'output', 'hours'],
            'Customer': ['satisfaction_score', 'nps', 'churn_rate', 'active_customers', 'satisfaction', 'csat', 'rating']
        }

    def generate_charts(self, df: pd.DataFrame, models: Dict[str, Any], metadata: Dict[str, Any] = None, kpis: pd.DataFrame = None) -> List[Dict[str, Any]]:
        """
        Generate all relevant charts organized by department.

        Args:
            df: Input DataFrame
            models: Model results
            metadata: Dataset metadata
            kpis: KPI DataFrame with category column

        Returns:
            List of chart metadata with base64 encoded images
        """
        charts = []

        if plt is None:
            return [{'error': 'matplotlib not installed'}]

        # Time series plots by department (if applicable)
        if metadata and metadata.get('data_type') == 'time_series':
            dept_ts_charts = self.time_series_by_department(df, kpis)
            charts.extend([c for c in dept_ts_charts if 'error' not in c])

        # Correlation heatmaps by department
        dept_corr_charts = self.correlation_by_department(df, kpis)
        charts.extend([c for c in dept_corr_charts if 'error' not in c])

        # Distribution plots by department
        dept_dist_charts = self.distributions_by_department(df, kpis)
        charts.extend([c for c in dept_dist_charts if 'error' not in c])

        # Forecast visualization (if forecast available)
        if models and models.get('best_model'):
            forecast_chart = self.forecast_plot(df, models)
            if forecast_chart and 'error' not in forecast_chart:
                charts.append(forecast_chart)

            # IRF visualization (only for VAR, VECM, ECM, or linear models)
            best_model = models.get('best_model', {})
            model_type = best_model.get('model', '')
            if any(kw in model_type.lower() for kw in ['var', 'vecm', 'ecm', 'linear', 'ols']):
                irf_chart = self.irf_plot(df, models)
                if irf_chart and 'error' not in irf_chart:
                    charts.append(irf_chart)

        return charts

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        plt.close(fig)
        return image_base64
    
    def correlation_heatmap(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate correlation heatmap with base64 encoding."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) < 2:
            return None

        try:
            corr = df[numeric_cols].corr()

            fig, ax = plt.subplots(figsize=(10, 8))

            # Use seaborn if available for better styling
            if sns:
                sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
                           center=0, square=True, linewidths=1,
                           cbar_kws={"shrink": 0.8}, ax=ax)
            else:
                im = ax.imshow(corr, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
                ax.set_xticks(np.arange(len(corr.columns)))
                ax.set_yticks(np.arange(len(corr.columns)))
                ax.set_xticklabels(corr.columns, rotation=45, ha='right')
                ax.set_yticklabels(corr.columns)
                plt.colorbar(im, ax=ax)

            ax.set_title('Correlation Heatmap', fontsize=14, fontweight='bold')
            plt.tight_layout()

            # Convert to base64
            image_base64 = self._fig_to_base64(fig)

            return {
                'type': 'heatmap',
                'title': 'Correlation Heatmap',
                'image': image_base64
            }
        except Exception as e:
            return {'error': str(e)}
    
    def time_series_plot(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate time series plot with base64 encoding."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return None

        try:
            fig, axes = plt.subplots(min(len(numeric_cols), 4), 1,
                                    figsize=(12, 3 * min(len(numeric_cols), 4)))

            if len(numeric_cols) == 1:
                axes = [axes]

            # Plot up to 4 numeric columns
            for idx, col in enumerate(numeric_cols[:4]):
                ax = axes[idx] if len(numeric_cols) > 1 else axes[0]
                ax.plot(df.index if hasattr(df.index, '__iter__') else range(len(df)),
                       df[col], linewidth=2, color=f'C{idx}')
                ax.set_ylabel(col, fontsize=10)
                ax.set_title(f'{col} Over Time', fontsize=11, fontweight='bold')
                ax.grid(True, alpha=0.3)

                # Add trend line
                x = np.arange(len(df))
                z = np.polyfit(x, df[col].fillna(df[col].mean()), 1)
                p = np.poly1d(z)
                ax.plot(x, p(x), "--", alpha=0.5, color='red', label='Trend')
                ax.legend(fontsize=8)

            if len(numeric_cols) > 1:
                axes[-1].set_xlabel('Time Period', fontsize=10)
            else:
                axes[0].set_xlabel('Time Period', fontsize=10)

            plt.tight_layout()

            # Convert to base64
            image_base64 = self._fig_to_base64(fig)

            return {
                'type': 'line',
                'title': 'Time Series Analysis',
                'image': image_base64
            }
        except Exception as e:
            return {'error': str(e)}
    
    def distribution_plots(self, df: pd.DataFrame, max_plots: int = 2) -> List[Dict[str, Any]]:
        """Generate distribution plots for numeric columns with base64 encoding."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        charts = []

        # Limit to avoid too many charts
        for col in numeric_cols[:max_plots]:
            try:
                fig, ax = plt.subplots(figsize=(8, 5))

                data = df[col].dropna()

                # Histogram with KDE overlay if seaborn available
                if sns:
                    sns.histplot(data, bins=30, kde=True, ax=ax, color='steelblue')
                else:
                    ax.hist(data, bins=30, edgecolor='black', alpha=0.7, color='steelblue')

                ax.set_xlabel(col, fontsize=11)
                ax.set_ylabel('Frequency', fontsize=11)
                ax.set_title(f'Distribution of {col}', fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')

                # Add mean and median lines
                mean_val = data.mean()
                median_val = data.median()
                ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
                ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
                ax.legend()

                plt.tight_layout()

                # Convert to base64
                image_base64 = self._fig_to_base64(fig)

                charts.append({
                    'type': 'histogram',
                    'title': f'Distribution of {col}',
                    'image': image_base64
                })
            except Exception:
                continue

        return charts

    def _categorize_columns(self, df: pd.DataFrame, kpis: pd.DataFrame = None) -> Dict[str, List[str]]:
        """Categorize DataFrame columns by department."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorized = {dept: [] for dept in self.department_mapping.keys()}
        categorized['Other'] = []

        for col in numeric_cols:
            col_lower = col.lower()
            assigned = False

            for dept, keywords in self.department_mapping.items():
                if any(keyword in col_lower for keyword in keywords):
                    categorized[dept].append(col)
                    assigned = True
                    break

            if not assigned:
                categorized['Other'].append(col)

        # Remove empty departments
        categorized = {k: v for k, v in categorized.items() if v}

        return categorized

    def time_series_by_department(self, df: pd.DataFrame, kpis: pd.DataFrame = None) -> List[Dict[str, Any]]:
        """Generate time series plots organized by department."""
        if plt is None:
            return [{'error': 'matplotlib not installed'}]

        categorized = self._categorize_columns(df, kpis)
        charts = []

        for dept, cols in categorized.items():
            if not cols:
                continue

            try:
                n_cols = len(cols)
                fig, axes = plt.subplots(n_cols, 1, figsize=(14, 4 * n_cols))

                if n_cols == 1:
                    axes = [axes]

                fig.suptitle(f'{dept} - Time Series Analysis', fontsize=16, fontweight='bold', y=0.995)

                for idx, col in enumerate(cols):
                    ax = axes[idx]
                    ax.plot(df.index if hasattr(df.index, '__iter__') else range(len(df)),
                           df[col], linewidth=2, color=f'C{idx % 10}', label=col)
                    ax.set_ylabel(col, fontsize=11, fontweight='bold')
                    ax.set_title(f'{col} Over Time', fontsize=12)
                    ax.grid(True, alpha=0.3)

                    # Add trend line
                    x = np.arange(len(df))
                    z = np.polyfit(x, df[col].fillna(df[col].mean()), 1)
                    p = np.poly1d(z)
                    ax.plot(x, p(x), "--", alpha=0.6, color='red', linewidth=2, label='Trend')
                    ax.legend(fontsize=9, loc='best')

                axes[-1].set_xlabel('Time Period', fontsize=11, fontweight='bold')
                plt.tight_layout()

                image_base64 = self._fig_to_base64(fig)

                charts.append({
                    'type': 'time_series_dept',
                    'title': f'{dept} - Time Series',
                    'department': dept,
                    'image': image_base64
                })
            except Exception as e:
                charts.append({'error': f'{dept}: {str(e)}'})

        return charts

    def correlation_by_department(self, df: pd.DataFrame, kpis: pd.DataFrame = None) -> List[Dict[str, Any]]:
        """Generate correlation heatmaps organized by department."""
        if plt is None:
            return [{'error': 'matplotlib not installed'}]

        categorized = self._categorize_columns(df, kpis)
        charts = []

        for dept, cols in categorized.items():
            if len(cols) < 2:
                continue

            try:
                corr = df[cols].corr()

                fig, ax = plt.subplots(figsize=(max(8, len(cols) * 0.8), max(6, len(cols) * 0.6)))

                if sns:
                    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
                               center=0, square=True, linewidths=1,
                               cbar_kws={"shrink": 0.8}, ax=ax)
                else:
                    im = ax.imshow(corr, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
                    ax.set_xticks(np.arange(len(corr.columns)))
                    ax.set_yticks(np.arange(len(corr.columns)))
                    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
                    ax.set_yticklabels(corr.columns)
                    plt.colorbar(im, ax=ax)

                ax.set_title(f'{dept} - Correlation Matrix', fontsize=14, fontweight='bold')
                plt.tight_layout()

                image_base64 = self._fig_to_base64(fig)

                charts.append({
                    'type': 'correlation_dept',
                    'title': f'{dept} - Correlations',
                    'department': dept,
                    'image': image_base64
                })
            except Exception as e:
                charts.append({'error': f'{dept}: {str(e)}'})

        return charts

    def distributions_by_department(self, df: pd.DataFrame, kpis: pd.DataFrame = None) -> List[Dict[str, Any]]:
        """Generate distribution plots organized by department."""
        if plt is None:
            return [{'error': 'matplotlib not installed'}]

        categorized = self._categorize_columns(df, kpis)
        charts = []

        for dept, cols in categorized.items():
            if not cols:
                continue

            try:
                n_cols = len(cols)
                n_rows = (n_cols + 1) // 2  # 2 columns per row
                fig, axes = plt.subplots(n_rows, 2, figsize=(14, 4 * n_rows))

                if n_rows == 1:
                    axes = axes.reshape(1, -1)

                fig.suptitle(f'{dept} - Distributions', fontsize=16, fontweight='bold', y=0.995)

                for idx, col in enumerate(cols):
                    row = idx // 2
                    col_idx = idx % 2
                    ax = axes[row, col_idx] if n_rows > 1 else axes[col_idx]

                    data = df[col].dropna()

                    if sns:
                        sns.histplot(data, bins=30, kde=True, ax=ax, color='steelblue')
                    else:
                        ax.hist(data, bins=30, edgecolor='black', alpha=0.7, color='steelblue')

                    ax.set_xlabel(col, fontsize=10)
                    ax.set_ylabel('Frequency', fontsize=10)
                    ax.set_title(f'{col}', fontsize=11, fontweight='bold')
                    ax.grid(True, alpha=0.3, axis='y')

                    # Add mean and median lines
                    mean_val = data.mean()
                    median_val = data.median()
                    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
                    ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
                    ax.legend(fontsize=8)

                # Hide empty subplots
                if n_cols % 2 == 1:
                    axes[-1, -1].axis('off')

                plt.tight_layout()

                image_base64 = self._fig_to_base64(fig)

                charts.append({
                    'type': 'distribution_dept',
                    'title': f'{dept} - Distributions',
                    'department': dept,
                    'image': image_base64
                })
            except Exception as e:
                charts.append({'error': f'{dept}: {str(e)}'})

        return charts

    def forecast_plot(self, df: pd.DataFrame, models: Dict[str, Any]) -> Dict[str, Any]:
        """Generate forecast visualization plot."""
        if plt is None:
            return {'error': 'matplotlib not installed'}

        try:
            # Get forecast data from models
            best_model = models.get('best_model', {})

            # This will be populated by explanation_runner
            forecast_data = models.get('forecast', {})

            if not forecast_data or 'forecast_table' not in forecast_data:
                return {'error': 'No forecast data available'}

            forecast_df = forecast_data['forecast_table']

            if forecast_df is None or len(forecast_df) == 0:
                return {'error': 'Empty forecast table'}

            # Determine the target variable
            target = best_model.get('target', 'Value')

            # Get historical data (last 50 points for clarity)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                return {'error': 'No numeric columns for forecast'}

            # Use the target column if available, otherwise use first numeric column
            if target in numeric_cols:
                hist_col = target
            else:
                hist_col = numeric_cols[0]

            historical = df[hist_col].tail(50)

            fig, ax = plt.subplots(figsize=(14, 6))

            # Plot historical data
            hist_x = range(len(historical))
            ax.plot(hist_x, historical.values, linewidth=2, color='steelblue', label='Historical Data')

            # Plot forecast
            forecast_x = range(len(historical), len(historical) + len(forecast_df))
            ax.plot(forecast_x, forecast_df['Forecast'].values, linewidth=2, color='orange', label='Forecast', linestyle='--')

            # Plot confidence intervals
            ax.fill_between(forecast_x,
                           forecast_df['Lower_CI'].values,
                           forecast_df['Upper_CI'].values,
                           alpha=0.3, color='orange', label='95% Confidence Interval')

            ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax.set_ylabel(hist_col, fontsize=12, fontweight='bold')
            ax.set_title(f'Forecast: {hist_col} (Next {len(forecast_df)} Periods)', fontsize=14, fontweight='bold')
            ax.legend(fontsize=10, loc='best')
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            image_base64 = self._fig_to_base64(fig)

            return {
                'type': 'forecast',
                'title': 'Forecast Visualization',
                'image': image_base64
            }
        except Exception as e:
            return {'error': f'Forecast plot error: {str(e)}'}

    def irf_plot(self, df: pd.DataFrame, models: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Impulse Response Function (IRF) visualization.

        Only applicable for VAR, VECM, ECM, and linear models.
        Shows the dynamic response of variables to a shock.

        Args:
            df: Input DataFrame
            models: Model results containing best_model

        Returns:
            Dictionary with chart info and base64 encoded image
        """
        if plt is None:
            return {'error': 'matplotlib not installed'}

        try:
            best_model = models.get('best_model', {})
            model_type = best_model.get('model', '').lower()

            # Get numeric columns for IRF simulation
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

            if len(numeric_cols) < 2:
                return {'error': 'Need at least 2 variables for IRF'}

            # Use first 2-4 variables for IRF visualization
            irf_cols = numeric_cols[:min(4, len(numeric_cols))]
            n_vars = len(irf_cols)

            # Simulate IRF using VAR-based approach
            periods = 20  # Number of periods to show response

            try:
                from statsmodels.tsa.api import VAR

                # Prepare data
                data = df[irf_cols].dropna()

                if len(data) < 20:
                    return {'error': 'Insufficient data for IRF analysis'}

                # Fit VAR model
                var_model = VAR(data)
                var_fitted = var_model.fit(maxlags=min(4, len(data) // 5))

                # Generate IRF
                irf = var_fitted.irf(periods)

                # Create IRF plot
                fig, axes = plt.subplots(n_vars, n_vars, figsize=(12, 10))

                if n_vars == 1:
                    axes = np.array([[axes]])

                fig.suptitle('Impulse Response Functions', fontsize=14, fontweight='bold', y=0.995)

                for i, response_var in enumerate(irf_cols):
                    for j, impulse_var in enumerate(irf_cols):
                        ax = axes[i, j] if n_vars > 1 else axes[0, 0]

                        # Get IRF data
                        irf_data = irf.irfs[:, i, j]
                        lower = irf.lower()[:, i, j] if hasattr(irf, 'lower') else irf_data * 0.9
                        upper = irf.upper()[:, i, j] if hasattr(irf, 'upper') else irf_data * 1.1

                        # Plot
                        ax.plot(range(periods + 1), irf_data, 'b-', linewidth=2, label='IRF')
                        ax.fill_between(range(periods + 1), lower, upper, alpha=0.2, color='blue')
                        ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
                        ax.set_title(f'{impulse_var} → {response_var}', fontsize=9)
                        ax.grid(True, alpha=0.3)

                        if i == n_vars - 1:
                            ax.set_xlabel('Periods', fontsize=8)
                        if j == 0:
                            ax.set_ylabel('Response', fontsize=8)

                plt.tight_layout()

                image_base64 = self._fig_to_base64(fig)

                return {
                    'type': 'irf',
                    'title': 'Impulse Response Functions',
                    'image': image_base64,
                    'variables': irf_cols,
                    'periods': periods
                }

            except ImportError:
                return {'error': 'statsmodels not installed for IRF'}
            except Exception as e:
                # Fallback: Simple correlation-based IRF simulation
                return self._simple_irf_plot(df, irf_cols, periods)

        except Exception as e:
            return {'error': f'IRF plot error: {str(e)}'}

    def _simple_irf_plot(self, df: pd.DataFrame, cols: List[str], periods: int = 20) -> Dict[str, Any]:
        """
        Simple IRF simulation based on correlation structure.
        Used as fallback when VAR is not available.
        """
        try:
            n_vars = len(cols)
            data = df[cols].dropna()

            # Calculate correlation matrix
            corr = data.corr()

            # Simulate simple decay-based IRF
            fig, axes = plt.subplots(1, n_vars, figsize=(4 * n_vars, 4))

            if n_vars == 1:
                axes = [axes]

            fig.suptitle('Impulse Response (Simulated)', fontsize=14, fontweight='bold', y=0.98)

            colors = plt.cm.Set2(np.linspace(0, 1, n_vars))

            for i, (ax, shock_var) in enumerate(zip(axes, cols)):
                ax.set_title(f'Shock to: {shock_var}', fontsize=11, fontweight='bold')

                for j, response_var in enumerate(cols):
                    # Get correlation coefficient
                    rho = corr.loc[shock_var, response_var]

                    # Simulate response with exponential decay
                    decay_rate = 0.8
                    initial_shock = 1.0 if shock_var == response_var else abs(rho)

                    response = [initial_shock * (decay_rate ** t) for t in range(periods + 1)]
                    if rho < 0 and shock_var != response_var:
                        response = [-r for r in response]

                    ax.plot(range(periods + 1), response, linewidth=2,
                           label=response_var, color=colors[j])

                ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
                ax.set_xlabel('Periods', fontsize=10)
                ax.set_ylabel('Response', fontsize=10)
                ax.legend(fontsize=8, loc='best')
                ax.grid(True, alpha=0.3)

            plt.tight_layout()

            image_base64 = self._fig_to_base64(fig)

            return {
                'type': 'irf',
                'title': 'Impulse Response Functions (Simulated)',
                'image': image_base64,
                'variables': cols,
                'periods': periods,
                'note': 'Simulated based on correlation structure'
            }
        except Exception as e:
            return {'error': f'Simple IRF error: {str(e)}'}

