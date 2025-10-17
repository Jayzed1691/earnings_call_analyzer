# Phase 2B Quick Reference Guide

## 🚀 Quick Start

### 1. Setup Database
```bash
python scripts/setup_database.py --seed
```

### 2. Use in Your Code
```python
from src.database.repository import DatabaseRepository
from config.settings import settings

# Initialize
repo = DatabaseRepository(settings.DATABASE_URL)

# Save company
company_id = repo.save_company("Apple Inc.", "AAPL", "Technology")

# Save analysis
analysis_id = repo.save_analysis(
    company_name="Apple Inc.",
    quarter="Q4",
    year=2024,
    analysis_result=your_analysis_result
)

# Query data
latest = repo.get_latest_analysis("Apple Inc.")
historical = repo.load_historical_analyses("Apple Inc.", quarters=4)
```

---

## 📊 Common Operations

### Company Management
```python
# Create/Update
company_id = repo.save_company(name, ticker, sector, industry)

# Get
company = repo.get_company(name="Apple Inc.")
company = repo.get_company(ticker="AAPL")

# Search
results = repo.search_companies("Apple")

# Get by sector
tech_companies = repo.get_sector_companies("Technology")

# Get all
all_companies = repo.get_all_companies()
```

### Analysis Operations
```python
# Save
analysis_id = repo.save_analysis(company_name, quarter, year, result)

# Get specific quarter
analysis = repo.load_analysis(company_name, quarter, year)

# Get historical (last N quarters)
analyses = repo.load_historical_analyses(company_name, quarters=8)

# Get latest
latest = repo.get_latest_analysis(company_name)

# Delete
success = repo.delete_analysis(analysis_id)
```

### Benchmarks
```python
# Save
repo.save_benchmark(sector, metric_name, value, quarter=None, year=None)

# Get
benchmark = repo.get_benchmark(sector, metric_name, quarter, year)

# Get all for sector
benchmarks = repo.get_all_benchmarks(sector="Technology")

# Calculate sector statistics
stats = repo.calculate_sector_benchmark(sector, metric_name, quarter, year)
# Returns: {'mean': X, 'median': Y, 'std_dev': Z, 'min': A, 'max': B, 'count': N}
```

### Peer Comparison
```python
# Get analyses for multiple companies (same quarter)
peer_analyses = repo.get_peer_analyses(
    company_names=["Apple Inc.", "Microsoft Corporation"],
    quarter="Q4",
    year=2024
)
```

---

## 🗄️ Database Schema Reference

### Available Fields in AnalysisResult

**Sentiment (Phase 1)**
- `hybrid_sentiment_score` (Float)
- `sentiment_label` (String: Positive/Neutral/Negative)
- `lexicon_net_positivity` (Float)
- `llm_sentiment_score` (Float)

**Complexity (Phase 1)**
- `complexity_composite_score` (Float)
- `complexity_level` (String: Low/Moderate/High)
- `flesch_reading_ease` (Float)
- `flesch_kincaid_grade` (Float)
- `gunning_fog_index` (Float)
- `smog_index` (Float)
- `coleman_liau_index` (Float)

**Numerical (Phase 1)**
- `numeric_transparency_score` (Float)
- `numerical_specificity_index` (Float)
- `forward_looking_density` (Float)
- `backward_looking_density` (Float)
- `forward_to_backward_ratio` (Float)
- `contextualization_quality_score` (Float)
- `vs_sp500_benchmark` (String: above/at/below)

**Deception (Phase 2A)**
- `deception_risk_score` (Float 0-100)
- `deception_risk_level` (String: Low/Moderate/High/Critical)
- `deception_confidence` (Float 0-1)
- `hedging_density` (Float)
- `qualifier_density` (Float)
- `passive_voice_percentage` (Float)
- `pronoun_distancing_percentage` (Float)

**Evasiveness (Phase 2A)**
- `evasiveness_score` (Float 0-100)
- `evasiveness_level` (String: Low/Moderate/High)
- `evasiveness_vs_baseline` (String: above/at/below)

**Other**
- `word_count` (Integer)
- `sentence_count` (Integer)
- `full_results_json` (JSON - complete result)
- `key_findings` (Text)
- `red_flags` (Text)
- `strengths` (Text)

---

## 🔍 Query Examples

