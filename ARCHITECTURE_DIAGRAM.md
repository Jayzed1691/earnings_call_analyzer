# Phase 2A Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     EARNINGS CALL ANALYZER - PHASE 2A                         ║
║                        Deception Detection Integrated                         ║
╚══════════════════════════════════════════════════════════════════════════════╝


┌──────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  cli.py                                                                       │
│  ├─ analyze --with-deception    ← Main command                              │
│  ├─ deception                    ← Deception-only report                    │
│  ├─ batch --with-deception       ← Batch processing                         │
│  └─ config                       ← View settings                             │
│                                                                               │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           CONFIGURATION LAYER                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  config/settings.py                                                           │
│  ├─ Phase 1 Settings                                                         │
│  │  ├─ Sentiment weights (70% LLM / 30% Lexicon)                            │
│  │  ├─ Complexity thresholds                                                 │
│  │  └─ Numerical benchmarks (S&P 500: 3.5%)                                 │
│  │                                                                            │
│  └─ Phase 2A Settings ✨ NEW                                                 │
│     ├─ ENABLE_DECEPTION_ANALYSIS = True                                      │
│     ├─ DECEPTION_RISK_WARNING = 50                                           │
│     ├─ DECEPTION_RISK_CRITICAL = 70                                          │
│     ├─ SP500_EVASIVENESS_BASELINE = 11.0                                     │
│     └─ Component weights (Linguistic:25%, Behavioral:25%,                    │
│                           Numerical:30%, Evasion:20%)                         │
│                                                                               │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          MAIN ORCHESTRATOR                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  src/analysis/aggregator.py (EarningsCallAnalyzer)                           │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ __init__(use_llm, enable_deception_analysis)                           │ │
│  │  ├─ Phase 1 Analyzers                                                  │ │
│  │  │  ├─ TranscriptProcessor                                             │ │
│  │  │  ├─ HybridSentimentAnalyzer                                         │ │
│  │  │  ├─ ComplexityAnalyzer                                              │ │
│  │  │  └─ NumericalAnalyzer                                               │ │
│  │  │                                                                      │ │
│  │  └─ Phase 2A Analyzers ✨ NEW                                          │ │
│  │     ├─ DeceptionRiskAnalyzer                                           │ │
│  │     ├─ EvasivenessAnalyzer                                             │ │
│  │     └─ QuestionEvasionDetector                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ analyze_transcript(file_path) → ComprehensiveAnalysisResult           │ │
│  │                                                                         │ │
│  │  Step 1: Preprocess transcript                                         │ │
│  │          └─ Extract sections, speakers, metadata                       │ │
│  │                                                                         │ │
│  │  Step 2: Phase 1 Analysis                                              │ │
│  │          ├─ Sentiment (Lexicon + LLM)                                  │ │
│  │          ├─ Complexity (5 readability metrics)                         │ │
│  │          └─ Numerical (transparency, specificity, etc.)                │ │
│  │                                                                         │ │
│  │  Step 3: Phase 2A Deception Analysis ✨ NEW                           │ │
│  │          ├─ Risk scoring (4 component weights)                         │ │
│  │          ├─ Evasiveness patterns                                       │ │
│  │          └─ Q&A evasion detection                                      │ │
│  │                                                                         │ │
│  │  Step 4: Generate insights                                             │ │
│  │          └─ Key findings, red flags, strengths                         │ │
│  │                                                                         │ │
│  │  Return: ComprehensiveAnalysisResult                                   │ │
│  │          ├─ Phase 1 metrics                                            │ │
│  │          └─ Phase 2A metrics (deception_risk, evasiveness, qa_analysis)│ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
└───┬───────────────────────────────────────────────────────────────┬──────────┘
    │                                                               │
    │ Phase 1 Analysis                                              │ Phase 2A
    │                                                               │
    ▼                                                               ▼

