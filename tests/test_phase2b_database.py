#!/usr/bin/env python3
"""
Phase 2B Database Integration Tests

Validates:
- Database models creation
- Repository CRUD operations
- Company management
- Analysis storage and retrieval
- Benchmark operations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any

# Import database components
from src.database.models import Base, Company, AnalysisResult, Benchmark
from src.database.repository import DatabaseRepository
from config.settings import settings


# Mock ComprehensiveAnalysisResult for testing
@dataclass
class MockAnalysisResult:
    """Mock analysis result for testing"""
    sentiment: Dict[str, Any]
    complexity: Dict[str, Any]
    numerical: Dict[str, Any]
    deception_risk: Dict[str, Any]
    evasiveness: Dict[str, Any]
    word_count: int
    sentence_count: int
    insights: Dict[str, Any]


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_database_setup():
    """Test 1: Database setup and table creation"""
    print_section("TEST 1: Database Setup")
    
    try:
        # Create test database
        test_db_url = "sqlite:///./data/test_earnings.db"
        repo = DatabaseRepository(test_db_url)
        
        print("✓ Database connection established")
        print("✓ Tables created successfully")
        print(f"  - companies")
        print(f"  - analysis_results")
        print(f"  - benchmarks")
        
        return repo, True
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return None, False


def test_company_operations(repo: DatabaseRepository):
    """Test 2: Company CRUD operations"""
    print_section("TEST 2: Company Operations")
    
    try:
        # Save company
        company_id = repo.save_company(
            name="Apple Inc.",
            ticker="AAPL",
            sector="Technology",
            industry="Consumer Electronics"
        )
        print(f"✓ Company created (ID: {company_id})")
        
        # Get company
        company = repo.get_company(name="Apple Inc.")
        assert company is not None
        assert company.ticker == "AAPL"
        print(f"✓ Company retrieved: {company.name} ({company.ticker})")
        
        # Update company
        company_id = repo.save_company(
            name="Apple Inc.",
            ticker="AAPL",
            sector="Technology",
            industry="Consumer Electronics - Updated"
        )
        company = repo.get_company(name="Apple Inc.")
        assert company.industry == "Consumer Electronics - Updated"
        print(f"✓ Company updated successfully")
        
        # Search companies
        results = repo.search_companies("Apple")
        assert len(results) > 0
        print(f"✓ Company search works ({len(results)} results)")
        
        return True
    except Exception as e:
        print(f"✗ Company operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analysis_operations(repo: DatabaseRepository):
    """Test 3: Analysis storage and retrieval"""
    print_section("TEST 3: Analysis Operations")
    
    try:
        # Create mock analysis result
        mock_result = MockAnalysisResult(
            sentiment={
                'hybrid_score': 65.5,
                'label': 'Positive',
                'lexicon': {'net_positivity': 8.2},
                'llm': {'score': 0.75}
            },
            complexity={
                'composite_score': 72.3,
                'complexity_level': 'Moderate',
                'metrics': {
                    'flesch_reading_ease': 55.4,
                    'flesch_kincaid_grade': 12.1,
                    'gunning_fog_index': 14.8,
                    'smog_index': 13.2,
                    'coleman_liau_index': 11.9
                }
            },
            numerical={
                'transparency_score': 68.7,
                'specificity_index': 0.72,
                'forward_looking_density': 2.5,
                'backward_looking_density': 3.8,
                'forward_to_backward_ratio': 0.66,
                'contextualization_quality': 75.0,
                'vs_sp500_benchmark': 'above'
            },
            deception_risk={
                'overall_risk_score': 35.2,
                'risk_level': 'Low',
                'confidence': 0.82,
                'linguistic_markers': {
                    'hedging_density': 8.5,
                    'qualifier_density': 6.2,
                    'passive_voice_percentage': 22.0,
                    'pronoun_distancing_percentage': 15.3
                }
            },
            evasiveness={
                'overall_score': 12.8,
                'level': 'Moderate',
                'vs_baseline': 'at'
            },
            word_count=5234,
            sentence_count=287,
            insights={
                'key_findings': [
                    'Strong revenue growth of 15% YoY',
                    'Improved operating margins'
                ],
                'red_flags': [
                    'Increased inventory levels'
                ],
                'strengths': [
                    'Clear forward guidance',
                    'Transparent financial reporting'
                ]
            }
        )
        
        # Save analysis
        analysis_id = repo.save_analysis(
            company_name="Apple Inc.",
            quarter="Q4",
            year=2024,
            analysis_result=mock_result
        )
        print(f"✓ Analysis saved (ID: {analysis_id})")
        
        # Load analysis
        analysis = repo.load_analysis("Apple Inc.", "Q4", 2024)
        assert analysis is not None
        assert analysis.hybrid_sentiment_score == 65.5
        assert analysis.deception_risk_score == 35.2
        print(f"✓ Analysis retrieved successfully")
        print(f"  - Sentiment: {analysis.sentiment_label}")
        print(f"  - Complexity: {analysis.complexity_level}")
        print(f"  - Deception Risk: {analysis.deception_risk_level}")
        
        # Save multiple quarters for historical testing
        for quarter, year in [("Q3", 2024), ("Q2", 2024), ("Q1", 2024)]:
            repo.save_analysis(
                company_name="Apple Inc.",
                quarter=quarter,
                year=year,
                analysis_result=mock_result
            )
        print(f"✓ Multiple quarters saved for historical testing")
        
        # Load historical analyses
        historical = repo.load_historical_analyses("Apple Inc.", quarters=4)
        assert len(historical) == 4
        print(f"✓ Historical analyses retrieved ({len(historical)} quarters)")
        
        # Get latest analysis
        latest = repo.get_latest_analysis("Apple Inc.")
        assert latest is not None
        print(f"✓ Latest analysis: {latest.quarter} {latest.year}")
        
        return True
    except Exception as e:
        print(f"✗ Analysis operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_benchmark_operations(repo: DatabaseRepository):
    """Test 4: Benchmark operations"""
    print_section("TEST 4: Benchmark Operations")
    
    try:
        # Save benchmarks
        repo.save_benchmark("S&P 500", "net_positivity", 5.2)
        repo.save_benchmark("S&P 500", "evasiveness", 11.0)
        repo.save_benchmark("Technology", "numeric_transparency", 65.0)
        print("✓ Benchmarks saved")
        
        # Get benchmark
        benchmark = repo.get_benchmark("S&P 500", "net_positivity")
        assert benchmark is not None
        assert benchmark.value == 5.2
        print(f"✓ Benchmark retrieved: {benchmark.sector} - {benchmark.metric_name} = {benchmark.value}")
        
        # Get all benchmarks
        all_benchmarks = repo.get_all_benchmarks()
        print(f"✓ All benchmarks retrieved ({len(all_benchmarks)} total)")
        
        # Get sector benchmarks
        tech_benchmarks = repo.get_all_benchmarks(sector="Technology")
        print(f"✓ Technology sector benchmarks: {len(tech_benchmarks)}")
        
        return True
    except Exception as e:
        print(f"✗ Benchmark operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sector_operations(repo: DatabaseRepository):
    """Test 5: Sector and peer analysis operations"""
    print_section("TEST 5: Sector & Peer Operations")
    
    try:
        # Add more tech companies
        repo.save_company("Microsoft Corporation", "MSFT", "Technology", "Software")
        repo.save_company("Google Inc.", "GOOGL", "Technology", "Internet")
        print("✓ Additional companies added")
        
        # Get sector companies
        tech_companies = repo.get_sector_companies("Technology")
        print(f"✓ Technology sector companies: {len(tech_companies)}")
        for company in tech_companies:
            print(f"  - {company.name} ({company.ticker})")
        
        # Calculate sector benchmark (requires analyses)
        # Note: This will return empty since we haven't added analyses for all companies
        benchmark_stats = repo.calculate_sector_benchmark(
            sector="Technology",
            metric_name="hybrid_sentiment_score",
            quarter="Q4",
            year=2024
        )
        print(f"✓ Sector benchmark calculated")
        print(f"  Count: {benchmark_stats['count']} companies")
        if benchmark_stats['mean'] is not None:
            print(f"  Mean: {benchmark_stats['mean']:.2f}")
            print(f"  Median: {benchmark_stats['median']:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Sector operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_stats(repo: DatabaseRepository):
    """Test 6: Database statistics"""
    print_section("TEST 6: Database Statistics")
    
    try:
        stats = repo.get_database_stats()
        print(f"✓ Database statistics retrieved:")
        print(f"  - Companies: {stats['companies']}")
        print(f"  - Analyses: {stats['analyses']}")
        print(f"  - Benchmarks: {stats['benchmarks']}")
        
        return True
    except Exception as e:
        print(f"✗ Stats retrieval failed: {e}")
        return False


def cleanup(repo: DatabaseRepository):
    """Cleanup test data"""
    print_section("CLEANUP")
    
    try:
        # Delete test database file
        test_db_path = Path("./data/test_earnings.db")
        if test_db_path.exists():
            test_db_path.unlink()
            print("✓ Test database deleted")
        else:
            print("  No test database to clean up")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")


def main():
    """Run all tests"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PHASE 2B DATABASE INTEGRATION TESTS" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    
    tests_passed = 0
    tests_total = 6
    
    # Test 1: Database Setup
    repo, passed = test_database_setup()
    if passed:
        tests_passed += 1
    
    if repo is None:
        print("\n❌ Cannot continue without database connection")
        return
    
    # Test 2: Company Operations
    if test_company_operations(repo):
        tests_passed += 1
    
    # Test 3: Analysis Operations
    if test_analysis_operations(repo):
        tests_passed += 1
    
    # Test 4: Benchmark Operations
    if test_benchmark_operations(repo):
        tests_passed += 1
    
    # Test 5: Sector Operations
    if test_sector_operations(repo):
        tests_passed += 1
    
    # Test 6: Database Stats
    if test_database_stats(repo):
        tests_passed += 1
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"\nResults: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("\n🎉 ALL TESTS PASSED! Phase 2B database implementation successful.")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed")
    
    # Cleanup
    cleanup(repo)
    
    print("\n" + "=" * 80)
    print("Phase 2B Testing Complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
