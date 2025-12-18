"""
Department-Specific Regression Models

Implements regression models from the metrics document for each department.
Each department has specific dependent variables and predictors based on
empirical research and business theory.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    import statsmodels.api as sm
except ImportError:
    sm = None


# Department regression specifications from "About the metrics" document
DEPARTMENT_REGRESSIONS = {
    'customer': {
        'nps_driver': {
            'name': 'NPS Driver Model',
            'dependent': ['nps', 'net_promoter_score'],
            'predictors': ['perceived_quality', 'perceived_value', 'satisfaction', 'experience', 'touchpoint'],
            'expected_signs': {'perceived_quality': '+', 'perceived_value': '+', 'experience': '+'},
            'interpretation': 'NPS is driven by perceived quality, value, and customer experience at touchpoints.'
        },
        'churn_model': {
            'name': 'Churn Model',
            'dependent': ['churn', 'churn_rate', 'attrition'],
            'predictors': ['nps', 'onboarding', 'support_quality', 'price_value', 'issues', 'satisfaction'],
            'expected_signs': {'nps': '-', 'onboarding': '-', 'support_quality': '-', 'issues': '+'},
            'interpretation': 'Churn increases with poor onboarding, low NPS, and technical issues.'
        },
        'growth_model': {
            'name': 'Customer Growth Model',
            'dependent': ['customer_growth', 'active_customers', 'new_customers'],
            'predictors': ['cac', 'ltv', 'activation_rate', 'referral_rate', 'retention'],
            'expected_signs': {'activation_rate': '+', 'referral_rate': '+', 'retention': '+'},
            'interpretation': 'Customer growth driven by CAC:LTV ratio (target 1:3), activation, and referrals.'
        }
    },
    'finance': {
        'profitability_model': {
            'name': 'Profitability Model',
            'dependent': ['roa', 'roe', 'profitability', 'profit', 'net_profit'],
            'predictors': ['efficiency', 'revenue', 'cogs', 'expenses', 'capitalization', 'equity'],
            'expected_signs': {'efficiency': '+', 'revenue': '+', 'cogs': '-', 'expenses': '-'},
            'interpretation': 'Profitability driven by operational efficiency and revenue, reduced by costs.'
        },
        'valuation_model': {
            'name': 'Valuation Model',
            'dependent': ['valuation', 'market_cap', 'stock_price', 'enterprise_value'],
            'predictors': ['net_profit_margin', 'revenue_growth', 'economic_profit', 'market_share'],
            'expected_signs': {'net_profit_margin': '+', 'revenue_growth': '+', 'market_share': '+'},
            'interpretation': '1% increase in net profit margin ≈ 12% increase in valuation.'
        },
        'margin_model': {
            'name': 'Net Profit Margin Model',
            'dependent': ['net_profit_margin', 'margin', 'profit_margin'],
            'predictors': ['sales', 'revenue', 'cogs', 'expenses', 'interest', 'tax'],
            'expected_signs': {'sales': '+', 'revenue': '+', 'cogs': '-', 'expenses': '-'},
            'interpretation': 'Margin improved by sales volume/pricing, reduced by COGS and operating expenses.'
        }
    },
    'sales': {
        'sales_growth_model': {
            'name': 'Sales Growth Model',
            'dependent': ['sales_growth', 'revenue_growth', 'growth_rate'],
            'predictors': ['leads', 'market_penetration', 'new_products', 'headcount', 'pipeline'],
            'expected_signs': {'leads': '+', 'market_penetration': '+', 'headcount': '+'},
            'interpretation': 'Sales growth driven by lead volume, market penetration, and sales team size.'
        },
        'win_rate_model': {
            'name': 'Deal Quality Model (Win Rate)',
            'dependent': ['win_rate', 'close_rate', 'conversion_rate'],
            'predictors': ['training', 'lead_scoring', 'pricing', 'competitive', 'opportunities'],
            'expected_signs': {'training': '+', 'pricing': '+'},
            'interpretation': 'Win rate improved by sales training and pricing flexibility.'
        },
        'aov_model': {
            'name': 'Revenue Density Model (AOV)',
            'dependent': ['aov', 'average_order_value', 'deal_size', 'order_value'],
            'predictors': ['bundling', 'upsell', 'cross_sell', 'customer_tier', 'revenue', 'orders'],
            'expected_signs': {'bundling': '+', 'upsell': '+', 'cross_sell': '+'},
            'interpretation': 'AOV increased through bundling, upselling, and cross-selling strategies.'
        }
    },
    'hr': {
        'productivity_model': {
            'name': 'Productivity Model',
            'dependent': ['productivity', 'output_per_hour', 'efficiency'],
            'predictors': ['training_hours', 'engagement', 'skill_level', 'experience'],
            'expected_signs': {'training_hours': '+', 'engagement': '+', 'skill_level': '+'},
            'interpretation': '10 training hours/year per employee raises productivity ~0.6%.'
        },
        'retention_model': {
            'name': 'Retention Model',
            'dependent': ['turnover', 'attrition', 'retention'],
            'predictors': ['engagement', 'hr_practices', 'conditions', 'satisfaction', 'salary'],
            'expected_signs': {'engagement': '-', 'satisfaction': '-', 'salary': '-'},
            'interpretation': 'High turnover hurts performance; engagement reduces turnover.'
        },
        'hr_impact_model': {
            'name': 'HR Impact Model',
            'dependent': ['performance', 'org_performance', 'productivity'],
            'predictors': ['hr_practice_index', 'rewards', 'staffing', 'development', 'training'],
            'expected_signs': {'hr_practice_index': '+', 'training': '+', 'development': '+'},
            'interpretation': 'HR practices (rewards, staffing, development) drive organizational performance.'
        }
    },
    'legal': {
        'risk_cost_model': {
            'name': 'Risk Cost Model',
            'dependent': ['total_risk_cost', 'risk_cost', 'legal_cost'],
            'predictors': ['compliance_spend', 'regulatory', 'risk_posture', 'compliance'],
            'expected_signs': {'compliance_spend': '-', 'compliance': '-'},
            'interpretation': 'Non-compliance costs ~2.7x compliance cost; spending on compliance reduces risk.'
        },
        'investor_trust_model': {
            'name': 'Investor Trust Model',
            'dependent': ['firm_value', 'performance', 'valuation'],
            'predictors': ['governance_score', 'disclosure', 'litigation', 'compliance'],
            'expected_signs': {'governance_score': '+', 'disclosure': '+', 'litigation': '-'},
            'interpretation': 'Better governance and disclosure improve firm value; litigation damages it.'
        },
        'bottom_line_model': {
            'name': 'Bottom Line Impact Model',
            'dependent': ['net_income', 'profit', 'earnings'],
            'predictors': ['fines', 'litigation_costs', 'settlements', 'legal_spend'],
            'expected_signs': {'fines': '-', 'litigation_costs': '-', 'settlements': '-'},
            'interpretation': 'Fines and litigation costs directly reduce net income.'
        }
    },
    'marketing': {
        'sales_elasticity_model': {
            'name': 'Sales Elasticity Model',
            'dependent': ['sales', 'revenue', 'total_sales'],
            'predictors': ['ad_spend', 'marketing_spend', 'brand_awareness', 'consideration'],
            'expected_signs': {'ad_spend': '+', 'marketing_spend': '+', 'brand_awareness': '+'},
            'interpretation': 'Short-term ad elasticity ~0.12 (1% ad increase → 0.12% sales gain); long-term ~0.24.'
        },
        'efficiency_model': {
            'name': 'Marketing Efficiency Model',
            'dependent': ['roi', 'roas', 'profitability', 'margin'],
            'predictors': ['cac', 'marketing_capability', 'cost', 'conversions', 'leads'],
            'expected_signs': {'cac': '-', 'marketing_capability': '+', 'conversions': '+'},
            'interpretation': 'Lower CAC enhances ROI; marketing capability correlates r≈0.44 with performance.'
        },
        'market_power_model': {
            'name': 'Market Power Model',
            'dependent': ['market_share', 'share', 'penetration'],
            'predictors': ['brand_metrics', 'ad_intensity', 'ad_spend', 'awareness', 'consideration'],
            'expected_signs': {'brand_metrics': '+', 'ad_spend': '+', 'awareness': '+'},
            'interpretation': 'Strong brand metrics boost sales and market share.'
        }
    },
    'operations': {
        'efficiency_model': {
            'name': 'Operations Efficiency Model',
            'dependent': ['profitability', 'margin', 'profit'],
            'predictors': ['doi', 'days_inventory', 'scrap_rate', 'utilization', 'efficiency'],
            'expected_signs': {'doi': '-', 'scrap_rate': '-', 'utilization': '+'},
            'interpretation': 'Lower DOI (leaner inventory) increases profitability; scrap reduces margins.'
        },
        'fulfillment_model': {
            'name': 'Fulfillment Model',
            'dependent': ['satisfaction', 'customer_satisfaction', 'nps'],
            'predictors': ['fill_rate', 'lead_time', 'delivery_time', 'on_time'],
            'expected_signs': {'fill_rate': '+', 'lead_time': '-'},
            'interpretation': 'Higher fill rates improve satisfaction; shorter lead times enable better service.'
        },
        'output_model': {
            'name': 'Output Model',
            'dependent': ['throughput', 'output', 'production', 'units'],
            'predictors': ['oee', 'capacity', 'equipment', 'maintenance', 'process'],
            'expected_signs': {'oee': '+', 'capacity': '+', 'maintenance': '+'},
            'interpretation': 'Higher OEE and capacity increase throughput and revenue.'
        }
    },
    'product': {
        'success_rate_model': {
            'name': 'NPD Success Rate Model',
            'dependent': ['npd_success', 'success_rate', 'launch_success'],
            'predictors': ['cross_functional', 'market_research', 'novelty', 'collaboration'],
            'expected_signs': {'cross_functional': '+', 'market_research': '+'},
            'interpretation': 'Cross-functional involvement and market research improve product success.'
        },
        'growth_engine_model': {
            'name': 'Growth Engine Model',
            'dependent': ['sales_growth', 'future_sales', 'revenue_growth'],
            'predictors': ['rd_spend', 'r_and_d', 'novelty', 'innovation'],
            'expected_signs': {'rd_spend': '+', 'novelty': '+', 'innovation': '+'},
            'interpretation': 'R&D investment drives innovation; typical internal returns 20-25%.'
        },
        'speed_model': {
            'name': 'Speed Model',
            'dependent': ['competitive_advantage', 'market_position', 'advantage'],
            'predictors': ['time_to_market', 'project_management', 'development_time'],
            'expected_signs': {'time_to_market': '-', 'development_time': '-'},
            'interpretation': 'Faster time-to-market enables quicker revenue and competitive advantage.'
        }
    },
    'production': {
        'efficiency_model': {
            'name': 'Production Efficiency Model',
            'dependent': ['profitability', 'margin', 'profit'],
            'predictors': ['doi', 'scrap_rate', 'utilization', 'waste', 'defects'],
            'expected_signs': {'scrap_rate': '-', 'utilization': '+', 'defects': '-'},
            'interpretation': 'Lower scrap and defects improve margins; high utilization spreads fixed costs.'
        },
        'fulfillment_model': {
            'name': 'Production Fulfillment Model',
            'dependent': ['satisfaction', 'customer_satisfaction', 'delivery'],
            'predictors': ['fill_rate', 'lead_time', 'production_lead_time'],
            'expected_signs': {'fill_rate': '+', 'lead_time': '-'},
            'interpretation': 'Shorter production lead time accelerates order fulfillment.'
        },
        'output_model': {
            'name': 'Production Output Model',
            'dependent': ['throughput', 'total_output', 'production_volume', 'units'],
            'predictors': ['oee', 'capacity', 'equipment_capacity', 'maintenance', 'process_design'],
            'expected_signs': {'oee': '+', 'capacity': '+', 'maintenance': '+'},
            'interpretation': 'Higher OEE (fewer breakdowns, less downtime) directly increases output.'
        }
    }
}


class DepartmentRegressionRunner:
    """
    Runs department-specific regression models based on available data.
    """

    def __init__(self, department: str = None):
        """
        Initialize the regression runner.

        Args:
            department: Department to run regressions for (None = all)
        """
        self.department = department.lower() if department else None
        self.results = []

    def _find_matching_column(self, df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
        """Find a column that matches any of the keywords."""
        for col in df.columns:
            col_lower = col.lower()
            for kw in keywords:
                if kw in col_lower:
                    return col
        return None

    def _find_matching_columns(self, df: pd.DataFrame, keywords: List[str]) -> List[str]:
        """Find all columns that match any of the keywords."""
        matches = []
        for col in df.columns:
            col_lower = col.lower()
            for kw in keywords:
                if kw in col_lower and col not in matches:
                    matches.append(col)
                    break
        return matches

    def run_regression(self, df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run a single regression based on specification.

        Args:
            df: Input DataFrame
            spec: Regression specification dict

        Returns:
            Regression results or None if cannot be run
        """
        if sm is None:
            return None

        # Find dependent variable
        dep_col = self._find_matching_column(df, spec['dependent'])
        if dep_col is None:
            return None

        # Find predictor variables
        pred_cols = self._find_matching_columns(df, spec['predictors'])
        if len(pred_cols) < 1:
            return None

        # Prepare data
        cols_needed = [dep_col] + pred_cols
        data = df[cols_needed].dropna()

        if len(data) < len(pred_cols) + 5:  # Need enough observations
            return None

        try:
            y = data[dep_col]
            X = data[pred_cols]
            X_const = sm.add_constant(X)

            model = sm.OLS(y, X_const)
            fitted = model.fit()

            # Build coefficient interpretation
            coef_interpretation = []
            for var, coef in fitted.params.items():
                if var == 'const':
                    continue
                pval = fitted.pvalues[var]
                sig = '***' if pval < 0.01 else ('**' if pval < 0.05 else ('*' if pval < 0.1 else ''))
                sign = '+' if coef > 0 else '-'

                # Check if sign matches expected
                expected = spec['expected_signs'].get(var.lower().split('_')[0], '?')
                match_str = '✓' if (expected == sign or expected == '?') else '⚠️ unexpected'

                coef_interpretation.append({
                    'variable': var,
                    'coefficient': round(coef, 4),
                    'p_value': round(pval, 4),
                    'significance': sig,
                    'sign': sign,
                    'expected': expected,
                    'match': match_str
                })

            return {
                'model_name': spec['name'],
                'dependent_variable': dep_col,
                'predictors': pred_cols,
                'n_observations': int(fitted.nobs),
                'r_squared': round(fitted.rsquared, 4),
                'adj_r_squared': round(fitted.rsquared_adj, 4),
                'f_statistic': round(fitted.fvalue, 4),
                'f_pvalue': round(fitted.f_pvalue, 6),
                'mae': round(np.mean(np.abs(fitted.resid)), 4),
                'coefficients': coef_interpretation,
                'interpretation': spec['interpretation'],
                'fitted_model': fitted
            }
        except Exception as e:
            return None

    def run(self, df: pd.DataFrame, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Run all applicable department regressions.

        Args:
            df: Input DataFrame
            metadata: Optional metadata dict

        Returns:
            List of regression results
        """
        results = []

        # Determine which departments to run
        if self.department and self.department in DEPARTMENT_REGRESSIONS:
            depts_to_run = {self.department: DEPARTMENT_REGRESSIONS[self.department]}
        else:
            depts_to_run = DEPARTMENT_REGRESSIONS

        # Run regressions for each department
        for dept_name, dept_specs in depts_to_run.items():
            for reg_key, reg_spec in dept_specs.items():
                result = self.run_regression(df, reg_spec)
                if result:
                    result['department'] = dept_name
                    result['regression_type'] = reg_key
                    results.append(result)

        self.results = results
        return results

    def summary_table(self) -> pd.DataFrame:
        """Generate summary table of all regression results."""
        if not self.results:
            return pd.DataFrame()

        rows = []
        for r in self.results:
            rows.append({
                'Department': r['department'].capitalize(),
                'Model': r['model_name'],
                'Dependent': r['dependent_variable'],
                'Predictors': ', '.join(r['predictors'][:3]) + ('...' if len(r['predictors']) > 3 else ''),
                'R²': r['r_squared'],
                'Adj R²': r['adj_r_squared'],
                'MAE': r['mae'],
                'F-stat': r['f_statistic'],
                'n': r['n_observations']
            })

        return pd.DataFrame(rows)

