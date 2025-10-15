# Earnings Call Analysis Platform

A comprehensive platform for analyzing earnings call transcripts using advanced NLP techniques including sentiment analysis, language complexity metrics, and numerical transparency assessment.

## Features (Phase 1)

### Core Analysis
- **Multi-Layered Sentiment Analysis**
  - Loughran-McDonald dictionary-based analysis (7 categories)
  - Ollama LLM-based contextual sentiment
  - Hybrid scoring (70% LLM, 30% Lexicon)

- **Language Complexity Analysis**
  - Flesch Reading Ease Score
  - Flesch-Kincaid Grade Level
  - Gunning Fog Index
  - SMOG Index
  - Coleman-Liau Index
  - Composite complexity score

- **Numerical Content Transparency**
  - Numeric transparency score
  - Numerical specificity index
  - Forward-looking numerical density
  - Contextualization quality score
  - S&P 500 benchmarking

### Granular Analysis
- Speaker-level metrics (CEO, CFO, etc.)
- Section-level analysis (Prepared Remarks vs Q&A)
- Automated red flag identification
- Strength and weakness detection

## Installation

### Prerequisites

1. **Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Ollama** (for local LLM features)
   
   Install Ollama from [https://ollama.ai](https://ollama.ai)
   
   ```bash
   # On macOS/Linux
   curl https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve
   ```

3. **Pull required models**
   ```bash
   # Recommended model for sentiment analysis
   ollama pull llama3.1:8b
   
   # Alternative models (optional)
   ollama pull mistral
   ollama pull phi3
   ```

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd earnings-call-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data**
   ```python
   python -c "import nltk; nltk.download('punkt')"
   ```

5. **Set up Loughran-McDonald dictionaries**
   ```bash
   # Create starter dictionaries
   python scripts/download_dictionaries.py --create-starter
   ```

6. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

7. **Verify setup**
   ```bash
   python cli.py check-setup
   ```

## Quick Start

### Command-Line Interface

1. **Analyze a transcript**
   ```bash
   python cli.py analyze path/to/transcript.txt --summary
   ```

2. **Fast mode (no LLM features)**
   ```bash
   python cli.py analyze path/to/transcript.txt --no-llm --summary
   ```

3. **Save results to custom location**
   ```bash
   python cli.py analyze transcript.txt -o results/analysis.json -s
   ```

4. **Validate a transcript**
   ```bash
   python cli.py validate transcript.txt
   ```

5. **View system information**
   ```bash
   python cli.py info
   ```

### Python API

```python
from src.analysis.aggregator import EarningsCallAnalyzer

# Initialize analyzer
analyzer = EarningsCallAnalyzer(use_llm_features=True)

# Analyze transcript
results = analyzer.analyze_transcript('transcript.txt')

# Print summary
analyzer.print_summary(results)

# Save results
analyzer.save_results(results, 'analysis_results.json')
```

## Transcript Format

Transcripts should be plain text files (.txt or .md) with the following structure:

```text
Company: Apple Inc.
Ticker: AAPL
Quarter: Q4
Year: 2024
Date: October 31, 2024

[Prepared Remarks Section]
Tim Cook - CEO: [Opening statement...]

Luca Maestri - CFO: [Financial results...]

[Q&A Section]
Analyst Name - Firm: [Question...]

Tim Cook - CEO: [Answer...]
```

### Required Elements
- Speaker identification: `Name - Title:`
- Optional metadata: Company, Ticker, Quarter, Year, Date
- Section markers (optional): "Q&A", "Questions and Answers"

## Project Structure

```
earnings-call-analyzer/
├── cli.py                    # Command-line interface
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── core/
│   │   └── transcript_processor.py  # Text preprocessing
│   ├── analysis/
│   │   ├── sentiment/       # Sentiment analysis modules
│   │   ├── complexity/      # Complexity analysis
│   │   ├── numerical/       # Numerical content analysis
│   │   └── aggregator.py    # Main analysis orchestrator
│   ├── models/
│   │   └── ollama_client.py # LLM integration
│   └── utils/
│       └── text_utils.py    # Text processing utilities
├── data/
│   ├── dictionaries/        # LM dictionary files
│   ├── transcripts/         # Sample transcripts
│   └── benchmarks/          # Benchmark data
└── scripts/
    └── download_dictionaries.py  # Dictionary setup
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
SENTIMENT_MODEL=llama3.1:8b
CONTEXTUALIZATION_MODEL=llama3.1:8b

# Analysis Settings
HYBRID_SENTIMENT_WEIGHT_LEXICON=0.3
HYBRID_SENTIMENT_WEIGHT_LLM=0.7
```

### Changing Models

Edit `config/settings.py` or set environment variables:

```bash
export SENTIMENT_MODEL=mistral
export CONTEXTUALIZATION_MODEL=llama3.1:70b
```

## Output Format

Analysis results are saved in JSON format:

```json
{
  "timestamp": "2024-10-04T10:30:00",
  "company_name": "Apple Inc.",
  "quarter": "Q4",
  "year": 2024,
  "overall_sentiment": {
    "hybrid_sentiment_score": 0.45,
    "hybrid_label": "Positive",
    "confidence": 0.85
  },
  "overall_complexity": {
    "composite_score": 58.3,
    "complexity_level": "Moderate"
  },
  "overall_numerical": {
    "numeric_transparency_score": 2.67,
    "vs_sp500_benchmark": "above"
  },
  "red_flags": [...],
  "strengths": [...],
  "key_findings": [...]
}
```

## Performance

### Processing Times (approximate)
- Small transcript (1,000 words): ~30 seconds
- Medium transcript (5,000 words): ~1-2 minutes
- Large transcript (10,000 words): ~2-3 minutes

### Speed Optimization
1. Use `--no-llm` flag for 3-5x faster analysis
2. Use smaller Ollama models (phi3 vs llama3.1:70b)
3. Adjust `LLM_CHUNK_SIZE` in settings

## Benchmarks

The platform uses S&P 500 Q4 2024 benchmarks from S&P Global:

- **Net Positivity**: 1.22%
- **Numeric Transparency**: 2.22%
- **Sector-specific** benchmarks available in `config/settings.py`

## Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama"**
   ```bash
   # Make sure Ollama is running
   ollama serve
   ```

2. **"Missing dictionaries"**
   ```bash
   python scripts/download_dictionaries.py --create-starter
   ```

3. **"Model not found"**
   ```bash
   ollama pull llama3.1:8b
   ```

4. **Slow analysis**
   - Use `--no-llm` flag
   - Switch to smaller model
   - Reduce chunk size in settings

### Getting Help

Run the setup checker:
```bash
python cli.py check-setup
```

## Development Roadmap

### Phase 1 (Current) ✓
- Core sentiment, complexity, and numerical analysis
- Ollama LLM integration
- CLI interface
- Basic reporting

### Phase 2 (Planned)
- Deception detection
- Q&A dynamics analysis
- Temporal focus metrics
- Lexical diversity
- Historical trend analysis

### Phase 3 (Planned)
- Web-based dashboard
- Interactive visualizations
- PDF report generation
- Batch processing

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

[Specify license]

## Citation

If you use this platform in research, please cite:

```bibtex
@software{earnings_call_analyzer,
  title={Earnings Call Analysis Platform},
  author={[Your Name]},
  year={2025},
  url={[Repository URL]}
}
```

## References

- Loughran, T., & McDonald, B. (2011). When is a Liability not a Liability? Textual Analysis, Dictionaries, and 10-Ks
- S&P Global Market Intelligence. (2024). Analyzing Sentiment in Quarterly Earnings Calls
- Larcker & Zakolyukina (2012). Detecting Deceptive Discussions in Conference Calls

## Contact

[Your contact information]