┌─────────────────────────────┐                    ┌──────────────────────────┐
│     PHASE 1 ANALYZERS       │                    │   PHASE 2A ANALYZERS     │
├─────────────────────────────┤                    ├──────────────────────────┤
│                             │                    │                          │
│ TranscriptProcessor         │                    │ DeceptionRiskAnalyzer    │
│  └─ Sections, speakers      │                    │  ├─ Linguistic markers   │
│                             │                    │  ├─ Behavioral patterns  │
│ HybridSentimentAnalyzer     │                    │  ├─ Numerical indicators │
│  ├─ LexiconAnalyzer (30%)   │                    │  └─ Evasion detection    │
│  └─ LLMAnalyzer (70%)       │                    │                          │
│                             │                    │ EvasivenessAnalyzer      │
│ ComplexityAnalyzer          │                    │  ├─ Qualifiers           │
│  ├─ Flesch Reading Ease     │                    │  ├─ Hedging language     │
│  ├─ Flesch-Kincaid Grade    │                    │  ├─ Passive voice        │
│  ├─ Gunning Fog             │                    │  ├─ Vague pronouns       │
│  ├─ SMOG Index              │                    │  └─ Distancing score     │
│  └─ Coleman-Liau            │                    │                          │
│                             │                    │ QuestionEvasionDetector  │
│ NumericalAnalyzer           │                    │  ├─ Topic overlap        │
│  ├─ Transparency %          │                    │  ├─ Deflection patterns  │
│  ├─ Specificity index       │                    │  ├─ Vagueness density    │
│  ├─ Forward/Backward        │                    │  └─ Relevance scoring    │
│  └─ Contextualization       │                    │                          │
│                             │                    │                          │
└─────────────────────────────┘                    └──────────────────────────┘

                                     │
                                     ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT RESULTS                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ComprehensiveAnalysisResult                                                  │
│  ├─ Metadata (company, quarter, year, timestamp)                             │
│  │                                                                            │
│  ├─ Phase 1 Metrics                                                          │
│  │  ├─ overall_sentiment: HybridSentimentScores                              │
│  │  ├─ overall_complexity: ComplexityScores                                  │
│  │  ├─ overall_numerical: NumericalScores                                    │
│  │  ├─ section_metrics (Prepared Remarks vs Q&A)                             │
│  │  └─ speaker_metrics (CEO, CFO)                                            │
│  │                                                                            │
│  ├─ Phase 2A Metrics ✨ NEW                                                  │
│  │  ├─ deception_risk: DeceptionRiskScore                                    │
│  │  │  ├─ overall_risk_score: 0-100                                          │
│  │  │  ├─ risk_level: Low/Moderate/High/Critical                             │
│  │  │  ├─ confidence: 0-1                                                    │
│  │  │  ├─ indicators: DeceptionIndicators                                    │
│  │  │  │  ├─ Linguistic (hedging, qualifiers, passive, distancing)           │
│  │  │  │  ├─ Behavioral (complexity spikes, sentiment drops)                 │
│  │  │  │  ├─ Numerical (forward avoidance, vague numbers)                    │
│  │  │  │  └─ Evasion (question dodge, topic deflection)                      │
│  │  │  └─ triggered_flags: List[str]                                         │
│  │  │                                                                         │
│  │  ├─ evasiveness_scores: EvasivenessScores                                 │
│  │  │  ├─ overall_evasiveness: 0-100                                         │
│  │  │  ├─ evasiveness_level: Low/Moderate/High/Very High                     │
│  │  │  ├─ vs_baseline: above/at/below                                        │
│  │  │  └─ component_scores                                                   │
│  │  │                                                                         │
│  │  └─ qa_analysis: List[QuestionResponse]                                   │
│  │     └─ For each Q&A pair:                                                 │
│  │        ├─ question, response                                              │
│  │        ├─ response_relevance: 0-1                                         │
│  │        ├─ is_evasive: bool                                                │
│  │        ├─ evasion_type: str                                               │
│  │        └─ topic_overlap: 0-1                                              │
│  │                                                                            │
│  └─ Insights                                                                  │
│     ├─ key_findings: List[str]                                               │
│     ├─ red_flags: List[str]                                                  │
│     └─ strengths: List[str]                                                  │
│                                                                               │
└───┬───────────────────────────────────────────────────────────────┬──────────┘
    │                                                               │
    │ Console Output                                                │ JSON Export
    ▼                                                               ▼

┌──────────────────────────┐                         ┌─────────────────────────┐
│  print_summary()         │                         │  save_results()         │
│  • Phase 1 metrics       │                         │  • Complete JSON output │
│  • Phase 2A metrics ✨   │                         │  • All nested dataclass │
│  • Risk assessment       │                         │  • Timestamp & metadata │
│  • Red flags             │                         │  • Importable format    │
│  • Recommendations       │                         │                         │
└──────────────────────────┘                         └─────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════

