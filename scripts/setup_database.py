#!/usr/bin/env python3
"""
Database Setup Script

Creates database tables and optionally seeds initial benchmark data.

Usage:
    python scripts/setup_database.py              # Create tables only
    python scripts/setup_database.py --seed       # Create tables and seed benchmarks
    python scripts/setup_database.py --reset      # Drop all tables and recreate
"""

from pathlib import Path
import sys
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.database.models import Base
from src.database.repository import DatabaseRepository
from sqlalchemy import create_engine


def setup_database(reset: bool = False):
    """
    Create database tables
    
    Args:
        reset: If True, drop all existing tables first
    """
    print("=" * 80)
    print("EARNINGS CALL ANALYZER - DATABASE SETUP")
    print("=" * 80)
    print(f"\nDatabase URL: {settings.DATABASE_URL}")
    print(f"Database Path: {settings.DATABASE_PATH}")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    if reset:
        print("\n⚠️  WARNING: Dropping all existing tables...")
        response = input("Are you sure? This will delete all data! (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
        
        Base.metadata.drop_all(engine)
        print("✓ All tables dropped")
    
    # Create all tables
    print("\n📊 Creating database tables...")
    Base.metadata.create_all(engine)
    
    print("✓ Tables created successfully!")
    print("\nCreated tables:")
    print("  - companies")
    print("  - analysis_results")
    print("  - benchmarks")
    
    # Show database location
    print(f"\n📁 Database file location:")
    print(f"   {settings.DATABASE_PATH.absolute()}")
    
    print("\n✅ Database setup complete!")


def seed_benchmarks():
    """Seed initial benchmark data"""
    print("\n" + "=" * 80)
    print("SEEDING BENCHMARK DATA")
    print("=" * 80)
    
    repo = DatabaseRepository(settings.DATABASE_URL)
    
    print("\n📈 Adding S&P 500 benchmarks...")
    
    # S&P 500 baseline metrics
    benchmarks_added = 0
    
    # Net Positivity
    if hasattr(settings, 'SP500_NET_POSITIVITY'):
        repo.save_benchmark("S&P 500", "net_positivity", settings.SP500_NET_POSITIVITY)
        print(f"  ✓ Net Positivity: {settings.SP500_NET_POSITIVITY}")
        benchmarks_added += 1
    
    # Numeric Transparency
    if hasattr(settings, 'SP500_NUMERIC_TRANSPARENCY'):
        repo.save_benchmark("S&P 500", "numeric_transparency", settings.SP500_NUMERIC_TRANSPARENCY)
        print(f"  ✓ Numeric Transparency: {settings.SP500_NUMERIC_TRANSPARENCY}")
        benchmarks_added += 1
    
    # Evasiveness
    if hasattr(settings, 'SP500_EVASIVENESS_BASELINE'):
        repo.save_benchmark("S&P 500", "evasiveness", settings.SP500_EVASIVENESS_BASELINE)
        print(f"  ✓ Evasiveness: {settings.SP500_EVASIVENESS_BASELINE}")
        benchmarks_added += 1
    
    # Add sector-specific benchmarks if available
    if hasattr(settings, 'SECTOR_NUMERIC_TRANSPARENCY'):
        print("\n📊 Adding sector-specific benchmarks...")
        for sector, transparency in settings.SECTOR_NUMERIC_TRANSPARENCY.items():
            repo.save_benchmark(sector, "numeric_transparency", transparency)
            print(f"  ✓ {sector}: {transparency}")
            benchmarks_added += 1
    
    print(f"\n✅ Seeded {benchmarks_added} benchmark values!")


def show_stats():
    """Show database statistics"""
    print("\n" + "=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    
    repo = DatabaseRepository(settings.DATABASE_URL)
    stats = repo.get_database_stats()
    
    print(f"\n📊 Current database contents:")
    print(f"   Companies:  {stats['companies']}")
    print(f"   Analyses:   {stats['analyses']}")
    print(f"   Benchmarks: {stats['benchmarks']}")


def main():
    parser = argparse.ArgumentParser(
        description='Setup database for Earnings Call Analyzer'
    )
    parser.add_argument(
        '--seed',
        action='store_true',
        help='Seed initial benchmark data after setup'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Drop all existing tables and recreate (DANGER: deletes all data)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    
    args = parser.parse_args()
    
    try:
        # Setup database
        if not args.stats:
            setup_database(reset=args.reset)
        
        # Seed benchmarks if requested
        if args.seed:
            seed_benchmarks()
        
        # Show stats if requested or after setup
        if args.stats or not args.stats:
            show_stats()
        
        print("\n" + "=" * 80)
        print("🎉 All done!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Run analysis with --save-db flag to store results")
        print("  2. Use historical command to view trends")
        print("  3. Use compare command for peer analysis")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
