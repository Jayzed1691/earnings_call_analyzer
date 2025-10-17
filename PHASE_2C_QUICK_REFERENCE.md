# Phase 2C: Quick Reference Guide

Quick reference for developers using the Phase 2C Advanced Reporting module.

---

## 🚀 Quick Start

### Installation

```bash
# Install Phase 2C dependencies
pip install -r requirements-phase2c.txt

# Verify installation
python -c "from src.reporting import PDFReportGenerator, HTMLDashboardGenerator, ExcelExporter; print('✓ Phase 2C ready')"
```

### Basic Usage

```python
# Import modules
from src.reporting import PDFReportGenerator, HTMLDashboardGenerator, ExcelExporter

# Initialize generators
pdf_gen = PDFReportGenerator()
html_gen = HTMLDashboardGenerator()
excel_exp = ExcelExporter()

# Generate reports (assuming you have analysis_data)
pdf_gen.generate_report(company_name, analysis_data, "output.pdf")
html_gen.generate_dashboard(company_name, analysis_data, output_path="dashboard.html")
excel_exp.export_analysis(company_name, analysis_data, output_path="analysis.xlsx")
```

---

## 📄 PDF Reports

### Basic PDF Report

```python
from src.reporting.pdf_generator import PDFReportGenerator

generator = PDFReportGenerator()

output = generator.generate_report(
    company_name="Apple Inc.",
    analysis_data=analysis_results,
    output_path="/path/to/report.pdf",
    include_charts=True,           # Include gauge charts
    include_historical=False        # No historical section
)
```

### PDF with Peer Comparison

```python
output = generator.generate_report(
    company_name="Apple Inc.",
    analysis_data=analysis_results,
    output_path="/path/to/report_with_peers.pdf",
    include_charts=True,
    peer_data=[
        competitor1_data,
        competitor2_data,
        competitor3_data
    ]
)
```

### PDF Features
- ✅ Executive summary with key highlights
- ✅ Color-coded metrics (green/yellow/red)
- ✅ Embedded gauge charts
- ✅ Sentiment, complexity, transparency sections
- ✅ Deception risk and evasiveness analysis
- ✅ Key findings, red flags, and strengths
- ✅ Optional peer comparison
- ✅ Document statistics
- ✅ Professional formatting

### Output
- Format: PDF
- Typical size: 200-500 KB
- Print-ready: Yes
- Editable: No (static PDF)

---

## 🌐 HTML Dashboards

### Basic Dashboard

```python
from src.reporting.html_dashboard import HTMLDashboardGenerator

generator = HTMLDashboardGenerator()

output = generator.generate_dashboard(
    company_name="Apple Inc.",
    current_analysis=current_quarter_data,
    output_path="/path/to/dashboard.html"
)
```

### Dashboard with Historical Trends

```python
output = generator.generate_dashboard(
    company_name="Apple Inc.",
    current_analysis=current_quarter_data,
    historical_analyses=[
        q3_data, q2_data, q1_data, q4_2023_data
    ],
    output_path="/path/to/dashboard_with_trends.html"
)
```

### Full Dashboard (Historical + Peers)

```python
output = generator.generate_dashboard(
    company_name="Apple Inc.",
    current_analysis=current_quarter_data,
    historical_analyses=historical_data,
    peer_analyses=peer_data,
    output_path="/path/to/full_dashboard.html"
)
```

### Dashboard Features
- ✅ Interactive Plotly charts
- ✅ Multi-tab interface (Overview, Detailed, Historical, Peers)
- ✅ Hover tooltips with details
- ✅ Zoom and pan capabilities
- ✅ Gauge charts for key metrics
- ✅ Radar chart for overall performance
- ✅ Line charts for historical trends
- ✅ Bar charts for peer comparison
- ✅ Responsive design
- ✅ Modern gradient styling

### Output
- Format: Single HTML file
- Typical size: 300-800 KB
- Interactive: Yes (requires browser)
- Shareable: Yes (send HTML file)

---

## 📊 Excel Workbooks

### Basic Excel Export

```python
from src.reporting.excel_exporter import ExcelExporter

exporter = ExcelExporter()

output = exporter.export_analysis(
    company_name="Apple Inc.",
    analysis_data=current_data,
    output_path="/path/to/analysis.xlsx"
)
```

### Excel with Historical Data

```python
output = exporter.export_analysis(
    company_name="Apple Inc.",
    analysis_data=current_data,
    historical_data=historical_data,
    output_path="/path/to/analysis_with_history.xlsx"
)
```

### Full Excel (Historical + Peers)

```python
output = exporter.export_analysis(
    company_name="Apple Inc.",
    analysis_data=current_data,
    historical_data=historical_data,
    peer_data=peer_data,
    output_path="/path/to/full_analysis.xlsx"
)
```