### Historical Trend Analysis
```python
# Get last 8 quarters
analyses = repo.load_historical_analyses("Apple Inc.", quarters=8)

# Extract sentiment trend
sentiments = [a.hybrid_sentiment_score for a in analyses]
quarters = [f"{a.quarter} {a.year}" for a in analyses]

print("Sentiment Trend:")
for q, s in zip(quarters, sentiments):
    print(f"{q}: {s:.1f}")
```

### Sector Benchmarking
```python
# Calculate sector average for Q4 2024
stats = repo.calculate_sector_benchmark(
    sector="Technology",
    metric_name="deception_risk_score",
    quarter="Q4",
    year=2024
)

print(f"Technology Sector Q4 2024:")
print(f"  Average Deception Risk: {stats['mean']:.1f}")
print(f"  Range: {stats['min']:.1f} - {stats['max']:.1f}")
print(f"  Companies: {stats['count']}")
```

### Peer Comparison
```python
# Compare Apple vs competitors
companies = ["Apple Inc.", "Microsoft Corporation", "Google Inc."]
analyses = repo.get_peer_analyses(companies, "Q4", 2024)

for analysis in analyses:
    print(f"{analysis.company.name}:")
    print(f"  Sentiment: {analysis.hybrid_sentiment_score:.1f}")
    print(f"  Deception Risk: {analysis.deception_risk_score:.1f}")
    print()
```

### Find High-Risk Companies
```python
from sqlalchemy import and_
from src.database.models import AnalysisResult, Company

# Direct SQL-alchemy query for advanced filtering
session = repo._get_session()
try:
    high_risk = session.query(AnalysisResult)\
        .join(Company)\
        .filter(
            and_(
                AnalysisResult.year == 2024,
                AnalysisResult.deception_risk_score > 60
            )
        )\
        .order_by(AnalysisResult.deception_risk_score.desc())\
        .all()
    
    for analysis in high_risk:
        print(f"{analysis.company.name} ({analysis.quarter} {analysis.year})")
        print(f"  Risk Score: {analysis.deception_risk_score:.1f}")
finally:
    session.close()
```

---

## 🛠️ Database Maintenance

### Get Statistics
```python
stats = repo.get_database_stats()
print(f"Companies: {stats['companies']}")
print(f"Analyses: {stats['analyses']}")
print(f"Benchmarks: {stats['benchmarks']}")
```

### Backup Database
```bash
# SQLite backup
cp data/earnings_analyzer.db data/backups/earnings_analyzer_backup_$(date +%Y%m%d).db
```

### Reset Database
```bash
# DANGER: Deletes all data
python scripts/setup_database.py --reset --seed
```

### Migration to PostgreSQL
```python
# Change DATABASE_URL in config/settings.py
DATABASE_URL = "postgresql://user:pass@localhost/earnings_analyzer"

# Run setup
python scripts/setup_database.py
```

---

## ⚠️ Common Pitfalls

### 1. Company Must Exist Before Analysis
```python
# ✗ Wrong - will create company with ticker="UNKNOWN"
repo.save_analysis("New Company", "Q4", 2024, result)

# ✓ Correct - create company first
repo.save_company("New Company", "NEWCO", "Technology")
repo.save_analysis("New Company", "Q4", 2024, result)
```

### 2. Handle None Values
```python
analysis = repo.load_analysis("Unknown Co.", "Q4", 2024)
if analysis is None:
    print("Analysis not found!")
else:
    print(f"Sentiment: {analysis.hybrid_sentiment_score}")
```

### 3. Check Benchmark Existence
```python
benchmark = repo.get_benchmark("Unknown Sector", "metric")
if benchmark is None:
    print("Benchmark not set for this sector")
```

### 4. Session Management
```python
# Repository handles sessions automatically
# Don't need to manage sessions manually unless doing complex queries

# For complex queries, use try/finally
session = repo._get_session()
try:
    # Your complex query
    results = session.query(...).all()
finally:
    session.close()  # Always close!
```

---

## 📈 Performance Tips

1. **Use Indexes**: Queries on `company_id`, `year`, `quarter` are indexed
2. **Batch Operations**: Save multiple records in a transaction
3. **Limit Historical Queries**: Use `quarters` parameter wisely
4. **Cache Benchmark Calculations**: They're expensive for large datasets

---

## 🧪 Testing

```bash
# Run integration tests
python test_phase2b_database.py

# Expected output: 6/6 tests passed
```

---

## 📞 Need Help?

- Check `PHASE_2B_COMPLETE.md` for full documentation
- Review `src/database/repository.py` for all available methods
- See `test_phase2b_database.py` for usage examples
