"""
Phase 2C: Advanced Reporting Module

This module provides comprehensive reporting capabilities for earnings call analysis:
- PDF report generation with charts and visualizations
- Interactive HTML dashboards with Plotly
- Excel workbook exports with formatted tables and charts

Author: Earnings Call Analyzer Team
Version: 2.0.0-phase2c
"""

from .pdf_generator import PDFReportGenerator
from .html_dashboard import HTMLDashboardGenerator
from .excel_exporter import ExcelExporter

__all__ = [
    'PDFReportGenerator',
    'HTMLDashboardGenerator',
    'ExcelExporter',
]

__version__ = '2.0.0-phase2c'
