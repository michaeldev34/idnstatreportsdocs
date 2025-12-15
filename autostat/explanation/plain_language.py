"""
Plain Language Explainer

Converts statistical results to plain language with actionable insights.
"""

from typing import Dict, Any, List
import pandas as pd


class PlainLanguageExplainer:
    """
    Generates plain language explanations of statistical results with recommendations.
    """

    def explain_model(self, model_result: Dict[str, Any], preprocessing_results: List[Dict] = None) -> str:
        """
        Generate comprehensive plain language explanation of a model.

        Args:
            model_result: Model result dictionary
            preprocessing_results: Optional preprocessing test results

        Returns:
            Plain language explanation with insights and recommendations
        """
        if not model_result or 'error' in model_result:
            return "No valid model results to explain."

        model_name = model_result.get('model', 'Unknown')

        # Build explanation based on model type
        explanation = ""

        if 'OLS' in model_name or 'Linear Regression' in model_name:
            explanation = self._explain_linear_regression(model_result)
        elif 'Random Forest' in model_name:
            explanation = self._explain_random_forest(model_result)
        elif 'ARIMA' in model_name:
            explanation = self._explain_arima(model_result)
        elif 'Granger' in model_name:
            explanation = self._explain_granger(model_result)
        else:
            explanation = self._explain_generic(model_result)

        # Add recommendations based on preprocessing
        if preprocessing_results:
            explanation += "\n\n" + self._generate_recommendations(preprocessing_results)

        return explanation
    
    def _explain_linear_regression(self, result: Dict[str, Any]) -> str:
        """Explain linear regression results."""
        target = result.get('target', 'the outcome')
        r_squared = result.get('r_squared', 0)
        n_obs = result.get('n_obs', 0)
        
        explanation = f"A linear regression model was fitted to predict {target}. "
        explanation += f"The model was trained on {n_obs} observations. "
        explanation += f"The model explains {r_squared*100:.1f}% of the variance in {target} (R² = {r_squared:.4f}). "
        
        # Interpret R²
        if r_squared > 0.7:
            explanation += "This indicates a strong relationship between the predictors and the outcome. "
        elif r_squared > 0.4:
            explanation += "This indicates a moderate relationship between the predictors and the outcome. "
        else:
            explanation += "This indicates a weak relationship between the predictors and the outcome. "
        
        # Significant predictors
        if 'pvalues' in result:
            sig_vars = [var for var, pval in result['pvalues'].items() 
                       if pval < 0.05 and var != 'const']
            if sig_vars:
                explanation += f"Significant predictors include: {', '.join(sig_vars)}. "
        
        return explanation
    
    def _explain_random_forest(self, result: Dict[str, Any]) -> str:
        """Explain Random Forest results."""
        target = result.get('target', 'the outcome')
        test_r2 = result.get('test_r2', 0)
        n_estimators = result.get('n_estimators', 0)
        
        explanation = f"A Random Forest model with {n_estimators} trees was fitted to predict {target}. "
        explanation += f"On the test set, the model achieves an R² of {test_r2:.4f}, "
        explanation += f"explaining {test_r2*100:.1f}% of the variance. "
        
        # Feature importance
        if 'feature_importance' in result:
            top_features = list(result['feature_importance'].keys())[:3]
            if top_features:
                explanation += f"The most important features are: {', '.join(top_features)}. "
        
        return explanation
    
    def _explain_arima(self, result: Dict[str, Any]) -> str:
        """Explain ARIMA results."""
        model = result.get('model', 'ARIMA')
        target = result.get('target', 'the series')
        aic = result.get('aic', 0)
        
        explanation = f"An {model} model was fitted to {target}. "
        explanation += f"The model has an AIC of {aic:.2f}. "
        explanation += "Lower AIC values indicate better model fit. "
        
        return explanation
    
    def _explain_granger(self, result: Dict[str, Any]) -> str:
        """Explain Granger causality results."""
        cause = result.get('cause', 'X')
        effect = result.get('effect', 'Y')
        has_causality = result.get('has_causality', False)
        
        if has_causality:
            explanation = f"Granger causality test indicates that {cause} Granger-causes {effect}. "
            explanation += f"This means past values of {cause} help predict {effect}. "
        else:
            explanation = f"Granger causality test does not find evidence that {cause} Granger-causes {effect}. "
        
        return explanation
    
    def _explain_generic(self, result: Dict[str, Any]) -> str:
        """Generic explanation for unknown model types."""
        model_name = result.get('model', 'The model')
        return f"{model_name} was fitted to the data. See detailed results for more information."

    def _generate_recommendations(self, preprocessing_results: List[Dict]) -> str:
        """Generate actionable recommendations based on preprocessing tests."""
        recommendations = []

        for test in preprocessing_results:
            test_name = test.get('test', '')
            passed = test.get('passed', True)
            result = test.get('result', {})

            # Non-stationarity recommendations
            if 'ADF Test' in test_name and not passed:
                recommendations.append(
                    f"⚠️ {test_name.split(' - ')[1] if ' - ' in test_name else 'Variable'} is non-stationary. "
                    "Consider differencing the series before modeling with ARIMA."
                )

            # Trend recommendations
            if 'Trend Detection' in test_name and result.get('has_trend'):
                var_name = test_name.split(' - ')[1] if ' - ' in test_name else 'Variable'
                slope = result.get('slope', 0)
                direction = "upward" if slope > 0 else "downward"
                recommendations.append(
                    f"📈 {var_name} shows a {direction} trend (slope={slope:.2f}). "
                    "This should be accounted for in forecasting models."
                )

            # Autocorrelation recommendations
            if 'Autocorrelation' in test_name and not passed:
                recommendations.append(
                    "⚠️ Significant autocorrelation detected. Use time series models (ARIMA, VAR) "
                    "instead of standard regression."
                )

            # Heteroscedasticity recommendations
            if 'Homoscedasticity' in test_name and not passed:
                recommendations.append(
                    "⚠️ Heteroscedasticity detected (non-constant variance). "
                    "Consider using robust standard errors or transforming the data (log, sqrt)."
                )

        if recommendations:
            return "**Recommendations:**\n" + "\n".join(f"• {rec}" for rec in recommendations[:5])
        else:
            return "**Data Quality:** All key statistical assumptions are satisfied. ✅"

