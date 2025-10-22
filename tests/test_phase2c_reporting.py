"""
Phase 2C: Advanced Reporting - Integration Tests

Tests all reporting capabilities:
- PDF report generation
- HTML dashboard creation
- Excel workbook export

Run with: python test_phase2c_reporting.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from src.reporting.pdf_generator import PDFReportGenerator
    from src.reporting.html_dashboard import HTMLDashboardGenerator
    from src.reporting.excel_exporter import ExcelExporter
    print("✓ All Phase 2C modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nPlease install Phase 2C dependencies:")
    print("  pip install -r requirements-phase2c.txt")
    sys.exit(1)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def get_mock_analysis_data():
    """Get mock analysis data for testing"""
    return {
        'sentiment': {
            'hybrid_score': 65.5,
            'label': 'Positive',
            'lexicon_net_positivity': 0.15,
            'llm_sentiment_score': 68.2
        },
        'complexity': {
            'composite_score': 55.8,
            'level': 'Moderate',
            'flesch_reading_ease': 45.2,
            'flesch_kincaid_grade': 12.5,
            'gunning_fog_index': 14.2,
            'smog_index': 13.1,
            'coleman_liau_index': 12.8
        },
        'numerical_transparency': {
            'transparency_score': 72.3,
            'specificity_index': 0.78,
            'forward_looking_density': 3.2,
            'backward_looking_density': 5.1,
            'forward_to_backward_ratio': 0.63,
            'contextualization_quality': 75.0
        },
        'deception_risk': {
            'overall_risk_score': 32.5,
            'risk_level': 'Low',
            'confidence': 0.85,
            'linguistic_markers': {
                'hedging_density': 7.5,
                'qualifier_density': 5.2,
                'passive_voice_percentage': 18.2,
                'pronoun_distancing_percentage': 12.3
            }
        },
        'evasiveness': {
            'overall_score': 25.8,
            'level': 'Low'
        },
        'insights': {
            'key_findings': [
                'Strong revenue growth of 15% YoY',
                'Positive forward guidance provided',
                'Improved operating margins'
            ],
            'red_flags': [
                'Elevated inventory levels mentioned'
            ],
            'strengths': [
                'Clear and transparent communication',
                'Detailed numerical context',
                'Strong Q&A session'
            ]
        },
        'quarter': 'Q4',
        'year': 2024,
        'word_count': 5234,
        'sentence_count': 287
    }


def get_mock_historical_data():
    """Get mock historical data for testing"""
    base_data = get_mock_analysis_data()
    
    historical = []
    quarters = [('Q3', 2024), ('Q2', 2024), ('Q1', 2024), ('Q4', 2023)]
    
    for i, (quarter, year) in enumerate(quarters):
        data = base_data.copy()
        # Vary the scores slightly for each quarter
        data['sentiment']['hybrid_score'] = 65.5 - (i * 3)
        data['deception_risk']['overall_risk_score'] = 32.5 + (i * 2)
        data['complexity']['composite_score'] = 55.8 + (i * 1.5)
        data['quarter'] = quarter
        data['year'] = year
        historical.append(data)
    
    return historical


def get_mock_peer_data():
    """Get mock peer comparison data for testing"""
    base_data = get_mock_analysis_data()
    
    peers = [
        {
            **base_data,
            'company_name': 'Competitor A',
            'sentiment': {'hybrid_score': 58.3},
            'deception_risk': {'overall_risk_score': 41.2},
            'numerical_transparency': {'transparency_score': 68.5}
        },
        {
            **base_data,
            'company_name': 'Competitor B',
            'sentiment': {'hybrid_score': 71.2},
            'deception_risk': {'overall_risk_score': 28.7},
            'numerical_transparency': {'transparency_score': 78.9}
        },
        {
            **base_data,
            'company_name': 'Competitor C',
            'sentiment': {'hybrid_score': 62.8},
            'deception_risk': {'overall_risk_score': 35.6},
            'numerical_transparency': {'transparency_score': 70.2}
        }
    ]
    
    return peers


def test_pdf_generation():
    """Test PDF report generation"""
    print_section("TEST 1: PDF Report Generation")
    
    try:
        generator = PDFReportGenerator()
        print("✓ PDF generator initialized")
        
        # Generate report with current analysis only
        output_path = "/home/claude/test_reports/test_report_basic.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        analysis_data = get_mock_analysis_data()
        
        result = generator.generate_report(
            company_name="Test Corporation",
            analysis_data=analysis_data,
            output_path=output_path,
            include_charts=True,
            include_historical=False
        )
        
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            print(f"✓ Basic PDF report generated: {result}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"✗ PDF file not created at {result}")
            return False
        
        # Generate report with peer data
        output_path_peers = "/home/claude/test_reports/test_report_with_peers.pdf"
        peer_data = get_mock_peer_data()
        
        result_peers = generator.generate_report(
            company_name="Test Corporation",
            analysis_data=analysis_data,
            output_path=output_path_peers,
            include_charts=True,
            peer_data=peer_data
        )
        
        if os.path.exists(result_peers):
            file_size = os.path.getsize(result_peers)
            print(f"✓ PDF report with peers generated: {result_peers}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"✗ PDF with peers not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_html_dashboard():
    """Test HTML dashboard generation"""
    print_section("TEST 2: HTML Dashboard Generation")
    
    try:
        generator = HTMLDashboardGenerator()
        print("✓ HTML dashboard generator initialized")
        
        # Generate basic dashboard
        output_path = "/home/claude/test_reports/test_dashboard_basic.html"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        analysis_data = get_mock_analysis_data()
        
        result = generator.generate_dashboard(
            company_name="Test Corporation",
            current_analysis=analysis_data,
            output_path=output_path
        )
        
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            print(f"✓ Basic HTML dashboard generated: {result}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"✗ HTML file not created at {result}")
            return False
        
        # Generate dashboard with historical data
        output_path_hist = "/home/claude/test_reports/test_dashboard_historical.html"
        historical_data = get_mock_historical_data()
        
        result_hist = generator.generate_dashboard(
            company_name="Test Corporation",
            current_analysis=analysis_data,
            historical_analyses=historical_data,
            output_path=output_path_hist
        )
        
        if os.path.exists(result_hist):
            file_size = os.path.getsize(result_hist)
            print(f"✓ HTML dashboard with historical data generated: {result_hist}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"✗ HTML with historical data not created")
            return False
        
        # Generate dashboard with peers
        output_path_full = "/home/claude/test_reports/test_dashboard_full.html"
        peer_data = get_mock_peer_data()
        
        result_full = generator.generate_dashboard(
            company_name="Test Corporation",
            current_analysis=analysis_data,
            historical_analyses=historical_data,
            peer_analyses=peer_data,
            output_path=output_path_full
        )
        
        if os.path.exists(result_full):
            file_size = os.path.getsize(result_full)
            print(f"✓ Full HTML dashboard generated: {result_full}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"✗ Full HTML dashboard not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ HTML dashboard generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_excel_export():
    """Test Excel workbook export"""
    print_section("TEST 3: Excel Workbook Export")
    
    try:
        exporter = ExcelExporter()
        print("✓ Excel exporter initialized")
        
        # Generate basic Excel report
        output_path = "/home/claude/test_reports/test_analysis_basic.xlsx"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        analysis_data = get_mock_analysis_data()
        
        result = exporter.export_analysis(
            company_name="Test Corporation",
            analysis_data=analysis_data,
            output_path=output_path
        )
        
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            print(f"✓ Basic Excel workbook generated: {result}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"✗ Excel file not created at {result}")
            return False
        
        # Generate Excel with historical data
        output_path_hist = "/home/claude/test_reports/test_analysis_historical.xlsx"
        historical_data = get_mock_historical_data()
        
        result_hist = exporter.export_analysis(
            company_name="Test Corporation",
            analysis_data=analysis_data,
            historical_data=historical_data,
            output_path=output_path_hist
        )
        
        if os.path.exists(result_hist):
            file_size = os.path.getsize(result_hist)
            print(f"✓ Excel with historical data generated: {result_hist}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"✗ Excel with historical data not created")
            return False
        
        # Generate full Excel with peers
        output_path_full = "/home/claude/test_reports/test_analysis_full.xlsx"
        peer_data = get_mock_peer_data()
        
        result_full = exporter.export_analysis(
            company_name="Test Corporation",
            analysis_data=analysis_data,
            historical_data=historical_data,
            peer_data=peer_data,
            output_path=output_path_full
        )
        
        if os.path.exists(result_full):
            file_size = os.path.getsize(result_full)
            print(f"✓ Full Excel workbook generated: {result_full}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"✗ Full Excel workbook not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Excel export failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_output_files():
    """Verify all output files exist and have content"""
    print_section("TEST 4: Output File Verification")
    
    test_dir = Path("/home/claude/test_reports")
    
    if not test_dir.exists():
        print("✗ Test reports directory not found")
        return False
    
    expected_files = [
        "test_report_basic.pdf",
        "test_report_with_peers.pdf",
        "test_dashboard_basic.html",
        "test_dashboard_historical.html",
        "test_dashboard_full.html",
        "test_analysis_basic.xlsx",
        "test_analysis_historical.xlsx",
        "test_analysis_full.xlsx"
    ]
    
    all_exist = True
    total_size = 0
    
    for filename in expected_files:
        filepath = test_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            total_size += size
            print(f"✓ {filename}: {size:,} bytes")
        else:
            print(f"✗ {filename}: NOT FOUND")
            all_exist = False
    
    if all_exist:
        print(f"\n✓ All files created successfully")
        print(f"  Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        return True
    else:
        print(f"\n✗ Some files missing")
        return False


def cleanup_test_files():
    """Clean up test output files"""
    print_section("CLEANUP")
    
    test_dir = Path("/home/claude/test_reports")
    
    if test_dir.exists():
        import shutil
        try:
            shutil.rmtree(test_dir)
            print("✓ Test reports directory cleaned up")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")
    else:
        print("  No test files to clean up")


def main():
    """Run all Phase 2C tests"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "PHASE 2C ADVANCED REPORTING - INTEGRATION TESTS" + " " * 13 + "║")
    print("╚" + "=" * 78 + "╝")
    
    tests_passed = 0
    tests_total = 4
    
    # Run tests
    if test_pdf_generation():
        tests_passed += 1
    
    if test_html_dashboard():
        tests_passed += 1
    
    if test_excel_export():
        tests_passed += 1
    
    if test_output_files():
        tests_passed += 1
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"\nResults: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("\n🎉 ALL TESTS PASSED! Phase 2C reporting implementation successful.")
        print("\nGenerated test reports in: /home/claude/test_reports/")
        print("  • PDF reports with charts and metrics")
        print("  • Interactive HTML dashboards")
        print("  • Multi-sheet Excel workbooks")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed")
    
    # Ask about cleanup
    print("\n" + "=" * 80)
    keep_files = input("Keep test report files for review? (y/n): ").strip().lower()
    
    if keep_files != 'y':
        cleanup_test_files()
    else:
        print("Test files kept in: /home/claude/test_reports/")
    
    print("\n" + "=" * 80)
    print("Phase 2C Testing Complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
