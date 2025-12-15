"""
Forecasting

Generate forecasts from fitted models.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class Forecaster:
    """
    Generates forecasts from fitted models.
    """
    
    def forecast_next_periods(self, df: pd.DataFrame, models: Dict[str, Any],
                              periods: int = 30) -> Dict[str, Any]:
        """
        Generate forecast for next N periods with confidence intervals.

        Args:
            df: Input DataFrame
            models: Model results
            periods: Number of periods to forecast

        Returns:
            Dictionary with forecast results including table
        """
        best_model = models.get('best_model', {})

        if not best_model:
            return {
                'periods': 0,
                'forecast': None,
                'forecast_table': None,
                'error': 'No model available'
            }

        model_type = best_model.get('model', '')

        try:
            # Granger causality doesn't have fitted_model, but we can still forecast
            if 'Granger' in model_type:
                forecast_df = self._forecast_granger(df, best_model, periods)
            elif 'fitted_model' not in best_model:
                return {
                    'periods': 0,
                    'forecast': None,
                    'forecast_table': None,
                    'error': 'No fitted model available'
                }
            elif 'ARIMA' in model_type:
                fitted_model = best_model['fitted_model']
                forecast_df = self._forecast_arima(fitted_model, periods)
            elif 'Random Forest' in model_type or 'OLS' in model_type:
                fitted_model = best_model['fitted_model']
                forecast_df = self._forecast_regression(df, fitted_model, best_model, periods)
            else:
                return {
                    'periods': 0,
                    'forecast': None,
                    'forecast_table': None,
                    'error': f'Forecasting not implemented for {model_type}'
                }

            return {
                'periods': periods,
                'forecast': forecast_df['Forecast'].tolist() if forecast_df is not None else None,
                'forecast_table': forecast_df,
                'model': model_type
            }
        except Exception as e:
            return {
                'periods': 0,
                'forecast': None,
                'forecast_table': None,
                'error': str(e)
            }
    
    def _forecast_arima(self, fitted_model, periods: int) -> pd.DataFrame:
        """Forecast using ARIMA model with confidence intervals."""
        try:
            # Get forecast with confidence intervals
            forecast_result = fitted_model.get_forecast(steps=periods)
            forecast = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int()

            forecast_df = pd.DataFrame({
                'Period': range(1, periods + 1),
                'Forecast': forecast.values,
                'Lower_CI': conf_int.iloc[:, 0].values,
                'Upper_CI': conf_int.iloc[:, 1].values
            })
        except:
            # Fallback if confidence intervals not available
            forecast = fitted_model.forecast(steps=periods)
            forecast_df = pd.DataFrame({
                'Period': range(1, periods + 1),
                'Forecast': forecast,
                'Lower_CI': forecast * 0.9,
                'Upper_CI': forecast * 1.1
            })

        # Round for readability
        forecast_df['Forecast'] = forecast_df['Forecast'].round(2)
        forecast_df['Lower_CI'] = forecast_df['Lower_CI'].round(2)
        forecast_df['Upper_CI'] = forecast_df['Upper_CI'].round(2)

        return forecast_df

    def _forecast_granger(self, df: pd.DataFrame, model_result: Dict[str, Any],
                         periods: int) -> pd.DataFrame:
        """Forecast using simple trend extrapolation for Granger causality."""
        # For Granger, we'll use simple trend-based forecasting
        target = model_result.get('target', None)

        if target is None or target not in df.columns:
            # Use first numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            target = numeric_cols[0] if len(numeric_cols) > 0 else None

        if target is None:
            raise ValueError("No target variable for forecasting")

        # Calculate trend
        y = df[target].values
        x = np.arange(len(y))
        z = np.polyfit(x, y, 1)  # Linear trend
        p = np.poly1d(z)

        # Forecast
        future_x = np.arange(len(y), len(y) + periods)
        forecast = p(future_x)

        # Estimate confidence intervals based on historical std
        std = df[target].std()

        forecast_df = pd.DataFrame({
            'Period': range(1, periods + 1),
            'Forecast': forecast.round(2),
            'Lower_CI': (forecast - 1.96 * std).round(2),
            'Upper_CI': (forecast + 1.96 * std).round(2)
        })

        return forecast_df
    
    def _forecast_regression(self, df: pd.DataFrame, fitted_model,
                            model_result: Dict[str, Any], periods: int) -> pd.DataFrame:
        """
        Forecast using regression model with confidence intervals.

        Note: This is a simplified approach using trend extrapolation.
        """
        features = model_result.get('features', [])

        if not features:
            raise ValueError("No features available for forecasting")

        # Simple approach: use last known values and add trend
        last_values = df[features].iloc[-1].values

        forecasts = []
        for i in range(periods):
            # Simple linear extrapolation (very basic)
            forecast_features = last_values * (1 + 0.01 * i)  # 1% growth per period

            # Predict
            if hasattr(fitted_model, 'predict'):
                try:
                    # For sklearn models
                    pred = fitted_model.predict([forecast_features])[0]
                except:
                    # For statsmodels
                    import statsmodels.api as sm
                    X_with_const = sm.add_constant([forecast_features])
                    pred = fitted_model.predict(X_with_const)[0]
            else:
                pred = np.nan

            forecasts.append(pred)

        # Estimate confidence intervals based on historical residuals
        target = model_result.get('target', None)
        if target and target in df.columns:
            std = df[target].std()
        else:
            std = np.std(forecasts) if forecasts else 0

        forecast_df = pd.DataFrame({
            'Period': range(1, periods + 1),
            'Forecast': np.round(forecasts, 2),
            'Lower_CI': np.round(np.array(forecasts) - 1.96 * std, 2),
            'Upper_CI': np.round(np.array(forecasts) + 1.96 * std, 2)
        })

        return forecast_df

