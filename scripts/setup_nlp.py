#!/usr/bin/env python3
"""
Setup script for NLP enhancements
Handles dictionary processing and configuration file setup
"""
import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


def create_nlp_config_directory():
    """Create NLP configuration directory structure"""
    nlp_config_dir = settings.DATA_DIR / "nlp_config"
    nlp_config_dir.mkdir(parents=True, exist_ok=True)
    return nlp_config_dir


def create_financial_phrases_config(output_dir: Path):
    """Create default financial phrases configuration"""
    phrases = {
        "description": "Multi-word financial and accounting phrases for earnings call analysis",
        "version": "1.0",
        "phrases": [
            # Core financial metrics
            "earnings per share", "eps", "diluted eps", "basic eps",
            "return on equity", "roe", "return on assets", "roa",
            "return on investment", "roi", "return on capital", "roic",
            
            # Margins
            "gross margin", "gross profit margin", "operating margin",
            "operating profit margin", "net margin", "net profit margin",
            "ebitda margin",
            
            # Income metrics
            "operating income", "net income", "gross profit", "net profit",
            "operating profit", "pre tax income", "after tax income",
            
            # Cash flow
            "operating cash flow", "free cash flow", "cash flow from operations",
            "cash flow from investing", "cash flow from financing",
            
            # Balance sheet
            "working capital", "net working capital", "current ratio",
            "quick ratio", "debt to equity", "debt to equity ratio",
            
            # Growth metrics
            "revenue growth", "sales growth", "top line growth",
            "bottom line growth", "organic growth", "year over year",
            "year on year", "yoy", "quarter over quarter", "qoq",
            "sequential growth", "same store sales", "comparable store sales",
            "comp store sales",
            
            # Financial statements
            "balance sheet", "income statement", "cash flow statement",
            "statement of cash flows", "statement of operations",
            
            # Customer metrics
            "market share", "customer acquisition", "customer acquisition cost",
            "customer retention", "retention rate", "churn rate",
            "average revenue per user", "arpu", "monthly active users", "mau",
            "daily active users", "dau", "lifetime value", "ltv",
            "customer lifetime value",
            
            # Guidance
            "forward guidance", "full year guidance", "annual guidance",
            "quarterly guidance", "fiscal year", "fiscal quarter",
            "earnings guidance", "revenue guidance",
            
            # Accounting
            "generally accepted accounting principles", "gaap", "non gaap",
            "adjusted earnings", "adjusted ebitda", "adjusted operating income",
            "earnings before interest and tax", "ebit", "ebitda",
            "stock based compensation", "share based compensation",
            "deferred revenue", "accrued expenses", "accounts receivable",
            "accounts payable",
            
            # Corporate actions
            "share repurchase", "share buyback", "stock buyback",
            "dividend payment", "dividend yield", "capital allocation",
            "capital expenditure", "capex",
            
            # Operations
            "research and development", "r and d", "r&d",
            "sales and marketing", "s&m", "general and administrative", "g&a",
            "cost of goods sold", "cogs", "cost of revenue", "cost of sales",
            "selling general and administrative", "sg&a",
            "operating expenses", "one time charges", "restructuring charges",
            
            # Market/strategy
            "market conditions", "competitive landscape", "industry trends",
            "macroeconomic environment", "economic conditions",
            "business model", "business strategy", "growth strategy",
            "go to market strategy", "pricing power", "product mix",
            "revenue mix", "business segment", "operating segment",
            
            # Operational
            "operational efficiency", "operational excellence",
            "productivity improvement", "cost reduction", "cost savings",
            "margin expansion", "margin compression",
            
            # Strategic
            "strategic initiative", "growth driver", "value driver",
            "total addressable market", "tam", "market opportunity",
            "strategic acquisition", "strategic partnership",
            "competitive advantage", "barriers to entry", "network effects"
        ]
    }
    
    output_file = output_dir / "financial_phrases.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(phrases, f, indent=2)
    
    print(f"✓ Created financial_phrases.json ({len(phrases['phrases'])} phrases)")
    return output_file


def create_stopwords_config(output_dir: Path):
    """Create custom stopwords configuration"""
    config = {
        "description": "Custom stopword configuration for financial earnings call analysis",
        "version": "1.0",
        "preserve": [
            # Negations - CRITICAL for sentiment
            "not", "no", "nor", "neither", "never", "none", "nobody",
            "nothing", "nowhere",
            
            # Directional/comparative - important for analysis
            "up", "down", "above", "below", "over", "under",
            "more", "less", "most", "least",
            "very", "too",
            
            # Temporal - important for context
            "against", "before", "after", "during", "until",
            
            # Sentiment-bearing
            "positive", "negative", "good", "bad", "better", "worse",
            "best", "worst", "strong", "stronger", "strongest",
            "weak", "weaker", "weakest", "high", "higher", "highest",
            "low", "lower", "lowest",
            
            # Change verbs - critical for earnings calls
            "increase", "increased", "increasing", "decrease", "decreased",
            "decreasing", "improve", "improved", "improving",
            "decline", "declined", "declining", "growth", "grow", "growing"
        ],
        "financial": [
            # Common but low-value words in earnings calls
            "quarter", "quarters", "year", "years", "fiscal", "period", "periods",
            "company", "companies", "business", "businesses",
            "call", "calls", "today", "discussion", "presentation",
            "slide", "slides", "comment", "comments",
            "question", "questions", "answer", "answers",
            "thank", "thanks", "please", "appreciate"
        ]
    }
    
    output_file = output_dir / "custom_stopwords.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created custom_stopwords.json")
    print(f"  - {len(config['preserve'])} words preserved from stopword removal")
    print(f"  - {len(config['financial'])} financial filler words to remove")
    return output_file


