# Earnings Call Analyzer - Phase 2 Specification

**Version:** 2.0.0  
**Date:** 2025-01-15  
**Status:** Development Roadmap

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1 Status & Required Revisions](#phase-1-status--required-revisions)
3. [Phase 2 Architecture](#phase-2-architecture)
4. [Module Specifications](#module-specifications)
5. [Data Models & Schemas](#data-models--schemas)
6. [Integration Points](#integration-points)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Considerations](#deployment-considerations)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Overview

### Phase 2 Goals

Phase 2 transforms the Earnings Call Analyzer from a batch analysis tool into a comprehensive platform with:

1. **Advanced Detection**: Deception risk scoring, evasiveness detection, question avoidance analysis
2. **Comparative Intelligence**: Historical trending, peer comparison, sector benchmarking
3. **Rich Reporting**: PDF reports, interactive dashboards, Excel exports
4. **API & Web Interface**: RESTful API, web dashboard, real-time analysis
5. **Pattern Recognition**: Communication pattern detection, predictive analytics

### Phase 2 Features Summary

| Category | Features | Priority | Status |
|----------|----------|----------|--------|
| **Deception Analysis** | Risk scoring, linguistic markers, behavioral indicators | **HIGH** | Partially Complete |
| **Evasiveness Detection** | Question avoidance, topic deflection, response quality | **HIGH** | Partially Complete |
| **Historical Analysis** | Multi-quarter trends, metric evolution, seasonality | **MEDIUM** | Not Started |
| **Peer Comparison** | Industry benchmarks, sector rankings, competitive positioning | **MEDIUM** | Not Started |
| **Advanced Reporting** | PDF generation, HTML dashboards, Excel exports | **HIGH** | Not Started |
| **API & Web** | REST API, web interface, job queue | **MEDIUM** | Not Started |
| **Pattern Recognition** | Behavior patterns, early warnings, predictions | **LOW** | Not Started |

---

## Phase 1 Status & Required Revisions

### Phase 1 Completed Modules

✅ **Core Infrastructure**
- `src/core/transcript_processor.py` - Transcript loading and parsing
- `config/settings.py` - Configuration management
- `src/utils/text_utils.py` - Text processing utilities

✅ **Sentiment Analysis**
- `src/analysis/sentiment/lexicon_analyzer.py` - LM dictionary-based analysis
- `src/analysis/sentiment/llm_analyzer.py` - Ollama LLM sentiment
- `src/analysis/sentiment/hybrid_scorer.py` - Hybrid approach (30% lexicon, 70% LLM)

✅ **Complexity Analysis**
- `src/analysis/complexity/readability.py` - 5 readability metrics + composite score

✅ **Numerical Analysis**
- `src/analysis/numerical/transparency.py` - 4 numerical metrics

✅ **Aggregation & CLI**
- `src/analysis/aggregator.py` - Main analysis orchestrator
- `cli.py` - Command-line interface

✅ **Deception Modules (Partially Complete - Need Integration)**
- `src/deception/detector.py` - Deception risk analyzer
- `src/deception/linguistic_markers.py` - Linguistic pattern detection
- `src/deception/evasiveness.py` - Evasiveness scoring
- `src/deception/question_evasion.py` - Q&A analysis

### Required Phase 1 Revisions

#### 1. Reorganize Deception Module Structure

**Current:** `src/deception/`  
**Target:** `src/analysis/deception/`

**Action:**
```bash
# Move deception modules to analysis directory
mv src/deception/* src/analysis/deception/
rm -rf src/deception/
```

**Update imports in:**
- `src/deception/__init__.py` → `src/analysis/deception/__init__.py`
- All files that import from `src.deception` → `src.analysis.deception`

#### 2. Update `aggregator.py` Integration

**File:** `src/analysis/aggregator.py`

**Changes:**
```python
# Add to imports
from src.analysis.deception.detector import DeceptionRiskAnalyzer, DeceptionRiskScore
from src.analysis.deception.evasiveness import EvasivenessAnalyzer, EvasivenessScores
from src.analysis.deception.question_evasion import QuestionEvasionDetector, QuestionResponse

# Add to __init__
def __init__(self, use_llm_features: bool = True):
    # ... existing analyzers ...
    self.deception_analyzer = DeceptionRiskAnalyzer()
    self.evasiveness_analyzer = EvasivenessAnalyzer()
    self.qa_detector = QuestionEvasionDetector()

# Update ComprehensiveAnalysisResult dataclass
@dataclass
class ComprehensiveAnalysisResult:
    # ... existing Phase 1 fields ...
    
    # Phase 2 additions
    deception_risk: DeceptionRiskScore
    evasiveness_scores: EvasivenessScores
    qa_analysis: Optional[List[QuestionResponse]] = None

# Add to analyze_transcript() method (after existing analysis)
# Phase 2: Deception risk analysis
print("  → Analyzing deception risk indicators...")
deception_risk = self.deception_analyzer.analyze(
    transcript=transcript,
    sentiment_scores=overall_sentiment,
    complexity_scores=overall_complexity,
    numerical_scores=overall_numerical,
    section_analysis={
        'prepared_remarks': section_complexity.get('prepared_remarks'),
        'qa': section_complexity.get('qa')
    }
)

# Phase 2: Evasiveness analysis
print("  → Analyzing language evasiveness...")
evasiveness = self.evasiveness_analyzer.analyze(transcript.cleaned_text)

# Phase 2: Q&A analysis (if Q&A section exists)
qa_analysis = None
if transcript.sections.get('qa'):
    print("  → Analyzing Q&A exchanges...")
    qa_pairs = self.qa_detector.analyze_qa_section(transcript.sections['qa'])
    qa_analysis = qa_pairs

# Update result object construction
result = ComprehensiveAnalysisResult(
    # ... all existing Phase 1 fields ...
    deception_risk=deception_risk,
    evasiveness_scores=evasiveness,
    qa_analysis=qa_analysis,
    # ... rest of fields ...
)
```

#### 3. Update `_generate_insights()` Method

**File:** `src/analysis/aggregator.py`

**Add to `_generate_insights()` method:**
```python
def _generate_insights(
    self,
    overall_sentiment: HybridSentimentScores,
    overall_complexity: ComplexityScores,
    overall_numerical: NumericalScores,
    section_sentiment: Dict,
    section_complexity: Dict,
    deception_risk: DeceptionRiskScore,  # NEW
    evasiveness: EvasivenessScores       # NEW
) -> tuple:
    """Generate key findings, red flags, and strengths"""
    key_findings = []
    red_flags = []
    strengths = []
    
    # ... existing Phase 1 insight generation ...
    
    # Phase 2: Deception risk insights
    if deception_risk.risk_level == "Critical":
        red_flags.append(f"CRITICAL deception risk detected ({deception_risk.overall_risk_score:.0f}/100)")
        key_findings.append(f"Multiple deception indicators triggered: {len(deception_risk.triggered_flags)} flags")
    elif deception_risk.risk_level == "High":
        red_flags.append(f"High deception risk ({deception_risk.overall_risk_score:.0f}/100)")
    elif deception_risk.risk_level == "Low":
        strengths.append(f"Low deception risk ({deception_risk.overall_risk_score:.0f}/100)")
    
    # Phase 2: Evasiveness insights
    if evasiveness.vs_baseline == "above":
        if evasiveness.evasiveness_level in ["High", "Very High"]:
            red_flags.append(f"{evasiveness.evasiveness_level} evasiveness detected ({evasiveness.overall_evasiveness:.1f} vs {settings.SP500_EVASIVENESS_BASELINE} baseline)")
    elif evasiveness.vs_baseline == "below":
        strengths.append(f"Below-average evasiveness (transparent communication)")
    
    # Phase 2: Q&A evasion insights
    if deception_risk.indicators.question_dodge_rate > settings.QUESTION_AVOIDANCE_ALERT:
        red_flags.append(f"High question evasion rate in Q&A ({deception_risk.indicators.question_dodge_rate:.1f}%)")
    
    return key_findings, red_flags, strengths
```

#### 4. Update `print_summary()` Method

**File:** `src/analysis/aggregator.py`

**Add Phase 2 sections:**
```python
def print_summary(self, results: ComprehensiveAnalysisResult) -> None:
    """Print a human-readable summary of results"""
    # ... existing Phase 1 summary ...
    
    # Phase 2: Deception Risk
    print("\n⚠️  DECEPTION RISK ASSESSMENT")
    print("-" * 80)
    risk_emoji = {
        "Low": "🟢",
        "Moderate": "🟡", 
        "High": "🟠",
        "Critical": "🔴"
    }
    print(f"{risk_emoji.get(results.deception_risk.risk_level, '⚪')} Overall Risk: {results.deception_risk.risk_level} ({results.deception_risk.overall_risk_score:.0f}/100)")
    print(f"Confidence: {results.deception_risk.confidence:.0%}")
    
    if results.deception_risk.triggered_flags:
        print("\nTriggered Flags:")
        for flag in results.deception_risk.triggered_flags[:5]:  # Show top 5
            print(f"  • {flag}")
    
    # Phase 2: Evasiveness
    print("\n📊 EVASIVENESS ASSESSMENT")
    print("-" * 80)
    print(f"Overall Evasiveness: {results.evasiveness_scores.overall_evasiveness:.1f} ({results.evasiveness_scores.evasiveness_level})")
    print(f"vs S&P 500 Baseline: {results.evasiveness_scores.vs_baseline} ({settings.SP500_EVASIVENESS_BASELINE})")
    
    # Phase 2: Q&A Analysis
    if results.qa_analysis:
        print("\n💬 Q&A ANALYSIS")
        print("-" * 80)
        evasive_count = sum(1 for qa in results.qa_analysis if qa.is_evasive)
        total_count = len(results.qa_analysis)
        print(f"Questions Analyzed: {total_count}")
        print(f"Evasive Responses: {evasive_count} ({evasive_count/total_count*100:.1f}%)")
        
        if evasive_count > 0:
            most_evasive = sorted(results.qa_analysis, key=lambda x: x.response_relevance)[:3]
            print("\nMost Evasive Exchanges:")
            for i, qa in enumerate(most_evasive, 1):
                print(f"  {i}. {qa.evasion_type} (relevance: {qa.response_relevance:.2f})")
                print(f"     Q: {qa.question[:80]}...")
    
    print("\n" + "="*80)
```

#### 5. Add Configuration for Phase 2

**File:** `config/settings.py`

**Add settings:**
```python
class Settings(BaseSettings):
    # ... existing Phase 1 settings ...
    
    # ===== PHASE 2 SETTINGS =====
    
    # Database
    DATABASE_PATH: Path = DATA_DIR / "earnings_analyzer.db"
    DATABASE_URL: str = Field(
        default="sqlite:///./data/earnings_analyzer.db",
        env="DATABASE_URL"
    )
    
    # API settings
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")
    
    # Report settings
    REPORT_OUTPUT_DIR: Path = DATA_DIR / "reports"
    ENABLE_PDF_REPORTS: bool = Field(default=True, env="ENABLE_PDF_REPORTS")
    ENABLE_HTML_DASHBOARDS: bool = Field(default=True, env="ENABLE_HTML_DASHBOARDS")
    ENABLE_EXCEL_EXPORTS: bool = Field(default=True, env="ENABLE_EXCEL_EXPORTS")
    
    # Feature flags
    ENABLE_DECEPTION_ANALYSIS: bool = Field(default=True, env="ENABLE_DECEPTION_ANALYSIS")
    ENABLE_EVASIVENESS_ANALYSIS: bool = Field(default=True, env="ENABLE_EVASIVENESS_ANALYSIS")
    ENABLE_QA_ANALYSIS: bool = Field(default=True, env="ENABLE_QA_ANALYSIS")
    ENABLE_HISTORICAL_TRACKING: bool = Field(default=True, env="ENABLE_HISTORICAL_TRACKING")
    ENABLE_PEER_COMPARISON: bool = Field(default=True, env="ENABLE_PEER_COMPARISON")
    
    # Historical analysis
    HISTORICAL_DATA_RETENTION_QUARTERS: int = 12
    
    # Job queue
    USE_REDIS_QUEUE: bool = Field(default=False, env="USE_REDIS_QUEUE")
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    JOB_TIMEOUT: int = 600  # seconds
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Path = PROJECT_ROOT / "logs" / "analyzer.log"
```

#### 6. Update CLI for Phase 2

**File:** `cli.py`

**Add new commands:**
```python
@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output JSON file path', default=None)
@click.option('--no-llm', is_flag=True, help='Disable LLM features')
@click.option('--summary', '-s', is_flag=True, help='Print summary to console')
@click.option('--with-deception', is_flag=True, help='Include deception analysis (Phase 2)')
def analyze(transcript_file, output, no_llm, summary, with_deception):
    """Analyze an earnings call transcript (Phase 1 + Phase 2)"""
    # ... existing code ...
    
    if with_deception:
        click.echo("  → Deception analysis enabled")

@cli.command()
@click.argument('company')
@click.option('--quarters', '-q', default=4, help='Number of quarters to analyze')
def historical(company, quarters):
    """
    Analyze historical trends for a company (Phase 2)
    
    Example:
        earnings-analyzer historical AAPL --quarters 8
    """
    from src.analysis.comparative.historical import HistoricalTrendAnalyzer
    from config.settings import settings
    
    click.echo(f"\nAnalyzing {quarters} quarters of historical data for {company}...\n")
    
    analyzer = HistoricalTrendAnalyzer(settings.DATABASE_PATH)
    trends = analyzer.generate_trend_report(company, quarters)
    
    # Print trend summary
    for metric_name, trend in trends.items():
        click.echo(f"{metric_name}:")
        click.echo(f"  Trend: {trend.trend_direction} (strength: {trend.trend_strength:.2f})")
        click.echo(f"  Volatility: {trend.volatility:.2f}")
        if trend.forecast_next_quarter:
            click.echo(f"  Forecast: {trend.forecast_next_quarter:.2f}")
        click.echo()

@cli.command()
@click.argument('company')
@click.option('--peers', '-p', help='Comma-separated peer companies', default=None)
@click.option('--sector', '-s', help='GICS sector for comparison', default=None)
def compare(company, peers, sector):
    """
    Compare company to peers or sector (Phase 2)
    
    Example:
        earnings-analyzer compare AAPL --peers MSFT,GOOGL
        earnings-analyzer compare AAPL --sector "Information Technology"
    """
    from src.analysis.comparative.peer_comparison import PeerComparisonEngine
    
    engine = PeerComparisonEngine(settings.DATABASE_PATH)
    
    if peers:
        peer_list = [p.strip() for p in peers.split(',')]
        results = engine.compare_to_peers(company, peer_list)
    elif sector:
        results = engine.compare_to_sector(company, sector, "Q4", 2024)
    else:
        click.echo("Error: Must specify either --peers or --sector", err=True)
        return
    
    # Print comparison results
    for metric, comparison in results.items():
        click.echo(f"\n{metric}:")
        click.echo(f"  {company}: {comparison.company_value:.2f}")
        click.echo(f"  Sector Mean: {comparison.sector_mean:.2f}")
        click.echo(f"  Percentile: {comparison.percentile_rank:.0f}th")
        click.echo(f"  vs Peers: {comparison.vs_peers}")

@cli.command()
def serve():
    """Start the API server (Phase 2)"""
    import uvicorn
    from config.settings import settings
    
    click.echo(f"\nStarting API server on {settings.API_HOST}:{settings.API_PORT}...\n")
    
    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
```

---

## Phase 2 Architecture

### Directory Structure

```
earnings-call-analyzer/
├── src/
│   ├── analysis/
│   │   ├── sentiment/          # Phase 1 ✅
│   │   ├── complexity/         # Phase 1 ✅
│   │   ├── numerical/          # Phase 1 ✅
│   │   ├── deception/          # Phase 2 (move from src/deception/)
│   │   │   ├── __init__.py
│   │   │   ├── detector.py     # Deception risk analyzer
│   │   │   ├── linguistic_markers.py
│   │   │   ├── evasiveness.py
│   │   │   └── question_evasion.py
│   │   ├── comparative/        # Phase 2 NEW
│   │   │   ├── __init__.py
│   │   │   ├── historical.py
│   │   │   └── peer_comparison.py
│   │   └── aggregator.py       # Phase 1 (needs Phase 2 updates)
│   ├── reporting/              # Phase 2 NEW
│   │   ├── __init__.py
│   │   ├── pdf_generator.py
│   │   ├── html_dashboard.py
│   │   └── excel_exporter.py
│   ├── api/                    # Phase 2 NEW
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── jobs.py
│   ├── web/                    # Phase 2 NEW
│   │   ├── static/
│   │   │   ├── css/
│   │   │   └── js/
│   │   └── templates/
│   │       ├── report.html
│   │       └── dashboard.html
│   ├── analytics/              # Phase 2 NEW (LOW PRIORITY)
│   │   ├── __init__.py
│   │   ├── patterns.py
│   │   └── predictions.py
│   ├── database/               # Phase 2 NEW
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── repository.py
│   └── utils/
│       ├── text_utils.py       # Phase 1 ✅
│       └── visualization.py    # Phase 2 NEW
├── config/
│   ├── settings.py             # Phase 1 (needs Phase 2 updates)
│   └── models.yaml             # Phase 1 ✅
├── data/
│   ├── dictionaries/           # Phase 1 ✅
│   ├── benchmarks/             # Phase 1 ✅
│   ├── reports/                # Phase 2 NEW
│   └── earnings_analyzer.db    # Phase 2 NEW
├── tests/
│   ├── unit/
│   │   ├── test_deception_detector.py
│   │   ├── test_historical_analyzer.py
│   │   └── ...
│   └── integration/
│       ├── test_full_pipeline.py
│       └── test_api_endpoints.py
├── scripts/
│   ├── download_dictionaries.py
│   ├── setup_nlp.py
│   └── setup_database.py       # Phase 2 NEW
├── cli.py                      # Phase 1 (needs Phase 2 commands)
├── requirements.txt            # Phase 1
├── requirements-phase2.txt     # Phase 2 NEW
├── Dockerfile                  # Phase 2 NEW
├── docker-compose.yml          # Phase 2 NEW
└── README.md
```

### Technology Stack

**Phase 1:**
- Python 3.10+
- Ollama (LLM inference)
- NLTK (text processing)
- spaCy (NER - optional)
- Click (CLI)

**Phase 2 Additions:**
- **FastAPI** - REST API framework
- **SQLAlchemy** - ORM for database
- **SQLite** - Database (PostgreSQL for production)
- **Plotly** - Interactive charts
- **WeasyPrint** - HTML → PDF conversion
- **openpyxl** - Excel generation
- **Jinja2** - HTML templates
- **Redis** (optional) - Job queue
- **uvicorn** - ASGI server

---

## Module Specifications

### 1. Deception Detection Module (Phase 2A)

**Location:** `src/analysis/deception/`  
**Priority:** HIGH  
**Status:** Partially Complete - Needs Integration

#### 1.1 Overview

The deception detection module provides comprehensive risk assessment by analyzing linguistic patterns, behavioral indicators, numerical red flags, and question evasion patterns.

#### 1.2 Deception Risk Analyzer (`detector.py`)

**Status:** ✅ Implemented (needs integration)

**Purpose:** Calculate composite deception risk score from 13 individual indicators

**Key Classes:**

```python
@dataclass
class DeceptionIndicators:
    """Individual deception indicators (0-100 scale)"""
    # Linguistic (25% weight)
    hedging_score: float
    qualifier_density: float
    modal_weakness_score: float
    passive_voice_ratio: float
    pronoun_distancing: float
    
    # Behavioral (25% weight)
    complexity_spike_qa: float
    sentiment_drop_qa: float
    response_length_variance: float
    
    # Numerical (30% weight)
    forward_avoidance: float
    vague_number_ratio: float
    contextualization_gap: float
    
    # Evasion (20% weight)
    question_dodge_rate: float
    topic_deflection_score: float

@dataclass
class DeceptionRiskScore:
    overall_risk_score: float  # 0-100
    risk_level: str  # Low, Moderate, High, Critical
    confidence: float  # 0-1
    indicators: DeceptionIndicators
    triggered_flags: List[str]
    risk_components: Dict[str, float]
    most_evasive_questions: List[Dict]
    complexity_hotspots: List[Tuple[str, float]]
    numerical_red_flags: List[Dict]

class DeceptionRiskAnalyzer:
    def __init__(self):
        self.linguistic_analyzer = LinguisticDeceptionMarkers()
        self.evasiveness_analyzer = EvasivenessAnalyzer()
    
    def analyze(
        self,
        transcript: ProcessedTranscript,
        sentiment_scores: HybridSentimentScores,
        complexity_scores: ComplexityScores,
        numerical_scores: NumericalScores,
        section_analysis: Dict
    ) -> DeceptionRiskScore:
        """Comprehensive deception risk assessment"""
```

**Weighting Formula:**
```python
overall_risk = (
    linguistic_component * 0.25 +   # Hedging, qualifiers, passive voice, etc.
    behavioral_component * 0.25 +   # Complexity spikes, sentiment drops
    numerical_component * 0.30 +    # Forward avoidance, vague numbers
    evasion_component * 0.20        # Question dodging, topic deflection
)
```

**Risk Categorization:**
- **Low:** 0-29
- **Moderate:** 30-49
- **High:** 50-69 (`settings.DECEPTION_RISK_WARNING`)
- **Critical:** 70-100 (`settings.DECEPTION_RISK_CRITICAL`)

**Integration Steps:**
1. Import in `aggregator.py`
2. Instantiate in `__init__`
3. Call in `analyze_transcript()` after all Phase 1 analysis
4. Add to `ComprehensiveAnalysisResult`
5. Display in `print_summary()`

#### 1.3 Linguistic Deception Markers (`linguistic_markers.py`)

**Status:** ✅ Implemented

**Purpose:** Detect linguistic patterns associated with deception

**Key Methods:**

```python
class LinguisticDeceptionMarkers:
    def calculate_hedging_density(self, text: str) -> float
        """Calculate % of hedging words (perhaps, possibly, maybe, etc.)"""
    
    def calculate_qualifier_density(self, text: str) -> float
        """Calculate % of qualifiers (approximately, around, roughly, etc.)"""
    
    def calculate_modal_weakness(self, speakers: Dict, sentiment_scores) -> float
        """Calculate weak modal / strong modal ratio"""
    
    def detect_passive_voice(self, text: str) -> float
        """Detect passive voice constructions (uses spaCy if available)"""
    
    def analyze_pronoun_distancing(self, text: str) -> Dict[str, float]
        """Analyze "the company" vs "we/our" usage"""
    
    def calculate_vague_pronoun_usage(self, text: str) -> float
        """Calculate usage of vague pronouns (it, that, thing, etc.)"""
    
    def detect_euphemisms(self, text: str) -> List[str]
        """Detect business euphemisms (challenged, rightsizing, etc.)"""
    
    def calculate_specificity_index(self, text: str) -> float
        """Overall linguistic specificity (inverse of vagueness)"""
```

**Linguistic Markers Detected:**
- **Hedging words:** perhaps, possibly, maybe, might, could, somewhat, fairly, relatively, basically, essentially
- **Qualifiers:** approximately, around, roughly, about, nearly, almost, close to
- **Weak modals:** might, could, may, possibly, perhaps, maybe, potentially
- **Strong modals:** will, shall, must, definitely, certainly, absolutely
- **Distancing phrases:** "the company", "the organization", "the business" (vs "we", "our")
- **Vague pronouns:** it, that, this, thing, stuff
- **Euphemisms:** challenged (struggling), rightsizing (layoffs), headwinds (problems)

**Dependencies:**
- spaCy (optional, for improved passive voice detection)
- Uses LM dictionary for modal word analysis

#### 1.4 Evasiveness Analyzer (`evasiveness.py`)

**Status:** ✅ Implemented

**Purpose:** Measure overall language evasiveness

**Key Classes:**

```python
@dataclass
class EvasivenessScores:
    overall_evasiveness: float  # 0-100 composite score
    
    # Component metrics
    qualifier_density: float
    hedging_language_pct: float
    passive_voice_pct: float
    vague_pronoun_pct: float
    distancing_score: float
    
    # Comparisons
    vs_baseline: str  # "above", "at", "below"
    evasiveness_level: str  # "Low", "Moderate", "High", "Very High"
    
    # Examples
    most_evasive_sentences: List[Tuple[str, float]]

class EvasivenessAnalyzer:
    def __init__(self):
        self.linguistic_markers = LinguisticDeceptionMarkers()
        self.baseline = settings.SP500_EVASIVENESS_BASELINE  # 11.0
    
    def analyze(self, text: str) -> EvasivenessScores
```

**Composite Formula:**
```python
overall_evasiveness = (
    qualifier_density * 0.25 +
    hedging_pct * 0.25 +
    passive_voice_pct * 0.20 +
    vague_pronoun_pct * 0.15 +
    distancing_score * 0.15
)
```

**Benchmark Comparison:**
Compare to `settings.SP500_EVASIVENESS_BASELINE = 11.0`

**Evasiveness Levels:**
- **Low:** < 8.8 (80% of baseline)
- **Moderate:** 8.8-13.2 (80%-120% of baseline)
- **High:** 13.2-16.5 (120%-150% of baseline)
- **Very High:** > 16.5 (150%+ of baseline)

#### 1.5 Question Evasion Detector (`question_evasion.py`)

**Status:** ✅ Implemented

**Purpose:** Analyze Q&A exchanges for question dodging

**Key Classes:**

```python
@dataclass
class QuestionResponse:
    question: str
    response: str
    analyst: str
    responder: str
    
    # Analysis
    response_relevance: float  # 0-1
    is_evasive: bool
    evasion_type: str  # "direct", "deflection", "vague", "non-answer", "topic_change"
    key_question_topics: List[str]
    response_topics: List[str]
    topic_overlap: float  # 0-1

class QuestionEvasionDetector:
    def analyze_qa_section(self, qa_text: str) -> List[QuestionResponse]
    def calculate_overall_evasion_rate(self, analyzed_pairs: List[QuestionResponse]) -> float
    def get_most_evasive_questions(self, analyzed_pairs: List[QuestionResponse], top_n: int = 5) -> List[QuestionResponse]
```

**Evasion Detection Methods:**

1. **Topic Overlap Analysis:**
   - Extract topics from question (NER + noun chunks using spaCy)
   - Extract topics from response
   - Calculate Jaccard similarity
   - Low overlap (< 0.3) = potential evasion

2. **Deflection Phrase Detection:**
   ```python
   deflection_phrases = [
       "let me talk about",
       "what i would say is",
       "more broadly",
       "stepping back",
       "in general",
       "i think the important thing",
       "what's really important",
       "the real story here"
   ]
   ```

3. **Vagueness Density:**
   - Count qualifiers and hedging words
   - If > 5% of response words are vague = evasive

4. **Length Mismatch:**
   - Complex question (> 30 words) + short response (< 20 words) = suspicious
   - Response < 0.5 × question length = potential evasion

5. **LLM Relevance Scoring (optional):**
   - Use Ollama to rate response relevance (0-1)
   - Prompt: "Rate how well this response addresses the question"

**Evasion Types:**
- **direct:** Response directly answers question (relevance > 0.7, topic overlap > 0.5)
- **deflection:** Uses deflection phrases, changes topic
- **vague:** High vagueness density, lacks specifics
- **non-answer:** Very low relevance (< 0.3)
- **topic_change:** Low topic overlap (< 0.3)

#### 1.6 Integration Checklist

- [ ] Move `src/deception/` to `src/analysis/deception/`
- [ ] Update all imports
- [ ] Add deception analyzers to `aggregator.py __init__`
- [ ] Add `DeceptionRiskScore` and `EvasivenessScores` to `ComprehensiveAnalysisResult`
- [ ] Call deception analysis in `analyze_transcript()`
- [ ] Update `_generate_insights()` to include deception insights
- [ ] Update `print_summary()` to display deception results
- [ ] Update `save_results()` to include deception data in JSON
- [ ] Add CLI flag `--with-deception` to `analyze` command
- [ ] Write unit tests for integration
- [ ] Update documentation

---

### 2. Comparative Analysis Module (Phase 2E)

**Location:** `src/analysis/comparative/`  
**Priority:** MEDIUM  
**Status:** Not Started

#### 2.1 Historical Trend Analyzer (`historical.py`)

**Purpose:** Track metrics across multiple quarters for trend analysis

**Key Classes:**

```python
@dataclass
class HistoricalDataPoint:
    company: str
    ticker: str
    quarter: str
    year: int
    date: str
    
    # All metrics from analysis
    hybrid_sentiment_score: float
    complexity_composite_score: float
    numeric_transparency_score: float
    deception_risk_score: float
    evasiveness_score: float
    # ... additional metrics

@dataclass
class TrendAnalysis:
    metric_name: str
    values: List[float]
    quarters: List[str]
    
    # Trend characteristics
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0-1 (R-squared from regression)
    volatility: float  # Standard deviation
    
    # Regression
    regression_slope: float
    regression_intercept: float
    regression_r_squared: float
    
    # Advanced features
    seasonality_detected: bool
    forecast_next_quarter: Optional[float]
    anomalies: List[Tuple[str, float]]  # (quarter, value) for outliers

class HistoricalTrendAnalyzer:
    def __init__(self, database_path: Path):
        from src.database.repository import DatabaseRepository
        self.db = DatabaseRepository(database_path)
    
    def load_company_history(
        self, 
        company: str, 
        quarters: int = 4
    ) -> List[HistoricalDataPoint]:
        """Load N most recent quarters for a company"""
    
    def analyze_metric_trend(
        self,
        company: str,
        metric_name: str,
        quarters: int = 4
    ) -> TrendAnalysis:
        """Analyze single metric trend"""
    
    def generate_trend_report(
        self,
        company: str,
        quarters: int = 4
    ) -> Dict[str, TrendAnalysis]:
        """Analyze all key metrics"""
    
    def detect_anomalies(
        self,
        company: str,
        current_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Flag unusual deviations from historical norms"""
```

**Trend Detection Methods:**

1. **Linear Regression:**
   ```python
   import numpy as np
   from scipy import stats
   
   slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
   r_squared = r_value ** 2
   
   if r_squared > 0.7 and slope > 0:
       trend_direction = "improving"
   elif r_squared > 0.7 and slope < 0:
       trend_direction = "declining"
   else:
       trend_direction = "stable"
   ```

2. **Volatility Measurement:**
   ```python
   volatility = np.std(values)
   ```

3. **Seasonality Detection:**
   ```python
   # Check if Q4 values consistently higher than Q1
   q4_values = [v for q, v in zip(quarters, values) if "Q4" in q]
   q1_values = [v for q, v in zip(quarters, values) if "Q1" in q]
   
   if len(q4_values) >= 2 and len(q1_values) >= 2:
       seasonality_detected = np.mean(q4_values) > np.mean(q1_values) * 1.1
   ```

4. **Anomaly Detection:**
   ```python
   mean = np.mean(values)
   std = np.std(values)
   
   anomalies = []
   for quarter, value in zip(quarters, values):
       z_score = abs(value - mean) / std
       if z_score > 2:  # More than 2 standard deviations
           anomalies.append((quarter, value))
   ```

5. **Simple Forecasting:**
   ```python
   # Linear extrapolation
   next_x = len(values) + 1
   forecast = slope * next_x + intercept
   ```

**Key Metrics to Track:**
- `hybrid_sentiment_score`
- `complexity_composite_score`
- `numeric_transparency_score`
- `deception_risk_score`
- `evasiveness_score`
- `forward_to_backward_ratio`
- `contextualization_quality_score`

**CLI Integration:**
```bash
earnings-analyzer historical AAPL --quarters 8
```

**Output Example:**
```
HISTORICAL TREND ANALYSIS: AAPL

Hybrid Sentiment Score:
  Trend: improving (strength: 0.85)
  Q1 2023: 0.45
  Q2 2023: 0.52
  Q3 2023: 0.58
  Q4 2023: 0.61
  Forecast Q1 2024: 0.65
  
Deception Risk Score:
  Trend: declining (strength: 0.72)
  Volatility: 5.2
  Current vs Historical Mean: -12% (positive)
```

#### 2.2 Peer Comparison Engine (`peer_comparison.py`)

**Purpose:** Compare company metrics against industry peers

**Key Classes:**

```python
@dataclass
class PeerComparisonResult:
    company: str
    sector: str
    metric_name: str
    
    # Values
    company_value: float
    peer_values: List[Tuple[str, float]]  # (peer_name, value)
    sector_mean: float
    sector_median: float
    sector_std_dev: float
    
    # Rankings
    percentile_rank: float  # 0-100
    rank_in_sector: int  # 1 = best
    total_in_sector: int
    
    # Classification
    vs_peers: str  # "above", "at", "below"
    is_outlier: bool  # > 2 std devs from mean

class PeerComparisonEngine:
    def __init__(self, database_path: Path):
        from src.database.repository import DatabaseRepository
        self.db = DatabaseRepository(database_path)
    
    def compare_to_peers(
        self,
        company: str,
        peers: List[str],
        metrics: List[str] = None,
        quarter: str = "Q4",
        year: int = 2024
    ) -> Dict[str, PeerComparisonResult]:
        """Compare to specific peer companies"""
    
    def compare_to_sector(
        self,
        company: str,
        sector: str,
        quarter: str,
        year: int
    ) -> Dict[str, PeerComparisonResult]:
        """Compare to all companies in sector"""
    
    def calculate_percentile_ranks(
        self,
        company: str,
        sector: str
    ) -> Dict[str, float]:
        """Calculate percentile rank for all metrics"""
    
    def identify_competitive_advantages(
        self,
        company: str,
        sector: str
    ) -> List[str]:
        """Identify metrics where company significantly outperforms sector"""
    
    def identify_competitive_weaknesses(
        self,
        company: str,
        sector: str
    ) -> List[str]:
        """Identify metrics where company underperforms sector"""
```

**Sector Classification:**
Use GICS (Global Industry Classification Standard):
- **Information Technology**
- **Financials**
- **Health Care**
- **Consumer Discretionary**
- **Communication Services**
- **Industrials**
- **Consumer Staples**
- **Energy**
- **Utilities**
- **Real Estate**
- **Materials**

**Percentile Calculation:**
```python
def calculate_percentile(value: float, all_values: List[float]) -> float:
    """Calculate what percentile a value is at"""
    below_count = sum(1 for v in all_values if v < value)
    return (below_count / len(all_values)) * 100
```

**CLI Integration:**
```bash
# Compare to specific peers
earnings-analyzer compare AAPL --peers MSFT,GOOGL,META

# Compare to sector
earnings-analyzer compare AAPL --sector "Information Technology"
```

**Output Example:**
```
PEER COMPARISON: AAPL vs Information Technology Sector

Hybrid Sentiment Score:
  AAPL: 0.65
  Sector Mean: 0.52
  Percentile: 78th
  Rank: 15/67
  Status: Above average ✓

Deception Risk Score:
  AAPL: 32
  Sector Mean: 38
  Percentile: 35th
  Rank: 23/67
  Status: Below average ✓ (lower is better)

Competitive Advantages:
  • Sentiment: 78th percentile
  • Transparency: 82nd percentile

Competitive Weaknesses:
  • Complexity: 65th percentile (high complexity)
```

#### 2.3 Database Integration

Both historical and peer comparison modules require database access.

**Required Database Methods:**

```python
class DatabaseRepository:
    def load_historical_analyses(
        self,
        company_name: str,
        quarters: int = 4
    ) -> List[AnalysisResult]:
        """Load N most recent analyses"""
    
    def get_sector_companies(self, sector: str) -> List[Company]:
        """Get all companies in a sector"""
    
    def calculate_sector_benchmark(
        self,
        sector: str,
        metric_name: str,
        quarter: str,
        year: int
    ) -> Dict[str, float]:
        """Calculate mean/median/std for a metric"""
```

---

### 3. Advanced Reporting Module (Phase 2C)

**Location:** `src/reporting/`  
**Priority:** HIGH  
**Status:** Not Started

#### 3.1 Overview

The reporting module generates professional-quality reports in multiple formats:
- **PDF:** Printable executive summaries and detailed reports
- **HTML:** Interactive dashboards with charts
- **Excel:** Structured workbooks with formulas

#### 3.2 PDF Report Generator (`pdf_generator.py`)

**Purpose:** Generate professional PDF reports

**Technology:** WeasyPrint (HTML → PDF with CSS)

**Key Classes:**

```python
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import plotly.graph_objects as go

class PDFReportGenerator:
    def __init__(self, template_dir: Path = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / "src" / "web" / "templates"
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_executive_summary(
        self,
        results: ComprehensiveAnalysisResult,
        output_path: Path,
        include_charts: bool = True
    ) -> Path:
        """Generate 2-3 page executive summary"""
    
    def generate_detailed_report(
        self,
        results: ComprehensiveAnalysisResult,
        historical_data: List[HistoricalDataPoint] = None,
        peer_comparison: Dict[str, PeerComparisonResult] = None,
        output_path: Path
    ) -> Path:
        """Generate 8-12 page detailed report"""
    
    def _generate_charts(self, results: ComprehensiveAnalysisResult) -> Dict[str, Path]:
        """Generate chart images for embedding in PDF"""
```

**Report Sections:**

**Executive Summary (2-3 pages):**
1. **Cover Page**
   - Company name, logo placeholder
   - Quarter and year
   - Analysis date
   - Overall risk indicator (traffic light 🟢🟡🔴)

2. **Risk Assessment Dashboard**
   - Overall deception risk score (large display)
   - Risk level badge
   - Key metrics table:
     * Sentiment: X.XX (Positive/Negative/Neutral)
     * Complexity: XX/100 (Low/Moderate/High)
     * Transparency: X.XX% (vs S&P 500)
     * Deception Risk: XX/100 (Low/Moderate/High/Critical)
     * Evasiveness: X.XX (vs baseline)

3. **Key Findings**
   - 3-5 bullet points (most important insights)
   
4. **Red Flags** (if any)
   - Critical issues requiring attention
   
5. **Strengths**
   - Positive aspects of communication

**Detailed Report (8-12 pages):**
1. Executive Summary (from above)

2. **Sentiment Analysis (2 pages)**
   - Hybrid sentiment breakdown
   - Lexicon vs LLM comparison
   - Section comparison (prepared remarks vs Q&A)
   - Speaker comparison (CEO vs CFO)
   - Historical trend chart (if available)

3. **Language Complexity (2 pages)**
   - Composite score interpretation
   - All 5 readability metrics
   - Complexity level explanation
   - Most complex sentences (examples)
   - Comparison to industry average

4. **Numerical Transparency (2 pages)**
   - Transparency score vs benchmark
   - Specificity index
   - Forward vs backward-looking analysis
   - Contextualization quality
   - Examples of well/poorly contextualized numbers

5. **Deception Risk Assessment (2 pages)**
   - Overall risk score
   - Component breakdown (spider chart):
     * Linguistic: XX/100
     * Behavioral: XX/100
     * Numerical: XX/100
     * Evasion: XX/100
   - All 13 individual indicators
   - Triggered flags
   - Most evasive Q&A exchanges (examples)
   - Complexity hotspots

6. **Historical Trends (1 page, optional)**
   - Multi-quarter trend charts
   - Key metric evolution
   - Anomalies flagged

7. **Peer Comparison (1 page, optional)**
   - Percentile rankings
   - Sector benchmarking table
   - Competitive positioning

8. **Appendix**
   - Methodology overview
   - Glossary of metrics
   - Data sources

**Chart Generation:**

```python
def _generate_sentiment_trend_chart(self, historical_data: List[HistoricalDataPoint]) -> Path:
    """Generate sentiment trend line chart"""
    import plotly.graph_objects as go
    
    quarters = [d.quarter + " " + str(d.year) for d in historical_data]
    sentiment_scores = [d.hybrid_sentiment_score for d in historical_data]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=quarters,
        y=sentiment_scores,
        mode='lines+markers',
        name='Hybrid Sentiment',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Sentiment Trend',
        xaxis_title='Quarter',
        yaxis_title='Sentiment Score',
        template='plotly_white',
        width=800,
        height=400
    )
    
    # Save as PNG
    chart_path = Path("/tmp/sentiment_trend.png")
    fig.write_image(chart_path, format='png')
    return chart_path

def _generate_risk_spider_chart(self, deception_risk: DeceptionRiskScore) -> Path:
    """Generate deception risk component spider chart"""
    fig = go.Figure(data=go.Scatterpolar(
        r=[
            deception_risk.risk_components['linguistic'],
            deception_risk.risk_components['behavioral'],
            deception_risk.risk_components['numerical'],
            deception_risk.risk_components['evasion']
        ],
        theta=['Linguistic', 'Behavioral', 'Numerical', 'Evasion'],
        fill='toself',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title='Deception Risk Components',
        template='plotly_white',
        width=600,
        height=600
    )
    
    chart_path = Path("/tmp/risk_spider.png")
    fig.write_image(chart_path, format='png')
    return chart_path
```

**HTML Template (Jinja2):**

```html
<!-- templates/detailed_report.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ company }} - {{ quarter }} {{ year }} Analysis</title>
    <style>
        @page {
            size: Letter;
            margin: 0.75in;
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #333;
            line-height: 1.6;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        
        .risk-critical { background-color: #e74c3c; color: white; }
        .risk-high { background-color: #e67e22; color: white; }
        .risk-moderate { background-color: #f39c12; color: white; }
        .risk-low { background-color: #27ae60; color: white; }
        
        .risk-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 18px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background-color: #3498db;
            color: white;
        }
        
        .page-break {
            page-break-after: always;
        }
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="page-break">
        <h1 style="text-align: center; margin-top: 200px;">
            Earnings Call Analysis Report
        </h1>
        <h2 style="text-align: center;">{{ company }}</h2>
        <p style="text-align: center; font-size: 24px;">
            {{ quarter }} {{ year }}
        </p>
        <p style="text-align: center; color: #7f8c8d;">
            Analysis Date: {{ analysis_date }}
        </p>
    </div>
    
    <!-- Executive Summary -->
    <div class="page-break">
        <h1>Executive Summary</h1>
        
        <h2>Overall Risk Assessment</h2>
        <p>
            <span class="risk-badge risk-{{ risk_level|lower }}">
                {{ risk_level }}: {{ risk_score }}/100
            </span>
        </p>
        
        <h3>Key Metrics</h3>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Assessment</th>
            </tr>
            <tr>
                <td>Sentiment</td>
                <td>{{ sentiment_score }}</td>
                <td>{{ sentiment_label }}</td>
            </tr>
            <tr>
                <td>Complexity</td>
                <td>{{ complexity_score }}/100</td>
                <td>{{ complexity_level }}</td>
            </tr>
            <tr>
                <td>Numerical Transparency</td>
                <td>{{ transparency_score }}%</td>
                <td>{{ transparency_vs_benchmark }}</td>
            </tr>
            <tr>
                <td>Deception Risk</td>
                <td>{{ risk_score }}/100</td>
                <td>{{ risk_level }}</td>
            </tr>
            <tr>
                <td>Evasiveness</td>
                <td>{{ evasiveness_score }}</td>
                <td>{{ evasiveness_level }}</td>
            </tr>
        </table>
        
        <h3>Key Findings</h3>
        <ul>
            {% for finding in key_findings %}
            <li>{{ finding }}</li>
            {% endfor %}
        </ul>
        
        {% if red_flags %}
        <h3>🚩 Red Flags</h3>
        <ul>
            {% for flag in red_flags %}
            <li style="color: #e74c3c;"><strong>{{ flag }}</strong></li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {% if strengths %}
        <h3>✓ Strengths</h3>
        <ul>
            {% for strength in strengths %}
            <li style="color: #27ae60;">{{ strength }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    
    <!-- Sentiment Analysis -->
    <div class="page-break">
        <h1>Sentiment Analysis</h1>
        
        <p>
            The hybrid sentiment analysis combines dictionary-based (Loughran-McDonald) 
            and LLM-based contextual sentiment scoring, weighted 30% lexicon and 70% LLM.
        </p>
        
        <h2>Overall Sentiment</h2>
        <ul>
            <li><strong>Hybrid Score:</strong> {{ sentiment_score }} ({{ sentiment_label }})</li>
            <li><strong>Lexicon Net Positivity:</strong> {{ lexicon_net_positivity }}%</li>
            <li><strong>LLM Sentiment:</strong> {{ llm_sentiment_score }}</li>
        </ul>
        
        {% if sentiment_trend_chart %}
        <h2>Historical Trend</h2>
        <img src="{{ sentiment_trend_chart }}" style="width: 100%;" />
        {% endif %}
        
        <h2>Section Comparison</h2>
        <table>
            <tr>
                <th>Section</th>
                <th>Sentiment Score</th>
                <th>Label</th>
            </tr>
            <tr>
                <td>Prepared Remarks</td>
                <td>{{ prepared_remarks_sentiment }}</td>
                <td>{{ prepared_remarks_label }}</td>
            </tr>
            <tr>
                <td>Q&A</td>
                <td>{{ qa_sentiment }}</td>
                <td>{{ qa_label }}</td>
            </tr>
        </table>
    </div>
    
    <!-- Additional sections... -->
    
    <!-- Deception Risk Assessment -->
    <div class="page-break">
        <h1>Deception Risk Assessment</h1>
        
        <p>
            The deception risk score is calculated from 13 individual indicators across 
            4 categories: linguistic, behavioral, numerical, and evasion patterns.
        </p>
        
        <h2>Risk Components</h2>
        {% if risk_spider_chart %}
        <img src="{{ risk_spider_chart }}" style="width: 80%; display: block; margin: 20px auto;" />
        {% endif %}
        
        <table>
            <tr>
                <th>Component</th>
                <th>Score</th>
                <th>Weight</th>
            </tr>
            <tr>
                <td>Linguistic</td>
                <td>{{ linguistic_component }}/100</td>
                <td>25%</td>
            </tr>
            <tr>
                <td>Behavioral</td>
                <td>{{ behavioral_component }}/100</td>
                <td>25%</td>
            </tr>
            <tr>
                <td>Numerical</td>
                <td>{{ numerical_component }}/100</td>
                <td>30%</td>
            </tr>
            <tr>
                <td>Evasion</td>
                <td>{{ evasion_component }}/100</td>
                <td>20%</td>
            </tr>
        </table>
        
        <h2>Individual Indicators</h2>
        <table>
            <tr>
                <th>Indicator</th>
                <th>Score</th>
                <th>Category</th>
            </tr>
            {% for indicator in indicators %}
            <tr>
                <td>{{ indicator.name }}</td>
                <td>{{ indicator.score }}/100</td>
                <td>{{ indicator.category }}</td>
            </tr>
            {% endfor %}
        </table>
        
        {% if triggered_flags %}
        <h2>Triggered Flags</h2>
        <ul>
            {% for flag in triggered_flags %}
            <li style="color: #e74c3c;">{{ flag }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
</body>
</html>
```

**CLI Integration:**
```bash
earnings-analyzer report transcript.txt -f pdf -o my_report
```

**API Integration:**
```python
@router.get("/results/{job_id}/pdf")
async def get_pdf_report(job_id: str):
    job = job_queue.get_job(job_id)
    if not job or job.status != "completed":
        raise HTTPException(400, "Job not completed")
    
    generator = PDFReportGenerator()
    pdf_path = generator.generate_detailed_report(
        job.results,
        output_path=Path(f"/tmp/{job_id}.pdf")
    )
    
    return FileResponse(pdf_path, media_type="application/pdf")
```

#### 3.3 Interactive HTML Dashboard (`html_dashboard.py`)

**Purpose:** Generate interactive HTML dashboards with Plotly charts

**Key Features:**
- Interactive charts (hover, zoom, pan)
- Responsive design
- Collapsible sections
- Export options

**Key Classes:**

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from jinja2 import Environment, FileSystemLoader

class HTMLDashboardGenerator:
    def __init__(self, template_dir: Path = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / "src" / "web" / "templates"
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_dashboard(
        self,
        results: ComprehensiveAnalysisResult,
        historical_data: List[HistoricalDataPoint] = None,
        output_path: Path = None
    ) -> str:
        """Generate complete interactive dashboard"""
    
    def generate_comparison_dashboard(
        self,
        companies: List[Tuple[str, ComprehensiveAnalysisResult]],
        output_path: Path
    ) -> str:
        """Generate multi-company comparison dashboard"""
```

**Dashboard Template:**

```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ company }} - {{ quarter }} {{ year }} Dashboard</title>
    
    <!-- Plotly -->
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    
    <!-- Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
        }
        
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .risk-critical { background-color: #dc3545; }
        .risk-high { background-color: #fd7e14; }
        .risk-moderate { background-color: #ffc107; }
        .risk-low { background-color: #28a745; }
        
        .risk-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }
        
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- Header -->
        <div class="dashboard-header">
            <h1>{{ company }} Earnings Call Analysis</h1>
            <h3>{{ quarter }} {{ year }}</h3>
            <p>Analysis Date: {{ analysis_date }}</p>
        </div>
        
        <!-- Risk Assessment -->
        <div class="row">
            <div class="col-12">
                <div class="metric-card text-center">
                    <h2>Overall Deception Risk</h2>
                    <div class="risk-badge risk-{{ risk_level|lower }}">
                        {{ risk_level }}: {{ risk_score }}/100
                    </div>
                    <p class="mt-3">Confidence: {{ confidence }}%</p>
                </div>
            </div>
        </div>
        
        <!-- Key Metrics Cards -->
        <div class="row">
            <div class="col-md-3">
                <div class="metric-card">
                    <h5>Sentiment</h5>
                    <h2>{{ sentiment_score }}</h2>
                    <p>{{ sentiment_label }}</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <h5>Complexity</h5>
                    <h2>{{ complexity_score }}</h2>
                    <p>{{ complexity_level }}</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <h5>Transparency</h5>
                    <h2>{{ transparency_score }}%</h2>
                    <p>{{ transparency_vs_benchmark }}</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <h5>Evasiveness</h5>
                    <h2>{{ evasiveness_score }}</h2>
                    <p>{{ evasiveness_level }}</p>
                </div>
            </div>
        </div>
        
        <!-- Tabs -->
        <ul class="nav nav-tabs" id="analysisTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="sentiment-tab" data-bs-toggle="tab" 
                        data-bs-target="#sentiment" type="button">
                    Sentiment
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="complexity-tab" data-bs-toggle="tab" 
                        data-bs-target="#complexity" type="button">
                    Complexity
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="numerical-tab" data-bs-toggle="tab" 
                        data-bs-target="#numerical" type="button">
                    Numerical
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="deception-tab" data-bs-toggle="tab" 
                        data-bs-target="#deception" type="button">
                    Deception
                </button>
            </li>
        </ul>
        
        <!-- Tab Content -->
        <div class="tab-content" id="analysisTabContent">
            <!-- Sentiment Tab -->
            <div class="tab-pane fade show active" id="sentiment" role="tabpanel">
                <div class="chart-container">
                    <div id="sentiment-gauge"></div>
                </div>
                <div class="chart-container">
                    <div id="sentiment-trend"></div>
                </div>
                <div class="chart-container">
                    <div id="section-comparison"></div>
                </div>
            </div>
            
            <!-- Complexity Tab -->
            <div class="tab-pane fade" id="complexity" role="tabpanel">
                <div class="chart-container">
                    <div id="complexity-breakdown"></div>
                </div>
            </div>
            
            <!-- Numerical Tab -->
            <div class="tab-pane fade" id="numerical" role="tabpanel">
                <div class="chart-container">
                    <div id="transparency-vs-benchmark"></div>
                </div>
                <div class="chart-container">
                    <div id="forward-backward"></div>
                </div>
            </div>
            
            <!-- Deception Tab -->
            <div class="tab-pane fade" id="deception" role="tabpanel">
                <div class="chart-container">
                    <div id="risk-spider"></div>
                </div>
                <div class="chart-container">
                    <h4>Triggered Flags</h4>
                    <ul>
                        {% for flag in triggered_flags %}
                        <li>{{ flag }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Sentiment Gauge
        var sentimentGauge = {
            type: "indicator",
            mode: "gauge+number",
            value: {{ sentiment_score }},
            gauge: {
                axis: { range: [-1, 1] },
                bar: { color: "{{ '#27ae60' if sentiment_score > 0 else '#e74c3c' }}" },
                steps: [
                    { range: [-1, -0.2], color: "lightcoral" },
                    { range: [-0.2, 0.2], color: "lightgray" },
                    { range: [0.2, 1], color: "lightgreen" }
                ],
                threshold: {
                    line: { color: "red", width: 4 },
                    thickness: 0.75,
                    value: 0
                }
            }
        };
        
        var sentimentGaugeLayout = {
            title: { text: "Hybrid Sentiment Score" },
            height: 400
        };
        
        Plotly.newPlot('sentiment-gauge', [sentimentGauge], sentimentGaugeLayout);
        
        // Sentiment Trend (if historical data)
        {% if sentiment_trend_data %}
        var sentimentTrend = {
            x: {{ sentiment_trend_data.quarters | tojson }},
            y: {{ sentiment_trend_data.scores | tojson }},
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Hybrid Sentiment',
            line: { color: '#1f77b4', width: 3 },
            marker: { size: 10 }
        };
        
        var sentimentTrendLayout = {
            title: 'Sentiment Trend Over Time',
            xaxis: { title: 'Quarter' },
            yaxis: { title: 'Sentiment Score' },
            height: 400
        };
        
        Plotly.newPlot('sentiment-trend', [sentimentTrend], sentimentTrendLayout);
        {% endif %}
        
        // Section Comparison
        var sectionComparison = {
            x: ['Prepared Remarks', 'Q&A'],
            y: [{{ prepared_remarks_sentiment }}, {{ qa_sentiment }}],
            type: 'bar',
            marker: {
                color: ['#3498db', '#e74c3c']
            }
        };
        
        var sectionLayout = {
            title: 'Sentiment by Section',
            yaxis: { title: 'Sentiment Score' },
            height: 400
        };
        
        Plotly.newPlot('section-comparison', [sectionComparison], sectionLayout);
        
        // Deception Risk Spider
        var riskSpider = {
            type: 'scatterpolar',
            r: [
                {{ linguistic_component }},
                {{ behavioral_component }},
                {{ numerical_component }},
                {{ evasion_component }}
            ],
            theta: ['Linguistic', 'Behavioral', 'Numerical', 'Evasion'],
            fill: 'toself',
            line: { color: '#e74c3c' }
        };
        
        var riskSpiderLayout = {
            polar: {
                radialaxis: {
                    visible: true,
                    range: [0, 100]
                }
            },
            title: 'Deception Risk Components',
            height: 600
        };
        
        Plotly.newPlot('risk-spider', [riskSpider], riskSpiderLayout);
        
        // Additional charts...
    </script>
</body>
</html>
```

**CLI Integration:**
```bash
earnings-analyzer report transcript.txt -f html -o dashboard.html
```

**API Integration:**
```python
@router.get("/results/{job_id}/dashboard")
async def get_html_dashboard(job_id: str):
    job = job_queue.get_job(job_id)
    if not job or job.status != "completed":
        raise HTTPException(400, "Job not completed")
    
    generator = HTMLDashboardGenerator()
    html = generator.generate_dashboard(job.results)
    
    return HTMLResponse(content=html)
```

#### 3.4 Excel Export (`excel_exporter.py`)

**Purpose:** Export analysis to structured Excel workbooks

**Key Classes:**

```python
from openpyxl import Workbook
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import ColorScaleRule

class ExcelReportExporter:
    def export_analysis(
        self,
        results: ComprehensiveAnalysisResult,
        output_path: Path
    ) -> Path:
        """Export single analysis to Excel"""
    
    def export_historical_trends(
        self,
        company: str,
        historical_data: List[HistoricalDataPoint],
        output_path: Path
    ) -> Path:
        """Export historical trends to Excel with charts"""
    
    def export_peer_comparison(
        self,
        comparison_results: Dict[str, PeerComparisonResult],
        output_path: Path
    ) -> Path:
        """Export peer comparison to Excel"""
```

**Workbook Structure:**

**Sheet 1: Summary**
- Company metadata
- Overall scores
- Key findings
- Red flags
- Strengths

**Sheet 2: Sentiment**
- Hybrid sentiment breakdown
- Lexicon scores (all 7 categories)
- LLM sentiment
- Section comparison
- Speaker comparison

**Sheet 3: Complexity**
- 5 readability metrics
- Composite score
- Statistics

**Sheet 4: Numerical**
- Transparency score
- Specificity index
- Forward/backward density
- Contextualization quality

**Sheet 5: Deception**
- Overall risk score
- 13 indicators
- Risk components
- Triggered flags

**Sheet 6: Historical** (optional)
- Multi-quarter data
- Trend calculations
- Conditional formatting

**Sheet 7: Raw JSON**
- Full results as reference

**Implementation:**

```python
def export_analysis(self, results: ComprehensiveAnalysisResult, output_path: Path) -> Path:
    wb = Workbook()
    
    # Sheet 1: Summary
    ws_summary = wb.active
    ws_summary.title = "Summary"
    
    # Header
    ws_summary['A1'] = f"{results.company_name} - {results.quarter} {results.year}"
    ws_summary['A1'].font = Font(size=16, bold=True)
    
    # Metadata
    ws_summary['A3'] = 'Analysis Date:'
    ws_summary['B3'] = results.timestamp
    
    # Overall Scores
    ws_summary['A5'] = 'Overall Metrics'
    ws_summary['A5'].font = Font(size=14, bold=True)
    
    headers = ['Metric', 'Value', 'Assessment']
    for col, header in enumerate(headers, start=1):
        cell = ws_summary.cell(row=6, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.font = Font(color="FFFFFF", bold=True)
    
    # Add data
    row = 7
    ws_summary.cell(row=row, column=1, value='Sentiment')
    ws_summary.cell(row=row, column=2, value=results.overall_sentiment.hybrid_sentiment_score)
    ws_summary.cell(row=row, column=3, value=results.overall_sentiment.hybrid_label)
    
    row += 1
    ws_summary.cell(row=row, column=1, value='Complexity')
    ws_summary.cell(row=row, column=2, value=results.overall_complexity.composite_score)
    ws_summary.cell(row=row, column=3, value=results.overall_complexity.complexity_level)
    
    # ... additional rows
    
    # Conditional formatting
    ws_summary.conditional_formatting.add(
        'B7:B11',
        ColorScaleRule(
            start_type='num', start_value=0, start_color='FF0000',
            mid_type='num', mid_value=50, mid_color='FFFF00',
            end_type='num', end_value=100, end_color='00FF00'
        )
    )
    
    # Sheet 2: Sentiment
    ws_sentiment = wb.create_sheet("Sentiment")
    # ... populate sentiment data
    
    # Save
    wb.save(output_path)
    return output_path
```

**CLI Integration:**
```bash
earnings-analyzer report transcript.txt -f xlsx -o report.xlsx
```

---

### 4. Database & Persistence Module (Phase 2B)

**Location:** `src/database/`  
**Priority:** HIGH  
**Status:** Not Started

#### 4.1 Database Models (`models.py`)

**Purpose:** SQLAlchemy ORM models

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    ticker = Column(String(10), unique=True, index=True)
    sector = Column(String(100))
    industry = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    analyses = relationship("AnalysisResult", back_populates="company", cascade="all, delete-orphan")

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    quarter = Column(String(2), nullable=False)  # Q1, Q2, Q3, Q4
    year = Column(Integer, nullable=False)
    analysis_date = Column(DateTime, nullable=False, default=datetime.now)
    
    # Sentiment metrics
    hybrid_sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    lexicon_net_positivity = Column(Float)
    llm_sentiment_score = Column(Float)
    
    # Complexity metrics
    complexity_composite_score = Column(Float)
    complexity_level = Column(String(20))
    flesch_reading_ease = Column(Float)
    flesch_kincaid_grade = Column(Float)
    gunning_fog_index = Column(Float)
    smog_index = Column(Float)
    coleman_liau_index = Column(Float)
    
    # Numerical metrics
    numeric_transparency_score = Column(Float)
    numerical_specificity_index = Column(Float)
    forward_looking_density = Column(Float)
    backward_looking_density = Column(Float)
    forward_to_backward_ratio = Column(Float)
    contextualization_quality_score = Column(Float)
    vs_sp500_benchmark = Column(String(10))  # above, at, below
    
    # Deception metrics (Phase 2)
    deception_risk_score = Column(Float)
    deception_risk_level = Column(String(20))
    deception_confidence = Column(Float)
    
    # Evasiveness metrics (Phase 2)
    evasiveness_score = Column(Float)
    evasiveness_level = Column(String(20))
    evasiveness_vs_baseline = Column(String(10))
    
    # Counts
    word_count = Column(Integer)
    sentence_count = Column(Integer)
    
    # Full results as JSON
    full_results_json = Column(JSON)
    
    # Key findings (for quick access)
    key_findings = Column(Text)
    red_flags = Column(Text)
    strengths = Column(Text)
    
    # Relationships
    company = relationship("Company", back_populates="analyses")
    
    # Indexes
    __table_args__ = (
        Index('idx_company_quarter', 'company_id', 'year', 'quarter'),
    )

class Benchmark(Base):
    __tablename__ = 'benchmarks'
    
    id = Column(Integer, primary_key=True)
    sector = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    quarter = Column(String(2))
    year = Column(Integer)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_sector_metric', 'sector', 'metric_name'),
    )
```

#### 4.2 Database Repository (`repository.py`)

**Purpose:** Data access layer

```python
from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import statistics

from src.database.models import Base, Company, AnalysisResult, Benchmark
from src.analysis.aggregator import ComprehensiveAnalysisResult
from dataclasses import asdict

class DatabaseRepository:
    def __init__(self, database_url: str):
        """
        Initialize database repository
        
        Args:
            database_url: SQLAlchemy database URL
                e.g., "sqlite:///./data/earnings_analyzer.db"
                      "postgresql://user:pass@localhost/earnings"
        """
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def _get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # ===== Company Operations =====
    
    def get_or_create_company(
        self,
        name: str,
        ticker: Optional[str] = None,
        sector: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Company:
        """Get existing company or create new one"""
        session = self._get_session()
        try:
            company = session.query(Company).filter_by(name=name).first()
            if not company:
                company = Company(
                    name=name,
                    ticker=ticker,
                    sector=sector,
                    industry=industry
                )
                session.add(company)
                session.commit()
                session.refresh(company)
            return company
        finally:
            session.close()
    
    def update_company(
        self,
        company_id: int,
        **kwargs
    ) -> Company:
        """Update company information"""
        session = self._get_session()
        try:
            company = session.query(Company).get(company_id)
            if not company:
                raise ValueError(f"Company ID {company_id} not found")
            
            for key, value in kwargs.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            session.commit()
            session.refresh(company)
            return company
        finally:
            session.close()
    
    # ===== Analysis Operations =====
    
    def save_analysis(self, results: ComprehensiveAnalysisResult) -> int:
        """
        Save analysis results to database
        
        Returns:
            analysis_id
        """
        session = self._get_session()
        try:
            # Get or create company
            company = self.get_or_create_company(
                name=results.company_name,
                ticker=getattr(results, 'ticker', None)
            )
            
            # Create analysis record
            analysis = AnalysisResult(
                company_id=company.id,
                quarter=results.quarter,
                year=results.year,
                analysis_date=datetime.fromisoformat(results.timestamp),
                
                # Sentiment
                hybrid_sentiment_score=results.overall_sentiment.hybrid_sentiment_score,
                sentiment_label=results.overall_sentiment.hybrid_label,
                lexicon_net_positivity=results.overall_sentiment.lexicon_scores.net_positivity,
                llm_sentiment_score=results.overall_sentiment.llm_scores.sentiment_score,
                
                # Complexity
                complexity_composite_score=results.overall_complexity.composite_score,
                complexity_level=results.overall_complexity.complexity_level,
                flesch_reading_ease=results.overall_complexity.flesch_reading_ease,
                flesch_kincaid_grade=results.overall_complexity.flesch_kincaid_grade,
                gunning_fog_index=results.overall_complexity.gunning_fog_index,
                smog_index=results.overall_complexity.smog_index,
                coleman_liau_index=results.overall_complexity.coleman_liau_index,
                
                # Numerical
                numeric_transparency_score=results.overall_numerical.numeric_transparency_score,
                numerical_specificity_index=results.overall_numerical.numerical_specificity_index,
                forward_looking_density=results.overall_numerical.forward_looking_density,
                backward_looking_density=results.overall_numerical.backward_looking_density,
                forward_to_backward_ratio=results.overall_numerical.forward_to_backward_ratio,
                contextualization_quality_score=results.overall_numerical.contextualization_quality_score,
                vs_sp500_benchmark=results.overall_numerical.vs_sp500_benchmark,
                
                # Deception (Phase 2)
                deception_risk_score=results.deception_risk.overall_risk_score if hasattr(results, 'deception_risk') else None,
                deception_risk_level=results.deception_risk.risk_level if hasattr(results, 'deception_risk') else None,
                deception_confidence=results.deception_risk.confidence if hasattr(results, 'deception_risk') else None,
                
                # Evasiveness (Phase 2)
                evasiveness_score=results.evasiveness_scores.overall_evasiveness if hasattr(results, 'evasiveness_scores') else None,
                evasiveness_level=results.evasiveness_scores.evasiveness_level if hasattr(results, 'evasiveness_scores') else None,
                evasiveness_vs_baseline=results.evasiveness_scores.vs_baseline if hasattr(results, 'evasiveness_scores') else None,
                
                # Counts
                word_count=results.word_count,
                sentence_count=results.sentence_count,
                
                # Full results
                full_results_json=asdict(results),
                
                # Key findings (stored as newline-separated text)
                key_findings="\n".join(results.key_findings),
                red_flags="\n".join(results.red_flags),
                strengths="\n".join(results.strengths)
            )
            
            session.add(analysis)
            session.commit()
            analysis_id = analysis.id
            
            return analysis_id
        finally:
            session.close()
    
    def load_analysis(self, analysis_id: int) -> Optional[AnalysisResult]:
        """Load analysis by ID"""
        session = self._get_session()
        try:
            return session.query(AnalysisResult).get(analysis_id)
        finally:
            session.close()
    
    def load_historical_analyses(
        self,
        company_name: str,
        quarters: int = 4
    ) -> List[AnalysisResult]:
        """
        Load N most recent analyses for a company
        
        Args:
            company_name: Company name
            quarters: Number of quarters to retrieve
            
        Returns:
            List of AnalysisResult objects (newest first)
        """
        session = self._get_session()
        try:
            company = session.query(Company).filter_by(name=company_name).first()
            if not company:
                return []
            
            analyses = session.query(AnalysisResult)\
                .filter_by(company_id=company.id)\
                .order_by(AnalysisResult.year.desc(), AnalysisResult.quarter.desc())\
                .limit(quarters)\
                .all()
            
            return analyses
        finally:
            session.close()
    
    def get_latest_analysis(self, company_name: str) -> Optional[AnalysisResult]:
        """Get most recent analysis for a company"""
        analyses = self.load_historical_analyses(company_name, quarters=1)
        return analyses[0] if analyses else None
    
    # ===== Sector/Peer Operations =====
    
    def get_sector_companies(self, sector: str) -> List[Company]:
        """Get all companies in a sector"""
        session = self._get_session()
        try:
            return session.query(Company).filter_by(sector=sector).all()
        finally:
            session.close()
    
    def calculate_sector_benchmark(
        self,
        sector: str,
        metric_name: str,
        quarter: str,
        year: int
    ) -> Dict[str, float]:
        """
        Calculate sector benchmark statistics for a metric
        
        Returns:
            Dict with mean, median, std_dev, min, max, count
        """
        session = self._get_session()
        try:
            # Get all companies in sector
            companies = session.query(Company).filter_by(sector=sector).all()
            company_ids = [c.id for c in companies]
            
            if not company_ids:
                return {
                    'mean': None,
                    'median': None,
                    'std_dev': None,
                    'min': None,
                    'max': None,
                    'count': 0
                }
            
            # Get metric values for all companies in that quarter
            values = session.query(getattr(AnalysisResult, metric_name))\
                .filter(
                    AnalysisResult.company_id.in_(company_ids),
                    AnalysisResult.quarter == quarter,
                    AnalysisResult.year == year
                )\
                .all()
            
            # Extract values (skip None)
            values = [v[0] for v in values if v[0] is not None]
            
            if not values:
                return {
                    'mean': None,
                    'median': None,
                    'std_dev': None,
                    'min': None,
                    'max': None,
                    'count': 0
                }
            
            return {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
        finally:
            session.close()
    
    def get_peer_analyses(
        self,
        company_names: List[str],
        quarter: str,
        year: int
    ) -> List[AnalysisResult]:
        """Get analyses for multiple companies in same quarter"""
        session = self._get_session()
        try:
            companies = session.query(Company)\
                .filter(Company.name.in_(company_names))\
                .all()
            
            company_ids = [c.id for c in companies]
            
            analyses = session.query(AnalysisResult)\
                .filter(
                    AnalysisResult.company_id.in_(company_ids),
                    AnalysisResult.quarter == quarter,
                    AnalysisResult.year == year
                )\
                .all()
            
            return analyses
        finally:
            session.close()
    
    # ===== Benchmark Operations =====
    
    def save_benchmark(
        self,
        sector: str,
        metric_name: str,
        value: float,
        quarter: Optional[str] = None,
        year: Optional[int] = None
    ) -> int:
        """Save sector benchmark"""
        session = self._get_session()
        try:
            benchmark = Benchmark(
                sector=sector,
                metric_name=metric_name,
                value=value,
                quarter=quarter,
                year=year
            )
            session.add(benchmark)
            session.commit()
            return benchmark.id
        finally:
            session.close()
    
    def get_benchmark(
        self,
        sector: str,
        metric_name: str,
        quarter: Optional[str] = None,
        year: Optional[int] = None
    ) -> Optional[Benchmark]:
        """Get benchmark value"""
        session = self._get_session()
        try:
            query = session.query(Benchmark)\
                .filter_by(sector=sector, metric_name=metric_name)
            
            if quarter and year:
                query = query.filter_by(quarter=quarter, year=year)
            
            return query.first()
        finally:
            session.close()
    
    # ===== Utility Methods =====
    
    def get_all_companies(self) -> List[Company]:
        """Get all companies in database"""
        session = self._get_session()
        try:
            return session.query(Company).all()
        finally:
            session.close()
    
    def search_companies(self, query: str) -> List[Company]:
        """Search companies by name or ticker"""
        session = self._get_session()
        try:
            search_pattern = f"%{query}%"
            return session.query(Company)\
                .filter(
                    or_(
                        Company.name.ilike(search_pattern),
                        Company.ticker.ilike(search_pattern)
                    )
                )\
                .all()
        finally:
            session.close()
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete analysis by ID"""
        session = self._get_session()
        try:
            analysis = session.query(AnalysisResult).get(analysis_id)
            if analysis:
                session.delete(analysis)
                session.commit()
                return True
            return False
        finally:
            session.close()
```

#### 4.3 Database Setup Script

**File:** `scripts/setup_database.py`

```python
#!/usr/bin/env python3
"""
Database setup script
Creates tables and optionally seeds initial data
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.database.models import Base
from src.database.repository import DatabaseRepository
from sqlalchemy import create_engine

def setup_database():
    """Create database tables"""
    print("Setting up database...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    print("\nCreating tables...")
    Base.metadata.create_all(engine)
    
    print("✓ Database setup complete!")
    print(f"\nDatabase location: {settings.DATABASE_PATH}")

def seed_benchmarks():
    """Seed initial benchmark data"""
    print("\nSeeding sector benchmarks...")
    
    repo = DatabaseRepository(settings.DATABASE_URL)
    
    # Add S&P 500 benchmarks
    repo.save_benchmark("S&P 500", "net_positivity", settings.SP500_NET_POSITIVITY)
    repo.save_benchmark("S&P 500", "numeric_transparency", settings.SP500_NUMERIC_TRANSPARENCY)
    repo.save_benchmark("S&P 500", "evasiveness", settings.SP500_EVASIVENESS_BASELINE)
    
    # Add sector-specific benchmarks
    for sector, transparency in settings.SECTOR_NUMERIC_TRANSPARENCY.items():
        repo.save_benchmark(sector, "numeric_transparency", transparency)
    
    print("✓ Benchmarks seeded!")

if __name__ == "__main__":
    setup_database()
    
    if input("\nSeed benchmark data? (y/n): ").lower() == 'y':
        seed_benchmarks()
```

**Usage:**
```bash
python scripts/setup_database.py
```

---

### 5. API & Web Interface Module (Phase 2D)

**Location:** `src/api/`  
**Priority:** MEDIUM  
**Status:** Not Started

#### 5.1 Overview

The API module provides a RESTful interface for remote transcript analysis, job tracking, and result retrieval.

**Key Features:**
- File upload endpoint
- Background job processing
- Job status tracking
- Multiple output formats (JSON, PDF, HTML, Excel)
- Historical data access
- Peer comparison
- Sector benchmarks

#### 5.2 FastAPI Application (`app.py`)

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from src.api.routes import router
from src.api.jobs import JobQueue
from config.settings import settings

# Setup logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global job queue
job_queue = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup/shutdown"""
    global job_queue
    
    # Startup
    logger.info("Starting Earnings Call Analyzer API...")
    job_queue = JobQueue(num_workers=settings.API_WORKERS)
    job_queue.start_workers()
    logger.info(f"Started {settings.API_WORKERS} worker threads")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    job_queue.stop_workers()
    logger.info("Workers stopped")

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="API for analyzing earnings call transcripts",
    version=settings.API_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "workers": len(job_queue.workers) if job_queue else 0,
        "jobs_queued": job_queue.queue.qsize() if job_queue else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
```

#### 5.3 API Routes (`routes.py`)

```python
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
from pathlib import Path
import tempfile
import shutil

from src.api.models import (
    AnalysisResponse,
    JobStatus,
    ComparisonRequest,
    HistoricalRequest
)
from src.api import app
from src.database.repository import DatabaseRepository
from config.settings import settings

router = APIRouter()

def get_job_queue():
    """Dependency to get job queue"""
    return app.job_queue

def get_db():
    """Dependency to get database"""
    return DatabaseRepository(settings.DATABASE_URL)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transcript(
    file: UploadFile = File(...),
    use_llm: bool = True,
    with_deception: bool = True,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    job_queue = Depends(get_job_queue)
):
    """
    Submit a transcript for analysis
    
    Args:
        file: Transcript file (.txt, .md)
        use_llm: Enable LLM features
        with_deception: Include deception analysis
        
    Returns:
        Job ID for tracking
    """
    # Validate file type
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(400, "Only .txt and .md files supported")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp:
        shutil.copyfileobj(file.file, temp)
        temp_path = temp.name
    
    # Create job
    job_id = job_queue.create_job(
        transcript_path=temp_path,
        use_llm=use_llm,
        with_deception=with_deception
    )
    
    return AnalysisResponse(
        job_id=job_id,
        status="queued",
        message="Analysis job submitted successfully"
    )

@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(
    job_id: str,
    job_queue = Depends(get_job_queue)
):
    """Check status of analysis job"""
    job = job_queue.get_job(job_id)
    
    if not job:
        raise HTTPException(404, "Job not found")
    
    return JobStatus(
        job_id=job_id,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at,
        completed_at=job.completed_at,
        error=job.error
    )

@router.get("/results/{job_id}")
async def get_results(
    job_id: str,
    format: str = "json",
    job_queue = Depends(get_job_queue)
):
    """
    Retrieve analysis results
    
    Args:
        job_id: Job identifier
        format: Output format (json, pdf, html, excel)
        
    Returns:
        Results in requested format
    """
    job = job_queue.get_job(job_id)
    
    if not job:
        raise HTTPException(404, "Job not found")
    
    if job.status != "completed":
        raise HTTPException(400, f"Job not completed (status: {job.status})")
    
    if format == "json":
        return job.results
    
    elif format == "pdf":
        from src.reporting.pdf_generator import PDFReportGenerator
        generator = PDFReportGenerator()
        pdf_path = Path(f"/tmp/{job_id}.pdf")
        generator.generate_detailed_report(job.results, pdf_path)
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"analysis_{job_id}.pdf")
    
    elif format == "html":
        from src.reporting.html_dashboard import HTMLDashboardGenerator
        generator = HTMLDashboardGenerator()
        html = generator.generate_dashboard(job.results)
        return HTMLResponse(content=html)
    
    elif format == "excel":
        from src.reporting.excel_exporter import ExcelReportExporter
        exporter = ExcelReportExporter()
        excel_path = Path(f"/tmp/{job_id}.xlsx")
        exporter.export_analysis(job.results, excel_path)
        return FileResponse(excel_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=f"analysis_{job_id}.xlsx")
    
    else:
        raise HTTPException(400, f"Unsupported format: {format}")

@router.get("/historical/{company}")
async def get_historical_data(
    company: str,
    quarters: int = 4,
    db = Depends(get_db)
):
    """Get historical analysis data for a company"""
    analyses = db.load_historical_analyses(company, quarters)
    
    if not analyses:
        raise HTTPException(404, f"No analyses found for company: {company}")
    
    return {
        "company": company,
        "quarters": quarters,
        "data": [
            {
                "quarter": a.quarter,
                "year": a.year,
                "sentiment": a.hybrid_sentiment_score,
                "complexity": a.complexity_composite_score,
                "transparency": a.numeric_transparency_score,
                "deception_risk": a.deception_risk_score,
                "evasiveness": a.evasiveness_score
            }
            for a in analyses
        ]
    }

@router.post("/compare")
async def compare_companies(
    request: ComparisonRequest,
    db = Depends(get_db)
):
    """Compare multiple companies"""
    # Get analyses for all companies
    analyses = db.get_peer_analyses(
        request.company_names,
        request.quarter,
        request.year
    )
    
    if not analyses:
        raise HTTPException(404, "No analyses found for specified companies")
    
    # Format comparison data
    comparison = {}
    for analysis in analyses:
        company_name = analysis.company.name
        comparison[company_name] = {
            "sentiment": analysis.hybrid_sentiment_score,
            "complexity": analysis.complexity_composite_score,
            "transparency": analysis.numeric_transparency_score,
            "deception_risk": analysis.deception_risk_score,
            "evasiveness": analysis.evasiveness_score
        }
    
    return comparison

@router.get("/benchmarks/{sector}")
async def get_sector_benchmarks(
    sector: str,
    quarter: str,
    year: int,
    db = Depends(get_db)
):
    """Get sector benchmarks for a specific quarter"""
    metrics = [
        'hybrid_sentiment_score',
        'complexity_composite_score',
        'numeric_transparency_score',
        'deception_risk_score',
        'evasiveness_score'
    ]
    
    benchmarks = {}
    for metric in metrics:
        benchmarks[metric] = db.calculate_sector_benchmark(
            sector, metric, quarter, year
        )
    
    return {
        "sector": sector,
        "quarter": quarter,
        "year": year,
        "benchmarks": benchmarks
    }

@router.get("/companies")
async def list_companies(
    search: Optional[str] = None,
    sector: Optional[str] = None,
    db = Depends(get_db)
):
    """List all companies"""
    if search:
        companies = db.search_companies(search)
    elif sector:
        companies = db.get_sector_companies(sector)
    else:
        companies = db.get_all_companies()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "ticker": c.ticker,
            "sector": c.sector,
            "industry": c.industry
        }
        for c in companies
    ]
```

#### 5.4 API Models (`models.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: float = 0.0  # 0-100
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class ComparisonRequest(BaseModel):
    company_names: List[str]
    quarter: str
    year: int
    metrics: Optional[List[str]] = None

class HistoricalRequest(BaseModel):
    company: str
    quarters: int = 4
```

#### 5.5 Job Queue (`jobs.py`)

```python
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict
from queue import Queue
from threading import Thread
import logging

logger = logging.getLogger(__name__)

@dataclass
class AnalysisJob:
    job_id: str
    transcript_path: str
    use_llm: bool
    with_deception: bool
    status: str = "queued"  # queued, processing, completed, failed
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    results: Optional[Dict] = None
    error: Optional[str] = None

class JobQueue:
    def __init__(self, num_workers: int = 2):
        self.jobs: Dict[str, AnalysisJob] = {}
        self.queue = Queue()
        self.num_workers = num_workers
        self.workers = []
        self.running = False
    
    def create_job(
        self,
        transcript_path: str,
        use_llm: bool = True,
        with_deception: bool = True
    ) -> str:
        """Create new analysis job"""
        job_id = str(uuid.uuid4())
        job = AnalysisJob(
            job_id=job_id,
            transcript_path=transcript_path,
            use_llm=use_llm,
            with_deception=with_deception
        )
        self.jobs[job_id] = job
        self.queue.put(job_id)
        logger.info(f"Created job {job_id}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        """Retrieve job by ID"""
        return self.jobs.get(job_id)
    
    def worker(self):
        """Background worker thread"""
        from src.analysis.aggregator import EarningsCallAnalyzer
        from src.database.repository import DatabaseRepository
        from config.settings import settings
        from dataclasses import asdict
        
        logger.info("Worker thread started")
        
        while self.running:
            try:
                job_id = self.queue.get(timeout=1)
            except:
                continue
            
            if job_id is None:  # Shutdown signal
                break
            
            job = self.jobs[job_id]
            job.status = "processing"
            logger.info(f"Processing job {job_id}")
            
            try:
                # Perform analysis
                analyzer = EarningsCallAnalyzer(use_llm_features=job.use_llm)
                
                # If deception analysis enabled, ensure it's integrated
                if job.with_deception:
                    from src.database.repository import DatabaseRepository
                    analyzer.database_repo = DatabaseRepository(settings.DATABASE_URL)
                
                job.progress = 10.0
                results = analyzer.analyze_transcript(job.transcript_path)
                job.progress = 80.0
                
                # Save to database
                if hasattr(analyzer, 'database_repo') and analyzer.database_repo:
                    analyzer.database_repo.save_analysis(results)
                
                job.progress = 90.0
                
                # Store results
                job.results = asdict(results)
                job.status = "completed"
                job.progress = 100.0
                job.completed_at = datetime.now()
                
                logger.info(f"Job {job_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Job {job_id} failed: {e}", exc_info=True)
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.now()
            
            finally:
                self.queue.task_done()
    
    def start_workers(self):
        """Start worker threads"""
        self.running = True
        for i in range(self.num_workers):
            thread = Thread(target=self.worker, daemon=True, name=f"Worker-{i}")
            thread.start()
            self.workers.append(thread)
        logger.info(f"Started {self.num_workers} workers")
    
    def stop_workers(self):
        """Stop worker threads"""
        self.running = False
        
        # Send shutdown signals
        for _ in range(self.num_workers):
            self.queue.put(None)
        
        # Wait for workers to finish
        for thread in self.workers:
            thread.join(timeout=5)
        
        logger.info("All workers stopped")
```

**CLI Integration:**

```python
# In cli.py

@cli.command()
@click.option('--host', default=None, help='API host')
@click.option('--port', type=int, default=None, help='API port')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host, port, reload):
    """Start the API server"""
    import uvicorn
    from config.settings import settings
    
    api_host = host or settings.API_HOST
    api_port = port or settings.API_PORT
    
    click.echo(f"\n🚀 Starting API server on {api_host}:{api_port}...\n")
    
    uvicorn.run(
        "src.api.app:app",
        host=api_host,
        port=api_port,
        reload=reload
    )
```

**Usage:**
```bash
# Start server
earnings-analyzer serve

# Or with options
earnings-analyzer serve --host 0.0.0.0 --port 8000 --reload
```

---

## Implementation Roadmap

### Phase 2A: Deception Detection Integration (Week 1-2)

**Priority:** HIGH  
**Status:** Partially Complete

**Tasks:**
- [ ] Move `src/deception/` to `src/analysis/deception/`
- [ ] Update all imports throughout codebase
- [ ] Add deception analyzers to `aggregator.py __init__`
- [ ] Add `DeceptionRiskScore` and `EvasivenessScores` to `ComprehensiveAnalysisResult`
- [ ] Implement deception analysis in `analyze_transcript()`
- [ ] Update `_generate_insights()` to include deception insights
- [ ] Update `print_summary()` to display deception results
- [ ] Update `save_results()` to include deception data in JSON
- [ ] Add CLI flag `--with-deception` to `analyze` command
- [ ] Write unit tests for integration
- [ ] Write integration tests for full pipeline
- [ ] Update documentation and README

**Acceptance Criteria:**
- All tests pass
- Deception analysis works on sample transcripts
- CLI properly displays deception results
- JSON output includes all deception metrics

---

### Phase 2B: Database & Persistence (Week 2-3)

**Priority:** HIGH

**Tasks:**
- [ ] Create `src/database/models.py` with SQLAlchemy models
- [ ] Create `src/database/repository.py` with data access layer
- [ ] Create `scripts/setup_database.py` for initialization
- [ ] Add database configuration to `settings.py`
- [ ] Integrate database saving in `aggregator.py`
- [ ] Test database operations (CRUD)
- [ ] Add database migration support (Alembic)
- [ ] Write unit tests for repository
- [ ] Seed benchmark data
- [ ] Update documentation

**Acceptance Criteria:**
- Database tables created successfully
- Analysis results save and load correctly
- Historical data retrieval works
- Sector benchmarks calculated correctly

---

### Phase 2C: Advanced Reporting (Week 3-5)

**Priority:** HIGH

**Tasks:**

**PDF Generation:**
- [ ] Create Jinja2 templates for reports
- [ ] Implement `PDFReportGenerator` class
- [ ] Add chart generation with Plotly
- [ ] Test PDF generation with sample data
- [ ] Add CLI command for PDF reports
- [ ] Write unit tests

**HTML Dashboard:**
- [ ] Create HTML templates
- [ ] Implement `HTMLDashboardGenerator` class
- [ ] Add interactive Plotly charts
- [ ] Test responsiveness
- [ ] Add CLI command for HTML dashboards
- [ ] Write unit tests

**Excel Export:**
- [ ] Implement `ExcelReportExporter` class
- [ ] Create workbook structure with multiple sheets
- [ ] Add conditional formatting
- [ ] Add formulas and charts
- [ ] Test with sample data
- [ ] Add CLI command for Excel exports
- [ ] Write unit tests

**Acceptance Criteria:**
- PDF reports generate correctly with charts
- HTML dashboards are interactive and responsive
- Excel exports have proper structure and formatting
- All three formats tested on multiple transcripts

---

### Phase 2D: API & Web Interface (Week 5-6)

**Priority:** MEDIUM

**Tasks:**
- [ ] Implement `api/app.py` with FastAPI
- [ ] Implement `api/routes.py` with all endpoints
- [ ] Implement `api/jobs.py` with job queue
- [ ] Implement `api/models.py` with Pydantic models
- [ ] Add file upload endpoint
- [ ] Add job status tracking
- [ ] Add result retrieval in multiple formats
- [ ] Add historical data endpoints
- [ ] Add comparison endpoints
- [ ] Add benchmark endpoints
- [ ] Write API tests with TestClient
- [ ] Create OpenAPI/Swagger documentation
- [ ] Add authentication (optional)
- [ ] Test with Postman/curl
- [ ] Add CLI command to start server

**Acceptance Criteria:**
- API accepts file uploads
- Jobs process in background
- Status tracking works
- Results available in all formats
- All endpoints tested
- API documentation complete

---

### Phase 2E: Comparative Analysis (Week 6-7)

**Priority:** MEDIUM

**Tasks:**

**Historical Trends:**
- [ ] Implement `comparative/historical.py`
- [ ] Add trend detection (linear regression)
- [ ] Add volatility measurement
- [ ] Add seasonality detection
- [ ] Add anomaly detection
- [ ] Add simple forecasting
- [ ] Add CLI command for historical analysis
- [ ] Write unit tests

**Peer Comparison:**
- [ ] Implement `comparative/peer_comparison.py`
- [ ] Add sector company retrieval
- [ ] Add percentile calculation
- [ ] Add sector benchmarking
- [ ] Add competitive advantage identification
- [ ] Add CLI command for peer comparison
- [ ] Write unit tests

**Acceptance Criteria:**
- Historical trends work with 4+ quarters
- Trend detection accurately identifies patterns
- Peer comparison works with sector data
- Percentile rankings calculated correctly
- CLI commands produce readable output

---

### Phase 2F: Pattern Recognition (Week 8+)

**Priority:** LOW

**Tasks:**
- [ ] Implement `analytics/patterns.py`
- [ ] Add crisis communication detection
- [ ] Add defensive posture detection
- [ ] Implement `analytics/predictions.py`
- [ ] Add simple predictive models
- [ ] Add disclaimers
- [ ] Write tests
- [ ] Document limitations

**Acceptance Criteria:**
- Patterns detected on known examples
- Predictions include proper disclaimers
- Tests pass
- Documentation complete

---

## Testing Strategy

### Unit Tests Structure

```
tests/
├── unit/
│   ├── test_deception/
│   │   ├── test_detector.py
│   │   ├── test_linguistic_markers.py
│   │   ├── test_evasiveness.py
│   │   └── test_question_evasion.py
│   ├── test_comparative/
│   │   ├── test_historical.py
│   │   └── test_peer_comparison.py
│   ├── test_reporting/
│   │   ├── test_pdf_generator.py
│   │   ├── test_html_dashboard.py
│   │   └── test_excel_exporter.py
│   ├── test_database/
│   │   ├── test_models.py
│   │   └── test_repository.py
│   └── test_api/
│       ├── test_routes.py
│       └── test_jobs.py
├── integration/
│   ├── test_full_pipeline.py
│   ├── test_api_workflow.py
│   └── test_report_generation.py
└── fixtures/
    ├── sample_transcripts/
    ├── expected_outputs/
    └── mock_data/
```

### Key Test Cases

**Deception Detection:**
```python
def test_deception_risk_calculation():
    """Test overall deception risk score calculation"""
    # Test with known high-risk transcript
    # Test with known low-risk transcript
    # Verify score ranges (0-100)
    # Verify risk level categorization

def test_linguistic_markers():
    """Test individual linguistic indicators"""
    # Test hedging detection
    # Test qualifier detection
    # Test passive voice detection
    # Test pronoun distancing

def test_evasiveness_scoring():
    """Test evasiveness composite score"""
    # Test vs baseline comparison
    # Test level categorization
    # Test most evasive sentence identification

def test_question_evasion():
    """Test Q&A analysis"""
    # Test question/response pairing
    # Test topic extraction
    # Test relevance scoring
    # Test evasion type classification
```

**Database:**
```python
def test_save_and_load_analysis():
    """Test database persistence"""
    # Save analysis result
    # Load by ID
    # Verify all fields match

def test_historical_retrieval():
    """Test loading multiple quarters"""
    # Save 4 quarters of data
    # Load historical (n=4)
    # Verify order (newest first)
    # Verify data integrity

def test_sector_benchmarks():
    """Test benchmark calculations"""
    # Create multiple companies in sector
    # Save analyses
    # Calculate sector benchmark
    # Verify mean, median, std_dev
```

**Reporting:**
```python
def test_pdf_generation():
    """Test PDF report creation"""
    # Generate PDF
    # Verify file exists
    # Verify file size > 0
    # Verify PDF is valid (can open)

def test_html_dashboard():
    """Test HTML dashboard generation"""
    # Generate HTML
    # Verify valid HTML structure
    # Verify all charts present
    # Verify Bootstrap classes

def test_excel_export():
    """Test Excel workbook creation"""
    # Generate Excel
    # Verify file exists
    # Load with openpyxl
    # Verify sheet structure
    # Verify formulas
```

**API:**
```python
def test_analyze_endpoint():
    """Test analysis submission"""
    # Upload file
    # Get job ID
    # Verify status = queued

def test_job_status_tracking():
    """Test status endpoint"""
    # Submit job
    # Poll status
    # Verify status progression
    # Verify completion

def test_result_retrieval():
    """Test result formats"""
    # Get results as JSON
    # Get results as PDF
    # Get results as HTML
    # Get results as Excel
    # Verify each format

def test_historical_endpoint():
    """Test historical data API"""
    # Request historical data
    # Verify response structure
    # Verify data accuracy
```

---

## Deployment Considerations

### Development Environment

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-phase2.txt

# Setup database
python scripts/setup_database.py

# Setup NLP (if needed)
python scripts/setup_nlp.py --create-configs

# Download dictionaries
python scripts/download_dictionaries.py --create-starter

# Run tests
pytest tests/

# Start API server (development)
earnings-analyzer serve --reload

# Or directly
uvicorn src.api.app:app --reload --port 8000
```

### Production Deployment

**Docker Setup:**

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-phase2.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-phase2.txt

# Copy application
COPY . .

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Create data directories
RUN mkdir -p data/reports data/dictionaries data/benchmarks

# Expose API port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  analyzer:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - DATABASE_URL=sqlite:////app/data/earnings_analyzer.db
      - LOG_LEVEL=INFO
    depends_on:
      - ollama
    restart: unless-stopped
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: serve
    restart: unless-stopped

volumes:
  ollama_data:
```

**Start Services:**
```bash
docker-compose up -d
docker-compose logs -f
```

### Environment Variables

```bash
# .env.production
OLLAMA_HOST=http://ollama:11434
DATABASE_URL=sqlite:////app/data/earnings_analyzer.db
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=INFO

# Features
ENABLE_DECEPTION_ANALYSIS=true
ENABLE_HISTORICAL_TRACKING=true
ENABLE_PDF_REPORTS=true
ENABLE_HTML_DASHBOARDS=true
ENABLE_EXCEL_EXPORTS=true

# Security (if needed)
API_KEY=your-secret-key
ALLOWED_ORIGINS=https://yourapp.com
```

### Performance Considerations

1. **LLM Optimization:**
   - Cache identical text segments
   - Use smaller models for less critical analysis
   - Batch process when possible

2. **Database:**
   - Add indexes on frequently queried columns
   - Consider PostgreSQL for production
   - Implement connection pooling

3. **API:**
   - Use Redis for job queue (production)
   - Implement rate limiting
   - Add response caching
   - Use async/await for I/O

4. **Reporting:**
   - Generate reports asynchronously
   - Cache generated reports
   - Use CDN for static assets

---

## Success Criteria

### Phase 2 Completion Checklist

**Core Features:**
- [ ] Deception risk scoring works on all test transcripts
- [ ] Database successfully stores and retrieves analysis results
- [ ] Historical trend analysis works with 4+ quarters
- [ ] Peer comparison works with sector data
- [ ] PDF reports generate correctly with charts
- [ ] HTML dashboards are interactive and responsive
- [ ] Excel exports have proper structure and formatting
- [ ] API accepts uploads and returns results
- [ ] All CLI commands work as expected

**Quality:**
- [ ] All unit tests pass (>90% coverage)
- [ ] All integration tests pass
- [ ] API tests pass
- [ ] No critical bugs
- [ ] Code reviewed and documented
- [ ] Performance benchmarks met (<30s per transcript)

**Documentation:**
- [ ] API documentation complete (Swagger/OpenAPI)
- [ ] User guide updated
- [ ] Developer documentation updated
- [ ] Deployment guide complete
- [ ] All modules have docstrings

**Deployment:**
- [ ] Docker containers build successfully
- [ ] Application runs in production mode
- [ ] Database migrations work
- [ ] Logging and monitoring configured
- [ ] Error handling comprehensive

---

## Appendix

### Dependencies

**requirements-phase2.txt:**
```txt
# Phase 2: Database
sqlalchemy>=2.0.0
alembic>=1.12.0

# Phase 2: API
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.4.0

# Phase 2: Reporting - PDF
weasyprint>=60.0
jinja2>=3.1.2

# Phase 2: Reporting - Excel
openpyxl>=3.1.2

# Phase 2: Visualization
plotly>=5.17.0
kaleido>=0.2.1

# Phase 2: Job Queue (optional)
redis>=5.0.0
rq>=1.15.0

# Phase 2: Testing
pytest-asyncio>=0.21.0
httpx>=0.25.0
```

### Glossary

**Terms:**
- **Deception Risk:** Composite score (0-100) indicating likelihood of deceptive communication
- **Evasiveness:** Measure of vague, indirect, or evasive language
- **Question Dodging:** Avoiding direct answers to analyst questions
- **Topic Deflection:** Changing subject rather than answering question
- **Contextualization:** Providing comparison, explanation, and implication for numbers
- **Net Positivity:** (Positive words - Negative words) / (Positive + Negative) × 100
- **Hybrid Sentiment:** Weighted combination of lexicon (30%) and LLM (70%) sentiment

**Acronyms:**
- **API:** Application Programming Interface
- **CLI:** Command Line Interface
- **CRUD:** Create, Read, Update, Delete
- **GICS:** Global Industry Classification Standard
- **LLM:** Large Language Model
- **LM:** Loughran-McDonald
- **ORM:** Object-Relational Mapping
- **PDF:** Portable Document Format
- **Q&A:** Question and Answer
- **REST:** Representational State Transfer
- **SQL:** Structured Query Language

---

**END OF PHASE 2 SPECIFICATION**

---

## Document Metadata

**Version:** 2.0.0  
**Date:** 2025-01-15  
**Author:** AI Assistant  
**Purpose:** Master reference document for Phase 2 development

**Usage:**
This document should be used to:
1. Prime future chat conversations about Phase 2
2. Validate existing code against the roadmap
3. Guide implementation of new features
4. Ensure consistency across all Phase 2 modules
5. Track progress and completion status

**Updates:**
When implementing Phase 2 features, update this document to reflect:
- Status changes (Not Started → In Progress → Complete)
- Implementation decisions
- Any deviations from the original plan
- Lessons learned
