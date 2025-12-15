"""
AutoStat - Enterprise Statistical Automation Engine

A production-grade statistical analysis and reporting framework for automated
data analysis, KPI tracking, preprocessing, modeling, and PDF report generation.

Main entry point:
    from autostat.pipeline.auto_report import generate_report
    
    pdf = generate_report(df, label="company_name")
"""

__version__ = "1.0.0"
__author__ = "IDN Products"

from autostat.pipeline.auto_report import generate_report, AutoStatReport

__all__ = [
    "generate_report",
    "AutoStatReport",
]

