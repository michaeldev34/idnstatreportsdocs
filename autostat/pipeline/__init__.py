"""
Pipeline Module

Main orchestration pipeline.
"""

from autostat.pipeline.auto_report import AutoStatReport, generate_report

__all__ = [
    "AutoStatReport",
    "generate_report",
]

