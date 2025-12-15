"""
KPI Module

Business KPIs organized by functional area.
"""

from autostat.kpis.kpi_runner import KPIsRunner
from autostat.kpis.production import ProductionKPIs
from autostat.kpis.marketing import MarketingKPIs
from autostat.kpis.sales import SalesKPIs
from autostat.kpis.finance import FinanceKPIs
from autostat.kpis.operations import OperationsKPIs
from autostat.kpis.hr import HRKPIs
from autostat.kpis.product import ProductKPIs
from autostat.kpis.customer import CustomerKPIs
from autostat.kpis.legal import LegalKPIs

__all__ = [
    "KPIsRunner",
    "ProductionKPIs",
    "MarketingKPIs",
    "SalesKPIs",
    "FinanceKPIs",
    "OperationsKPIs",
    "HRKPIs",
    "ProductKPIs",
    "CustomerKPIs",
    "LegalKPIs",
]