### Excel Features
- ✅ Multi-sheet workbook
- ✅ Executive Summary sheet
- ✅ Detailed Metrics sheet
- ✅ Insights & Findings sheet
- ✅ Historical Trends sheet (optional)
- ✅ Peer Comparison sheet (optional)
- ✅ Professional formatting
- ✅ Color-coded scores
- ✅ Status icons (✓, ○, ✗)
- ✅ Embedded charts
- ✅ Auto-sized columns

### Output
- Format: .xlsx
- Typical size: 50-150 KB
- Editable: Yes
- Compatible with: Excel, Google Sheets, LibreOffice

---

## 🔄 Common Operations

### Generate All Three Report Types

```python
from src.reporting import PDFReportGenerator, HTMLDashboardGenerator, ExcelExporter

# Initialize
pdf_gen = PDFReportGenerator()
html_gen = HTMLDashboardGenerator()
excel_exp = ExcelExporter()

# Generate all reports
company = "Apple Inc."
data = analysis_results

# PDF
pdf_gen.generate_report(company, data, f"reports/{company}_report.pdf")

# HTML Dashboard
html_gen.generate_dashboard(company, data, output_path=f"dashboards/{company}_dashboard.html")

# Excel
excel_exp.export_analysis(company, data, output_path=f"exports/{company}_analysis.xlsx")

print(f"✓ All reports generated for {company}")
```

### Batch Report Generation

```python
from src.database.repository import DatabaseRepository
from src.reporting import PDFReportGenerator, HTMLDashboardGenerator, ExcelExporter

# Initialize
repo = DatabaseRepository("sqlite:///data/earnings_analyzer.db")
pdf_gen = PDFReportGenerator()
html_gen = HTMLDashboardGenerator()
excel_exp = ExcelExporter()

# Get all companies
companies = repo.get_all_companies()

for company in companies:
    # Load latest analysis
    analysis = repo.load_latest_analysis(company.name)
    
    if analysis:
        # Generate reports
        try:
            pdf_gen.generate_report(
                company.name, analysis, f"reports/{company.ticker}_report.pdf"
            )
            html_gen.generate_dashboard(
                company.name, analysis, None, None,
                f"dashboards/{company.ticker}_dashboard.html"
            )
            excel_exp.export_analysis(
                company.name, analysis, None, None,
                f"exports/{company.ticker}_analysis.xlsx"
            )
            print(f"✓ Reports generated for {company.name}")
        except Exception as e:
            print(f"✗ Error for {company.name}: {e}")
```

### With Historical and Peer Data

```python
from src.database.repository import DatabaseRepository
from src.reporting import PDFReportGenerator

# Initialize
repo = DatabaseRepository("sqlite:///data/earnings_analyzer.db")
pdf_gen = PDFReportGenerator()

company_name = "Apple Inc."

# Get current analysis
current = repo.load_analysis(company_name, "Q4", 2024)

# Get historical data (last 8 quarters)
historical = repo.load_historical_analyses(company_name, quarters=8)

# Get peer data
peers = repo.get_peer_analyses(
    company_names=["Apple Inc.", "Microsoft Corporation", "Google Inc."],
    quarter="Q4",
    year=2024
)

# Generate comprehensive report
pdf_gen.generate_report(
    company_name=company_name,
    analysis_data=current.__dict__,  # Convert to dict
    output_path=f"reports/{company_name}_comprehensive.pdf",
    include_charts=True,
    peer_data=[p.__dict__ for p in peers if p.company.name != company_name]
)
```

---

## 📋 Data Structure Requirements

### Analysis Data Dictionary

```python
analysis_data = {
    'sentiment': {
        'hybrid_score': 65.5,              # Float 0-100
        'label': 'Positive',               # String
        'lexicon_net_positivity': 0.15,    # Float
        'llm_sentiment_score': 68.2        # Float 0-100
    },
    'complexity': {
        'composite_score': 55.8,           # Float 0-100
        'level': 'Moderate',               # String
        'flesch_reading_ease': 45.2,       # Float
        'flesch_kincaid_grade': 12.5,      # Float
        'gunning_fog_index': 14.2,         # Float
        'smog_index': 13.1,                # Float
        'coleman_liau_index': 12.8         # Float
    },
    'numerical_transparency': {
        'transparency_score': 72.3,        # Float 0-100
        'specificity_index': 0.78,         # Float 0-1
        'forward_looking_density': 3.2,    # Float
        'backward_looking_density': 5.1,   # Float
        'forward_to_backward_ratio': 0.63, # Float
        'contextualization_quality': 75.0  # Float 0-100
    },
    'deception_risk': {
        'overall_risk_score': 32.5,        # Float 0-100
        'risk_level': 'Low',               # String
        'confidence': 0.85,                # Float 0-1
        'linguistic_markers': {
            'hedging_density': 7.5,        # Float
            'qualifier_density': 5.2,      # Float
            'passive_voice_percentage': 18.2,
            'pronoun_distancing_percentage': 12.3
        }
    },
    'evasiveness': {
        'overall_score': 25.8,             # Float 0-100
        'level': 'Low'                     # String
    },
    'insights': {
        'key_findings': [                  # List of strings
            'Strong revenue growth',
            'Positive guidance'
        ],
        'red_flags': [                     # List of strings
            'Elevated inventory'
        ],
        'strengths': [                     # List of strings
            'Clear communication',
            'Transparent metrics'
        ]
    },
    'quarter': 'Q4',                       # String
    'year': 2024,                          # Integer
    'word_count': 5234,                    # Integer
    'sentence_count': 287                  # Integer
}
```