def setup_nlp_enhancements(create_configs: bool = True):
    """
    Complete NLP enhancement setup
    
    Args:
        create_configs: Whether to create config files
    """
    print("\n" + "="*80)
    print("NLP ENHANCEMENTS SETUP")
    print("="*80 + "\n")
    
    # Create configuration directory
    print("1. Creating NLP configuration directory...")
    nlp_config_dir = create_nlp_config_directory()
    print(f"   ✓ Created: {nlp_config_dir}\n")
    
    if create_configs:
        # Create financial phrases config
        print("2. Creating financial phrases configuration...")
        phrases_file = create_financial_phrases_config(nlp_config_dir)
        print()
        
        # Create stopwords config
        print("3. Creating custom stopwords configuration...")
        stopwords_file = create_stopwords_config(nlp_config_dir)
        print()
    
    # Instructions for dictionary processing
    print("4. Loughran-McDonald Dictionary Setup")
    print("   " + "-"*76)
    print("   To use the full LM Master Dictionary:")
    print()
    print("   a) Download from: https://sraf.nd.edu/loughranmcdonald-master-dictionary/")
    print("   b) Process the file:")
    print("      python scripts/download_dictionaries.py --process /path/to/LM_Dictionary.csv")
    print()
    print("   OR for testing, create starter dictionaries:")
    print("      python scripts/download_dictionaries.py --create-starter")
    print()
    
    # Instructions for spaCy
    print("5. spaCy Model Setup (for Named Entity Recognition)")
    print("   " + "-"*76)
    print("   Download the English model:")
    print("      python -m spacy download en_core_web_sm")
    print()
    
    # Instructions for NLTK
    print("6. NLTK Data Setup (for lemmatization)")
    print("   " + "-"*76)
    print("   Download required data:")
    print("      python -c \"import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')\"")
    print()
    
    print("="*80)
    print("✓ NLP Enhancement setup complete!")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. Process the LM Master Dictionary (if you have it)")
    print("  2. Install spaCy model: python -m spacy download en_core_web_sm")
    print("  3. Download NLTK data as shown above")
    print("  4. Review and customize config files in:", nlp_config_dir)
    print()


def verify_setup():
    """Verify NLP enhancement setup"""
    print("\n" + "="*80)
    print("VERIFYING NLP ENHANCEMENTS")
    print("="*80 + "\n")
    
    issues = []
    
    # Check config directory
    nlp_config_dir = settings.DATA_DIR / "nlp_config"
    if nlp_config_dir.exists():
        print("✓ NLP config directory exists")
    else:
        print("❌ NLP config directory not found")
        issues.append("Config directory missing")
    
    # Check config files
    phrases_file = nlp_config_dir / "financial_phrases.json"
    stopwords_file = nlp_config_dir / "custom_stopwords.json"
    
    if phrases_file.exists():
        print("✓ Financial phrases config exists")
    else:
        print("⚠️  Financial phrases config not found (will use defaults)")
    
    if stopwords_file.exists():
        print("✓ Custom stopwords config exists")
    else:
        print("⚠️  Custom stopwords config not found (will use defaults)")
    
    # Check spaCy
    print("\nChecking spaCy...")
    try:
        import spacy
        try:
            nlp = spacy.load('en_core_web_sm')
            print("✓ spaCy model 'en_core_web_sm' installed")
        except OSError:
            print("❌ spaCy model 'en_core_web_sm' not found")
            print("   Install with: python -m spacy download en_core_web_sm")
            issues.append("spaCy model missing")
    except ImportError:
        print("❌ spaCy not installed")
        issues.append("spaCy not installed")
    
    # Check NLTK
    print("\nChecking NLTK data...")
    try:
        import nltk
        try:
            nltk.data.find('corpora/wordnet')
            print("✓ NLTK WordNet data installed")
        except LookupError:
            print("❌ NLTK WordNet data not found")
            issues.append("NLTK WordNet missing")
    except ImportError:
        print("❌ NLTK not installed")
        issues.append("NLTK not installed")
    
    # Check LM dictionaries
    print("\nChecking Loughran-McDonald dictionaries...")
    dict_dir = settings.DICTIONARIES_DIR / "loughran_mcdonald"
    if dict_dir.exists():
        dict_files = list(dict_dir.glob("*.txt"))
        if len(dict_files) >= 7:
            print(f"✓ Found {len(dict_files)} dictionary files")
        else:
            print(f"⚠️  Only {len(dict_files)}/7 dictionary files found")
            issues.append("Incomplete LM dictionaries")
    else:
        print("❌ LM dictionary directory not found")
        issues.append("LM dictionaries missing")
    
    # Summary
    print("\n" + "="*80)
    if issues:
        print(f"⚠️  Setup incomplete - {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✓ All NLP enhancements properly configured!")
    print("="*80 + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup NLP enhancements')
    parser.add_argument('--create-configs', action='store_true',
                       help='Create configuration files')
    parser.add_argument('--verify', action='store_true',
                       help='Verify setup is complete')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_setup()
    elif args.create_configs:
        setup_nlp_enhancements(create_configs=True)
    else:
        print("NLP Enhancement Setup Tool")
        print("=" * 80)
        print("\nOptions:")
        print("  --create-configs : Create configuration files")
        print("  --verify        : Verify installation")
        print("\nExample:")
        print("  python scripts/setup_nlp.py --create-configs")
        print("  python scripts/setup_nlp.py --verify")
        print()