RISK SCORING FORMULA (Phase 2A):

  Overall Risk = Linguistic(0.25) + Behavioral(0.25) + Numerical(0.30) + Evasion(0.20)

  Where:
    Linguistic  = hedging(0.25) + qualifiers(0.25) + passive(0.20) 
                  + pronouns(0.15) + distancing(0.15)
    
    Behavioral  = complexity_spike(0.45) + sentiment_drop(0.35) 
                  + length_variance(0.20)
    
    Numerical   = forward_avoidance(0.35) + vague_ratio(0.30) 
                  + context_gap(0.35)
    
    Evasion     = question_dodge(0.60) + topic_deflection(0.40)

═══════════════════════════════════════════════════════════════════════════════


DATA FLOW EXAMPLE:

  1. User: python cli.py analyze transcript.txt --with-deception
  
  2. CLI loads settings.py
     → ENABLE_DECEPTION_ANALYSIS = True ✓
  
  3. CLI creates EarningsCallAnalyzer(enable_deception_analysis=True)
     → Initializes all Phase 1 analyzers
     → Initializes all Phase 2A analyzers ✨
  
  4. analyzer.analyze_transcript("transcript.txt")
     → Step 1: Preprocess (sections, speakers)
     → Step 2: Phase 1 (sentiment, complexity, numerical)
     → Step 3: Phase 2A (deception, evasiveness, Q&A) ✨
     → Step 4: Generate insights
     → Returns ComprehensiveAnalysisResult with all metrics
  
  5. analyzer.print_summary(results)
     → Console output with Phase 1 & Phase 2A sections
  
  6. analyzer.save_results(results, "output.json")
     → JSON file with complete analysis

═══════════════════════════════════════════════════════════════════════════════
```

## Key Integration Points

### 1. Settings → Analyzers
```python
settings.ENABLE_DECEPTION_ANALYSIS → EarningsCallAnalyzer.__init__()
settings.DECEPTION_RISK_WARNING → DeceptionRiskAnalyzer.categorize_risk()
settings.SP500_EVASIVENESS_BASELINE → EvasivenessAnalyzer.analyze()
```

### 2. Phase 1 → Phase 2A Data Flow
```python
sentiment_scores ─┐
complexity_scores ├─→ DeceptionRiskAnalyzer.analyze()
numerical_scores ─┘      └─→ deception_risk: DeceptionRiskScore

cleaned_text ───→ EvasivenessAnalyzer.analyze()
                    └─→ evasiveness_scores: EvasivenessScores

qa_section ───→ QuestionEvasionDetector.analyze_qa_section()
                └─→ qa_analysis: List[QuestionResponse]
```

### 3. Results → Outputs
```python
ComprehensiveAnalysisResult ─┬─→ print_summary() → Console
                              ├─→ save_results() → JSON
                              └─→ [Future] → PDF, HTML, Excel
```

## Component Dependencies

```
aggregator.py
├── Requires: config.settings
├── Requires: src.core.transcript_processor
├── Requires: src.analysis.sentiment.hybrid_scorer
├── Requires: src.analysis.complexity.readability
├── Requires: src.analysis.numerical.transparency
└── Requires (Phase 2A):
    ├── src.analysis.deception.detector
    ├── src.analysis.deception.evasiveness
    └── src.analysis.deception.question_evasion

deception/detector.py
├── Requires: config.settings (thresholds)
├── Requires: src.analysis.deception.linguistic_markers
├── Requires: src.analysis.deception.evasiveness
└── Requires: Phase 1 scores (sentiment, complexity, numerical)

deception/evasiveness.py
├── Requires: config.settings (baseline)
├── Requires: src.analysis.deception.linguistic_markers
└── Requires: src.utils.text_utils

deception/question_evasion.py
├── Requires: config.settings (thresholds)
├── Requires: src.utils.text_utils
├── Requires: src.models.ollama_client (optional)
└── Requires: spacy (optional, for NER)
```

## ✅ Integration Checkpoints

- [x] Settings file has all Phase 2A configuration
- [x] Aggregator imports deception modules
- [x] ComprehensiveAnalysisResult has deception fields
- [x] Deception analyzers initialized in __init__()
- [x] analyze_transcript() calls deception analysis
- [x] _generate_insights() includes deception insights
- [x] print_summary() displays deception metrics
- [x] save_results() includes deception in JSON
- [x] CLI supports --with-deception flag
- [x] All component dependencies satisfied