### Peer Data Format

```python
peer_data = [
    {
        'company_name': 'Competitor A',
        'sentiment': {'hybrid_score': 58.3},
        'deception_risk': {'overall_risk_score': 41.2},
        'numerical_transparency': {'transparency_score': 68.5},
        # ... other metrics
    },
    {
        'company_name': 'Competitor B',
        # ... same structure
    }
]
```

---

## 🎨 Customization

### Template Customization

Modify templates in `src/reporting/templates/`:

```bash
# PDF template
src/reporting/templates/report_template.html

# HTML dashboard template
src/reporting/templates/dashboard.html
```

### Color Customization

In your code:

```python
# Custom color schemes can be applied
# See individual generator classes for color attributes
generator.colors = {
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    # ... etc
}
```

---

## ⚠️ Common Pitfalls

### Missing Dependencies

**Problem:** Import errors for jinja2, plotly, weasyprint, openpyxl

**Solution:**
```bash
pip install -r requirements-phase2c.txt
```

### Template Not Found

**Problem:** `TemplateNotFound: report_template.html`

**Solution:**
```python
# Specify template directory explicitly
generator = PDFReportGenerator(template_dir="/absolute/path/to/templates")
```

### WeasyPrint Installation Issues

**Problem:** WeasyPrint fails to install on Windows

**Solution:**
```bash
# Install GTK+ for Windows first
# Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

# Then install weasyprint
pip install weasyprint
```

### Large File Sizes

**Problem:** Dashboard HTML files are too large

**Solution:**
```python
# Use CDN for Plotly instead of embedding
# This is already done in Phase 2C implementation
# File sizes are optimized
```

### Slow Generation

**Problem:** Report generation is slow

**Solution:**
```python
# Disable charts for faster generation
generator.generate_report(
    company_name,
    analysis_data,
    output_path,
    include_charts=False  # Faster generation
)
```

---

## 📈 Performance Tips

1. **Batch Processing**: Generate multiple reports in parallel
2. **Cache Templates**: Templates are cached automatically by Jinja2
3. **Disable Charts**: Set `include_charts=False` for faster PDF generation
4. **Optimize Images**: Charts are already optimized at 400x250px
5. **Use SSD**: Store output files on SSD for faster I/O

---

## 🧪 Testing

```bash
# Run Phase 2C integration tests
python test_phase2c_reporting.py

# Expected output: 4/4 tests passed

# Test reports will be in: /home/claude/test_reports/
```

---

## 🔗 Integration Examples

### With CLI

```python
import argparse
from src.reporting import PDFReportGenerator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--company', required=True)
    parser.add_argument('--quarter', required=True)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    # Load analysis from database
    from src.database.repository import DatabaseRepository
    repo = DatabaseRepository()
    analysis = repo.load_analysis(args.company, args.quarter, args.year)
    
    # Generate report
    generator = PDFReportGenerator()
    output = generator.generate_report(
        args.company, analysis.__dict__, args.output
    )
    
    print(f"Report generated: {output}")

if __name__ == "__main__":
    main()
```

### With API (Future Phase 2D)

```python
from fastapi import FastAPI, BackgroundTasks
from src.reporting import PDFReportGenerator

app = FastAPI()

@app.post("/generate-report")
async def generate_report(
    company_name: str,
    quarter: str,
    year: int,
    background_tasks: BackgroundTasks
):
    # Generate report in background
    def generate():
        generator = PDFReportGenerator()
        generator.generate_report(company_name, analysis_data, output_path)
    
    background_tasks.add_task(generate)
    return {"message": "Report generation started"}
```

---

## 📞 Need Help?

- Check `PHASE_2C_COMPLETE.md` for full documentation
- Review `test_phase2c_reporting.py` for usage examples
- See template files for customization options
- Refer to Jinja2, Plotly, WeasyPrint, and Openpyxl documentation

---

**Phase 2C Status:** ✅ COMPLETE and PRODUCTION READY
