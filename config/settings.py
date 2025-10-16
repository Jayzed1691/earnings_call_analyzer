"""
Configuration settings for Earnings Call Analyzer
Phase 2 Enhanced - Includes database, API, and advanced analysis settings
"""
from pathlib import Path
from typing import Dict


class Settings:
    """Application settings and configuration"""
    
    # ===== PROJECT PATHS =====
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DICTIONARIES_DIR: Path = DATA_DIR / "dictionaries"
    CACHE_DIR: Path = DATA_DIR / "cache"
    
    # ===== PHASE 2: DATABASE =====
    DATABASE_PATH: Path = DATA_DIR / "earnings_analyzer.db"
    DATABASE_URL: str = f"sqlite:///{DATA_DIR}/earnings_analyzer.db"
    
    # ===== PHASE 2: API CONFIGURATION =====
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_TITLE: str = "Earnings Call Analyzer API"
    API_VERSION: str = "2.0.0"
    
    # ===== OLLAMA LLM CONFIGURATION =====
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 120
    
    # LLM Models
    SENTIMENT_MODEL: str = "llama3.1:8b"
    CONTEXTUALIZATION_MODEL: str = "llama3.1:8b"
    
    # LLM Parameters
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2048
    LLM_CHUNK_SIZE: int = 512
    LLM_CHUNK_OVERLAP: int = 128
    
    # ===== PHASE 2: FEATURE FLAGS =====
    ENABLE_DECEPTION_ANALYSIS: bool = True
    ENABLE_EVASIVENESS_ANALYSIS: bool = True
    ENABLE_QA_ANALYSIS: bool = True
    ENABLE_HISTORICAL_TRACKING: bool = True
    ENABLE_PDF_REPORTS: bool = True
    ENABLE_HTML_DASHBOARDS: bool = True
    ENABLE_EXCEL_EXPORTS: bool = True
    
    # ===== TRANSCRIPT VALIDATION =====
    MIN_TRANSCRIPT_LENGTH: int = 500  # words
    MAX_TRANSCRIPT_LENGTH: int = 50000  # words
    
    # ===== SENTIMENT ANALYSIS =====
    # Hybrid sentiment weighting (must sum to 1.0)
    HYBRID_SENTIMENT_WEIGHT_LEXICON: float = 0.3
    HYBRID_SENTIMENT_WEIGHT_LLM: float = 0.7
    
    # S&P 500 Benchmarks
    SP500_NET_POSITIVITY: float = 15.0  # LM Net Positivity benchmark
    
    # ===== COMPLEXITY ANALYSIS =====
    # Syllable count exceptions for common financial terms
    SYLLABLE_EXCEPTIONS: Dict[str, int] = {
        'ebitda': 4,
        'revenue': 3,
        'guidance': 2,
        'fiscal': 2,
        'quarter': 2,
    }
    
    # ===== NUMERICAL ANALYSIS =====
    # S&P 500 Benchmarks
    SP500_NUMERIC_TRANSPARENCY: float = 3.5  # Percentage of words that are numbers
    
    # ===== PHASE 2: DECEPTION DETECTION =====
    # Risk Level Thresholds (0-100 scale)
    DECEPTION_RISK_WARNING: int = 50  # High risk threshold
    DECEPTION_RISK_CRITICAL: int = 70  # Critical risk threshold
    
    # Component Weights for Overall Risk Score
    DECEPTION_WEIGHT_LINGUISTIC: float = 0.25
    DECEPTION_WEIGHT_BEHAVIORAL: float = 0.25
    DECEPTION_WEIGHT_NUMERICAL: float = 0.30
    DECEPTION_WEIGHT_EVASION: float = 0.20
    
    # Individual Indicator Thresholds
    HEDGING_DENSITY_THRESHOLD: float = 15.0  # % of words
    QUALIFIER_DENSITY_THRESHOLD: float = 10.0  # % of words
    PASSIVE_VOICE_THRESHOLD: float = 30.0  # % of verb phrases
    PRONOUN_DISTANCING_THRESHOLD: float = 40.0  # distancing score
    
    # ===== PHASE 2: EVASIVENESS ANALYSIS =====
    # S&P 500 Baseline
    SP500_EVASIVENESS_BASELINE: float = 11.0
    
    # Component Weights for Evasiveness Score
    EVASIVENESS_WEIGHT_QUALIFIER: float = 0.25
    EVASIVENESS_WEIGHT_HEDGING: float = 0.25
    EVASIVENESS_WEIGHT_PASSIVE: float = 0.20
    EVASIVENESS_WEIGHT_VAGUE_PRONOUN: float = 0.15
    EVASIVENESS_WEIGHT_DISTANCING: float = 0.15
    
    # ===== PHASE 2: Q&A EVASION DETECTION =====
    QUESTION_AVOIDANCE_ALERT: float = 40.0  # % of questions evaded
    TOPIC_OVERLAP_THRESHOLD: float = 0.3  # Jaccard similarity threshold
    VAGUE_DENSITY_THRESHOLD: float = 0.05  # 5% of words
    
    # ===== PHASE 2: COMPARATIVE ANALYSIS =====
    # Historical Trend Analysis
    DEFAULT_HISTORICAL_QUARTERS: int = 8  # 2 years
    TREND_STRENGTH_THRESHOLD: float = 0.7  # R-squared threshold
    ANOMALY_DETECTION_THRESHOLD: float = 2.0  # Standard deviations
    
    # Peer Comparison
    MIN_PEER_COMPANIES: int = 3
    MAX_PEER_COMPANIES: int = 10
    
    # ===== PHASE 2: REPORTING =====
    # PDF Report Settings
    PDF_PAGE_SIZE: str = "Letter"
    PDF_FONT_FAMILY: str = "Helvetica"
    PDF_FONT_SIZE_BODY: int = 10
    PDF_FONT_SIZE_HEADER: int = 14
    PDF_MARGIN: int = 20  # mm
    
    # HTML Dashboard Settings
    HTML_THEME: str = "bootstrap"
    HTML_CHART_HEIGHT: int = 400
    HTML_CHART_WIDTH: int = 800
    
    # Excel Export Settings
    EXCEL_INCLUDE_CHARTS: bool = True
    EXCEL_INCLUDE_RAW_JSON: bool = True
    
    # ===== LOGGING & DEBUG =====
    LOG_LEVEL: str = "INFO"
    DEBUG_MODE: bool = False
    VERBOSE_OUTPUT: bool = True
    
    # ===== CACHE SETTINGS =====
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600  # seconds (1 hour)
    
    # ===== JOB QUEUE (for API) =====
    MAX_CONCURRENT_JOBS: int = 4
    JOB_TIMEOUT: int = 600  # seconds (10 minutes)
    JOB_CLEANUP_AGE: int = 86400  # seconds (24 hours)
    
    # ===== RATE LIMITING (for API) =====
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # seconds (1 hour)
    
    def __init__(self):
        """Initialize settings and create necessary directories"""
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.DATA_DIR,
            self.DICTIONARIES_DIR,
            self.CACHE_DIR,
            self.DATA_DIR / "reports",
            self.DATA_DIR / "uploads",
            self.DATA_DIR / "nlp_config",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_database_url(self) -> str:
        """Get formatted database URL for SQLAlchemy"""
        return str(self.DATABASE_URL)
    
    def validate_settings(self) -> list:
        """
        Validate configuration settings
        
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        # Validate weights sum to 1.0
        if abs((self.HYBRID_SENTIMENT_WEIGHT_LEXICON + 
                self.HYBRID_SENTIMENT_WEIGHT_LLM) - 1.0) > 0.01:
            warnings.append("Sentiment weights do not sum to 1.0")
        
        deception_weights = (
            self.DECEPTION_WEIGHT_LINGUISTIC +
            self.DECEPTION_WEIGHT_BEHAVIORAL +
            self.DECEPTION_WEIGHT_NUMERICAL +
            self.DECEPTION_WEIGHT_EVASION
        )
        if abs(deception_weights - 1.0) > 0.01:
            warnings.append("Deception component weights do not sum to 1.0")
        
        evasiveness_weights = (
            self.EVASIVENESS_WEIGHT_QUALIFIER +
            self.EVASIVENESS_WEIGHT_HEDGING +
            self.EVASIVENESS_WEIGHT_PASSIVE +
            self.EVASIVENESS_WEIGHT_VAGUE_PRONOUN +
            self.EVASIVENESS_WEIGHT_DISTANCING
        )
        if abs(evasiveness_weights - 1.0) > 0.01:
            warnings.append("Evasiveness component weights do not sum to 1.0")
        
        # Validate threshold ranges
        if not (0 <= self.DECEPTION_RISK_WARNING <= 100):
            warnings.append("DECEPTION_RISK_WARNING must be 0-100")
        
        if not (0 <= self.DECEPTION_RISK_CRITICAL <= 100):
            warnings.append("DECEPTION_RISK_CRITICAL must be 0-100")
        
        if self.DECEPTION_RISK_WARNING >= self.DECEPTION_RISK_CRITICAL:
            warnings.append("DECEPTION_RISK_WARNING must be less than DECEPTION_RISK_CRITICAL")
        
        # Validate API settings
        if not (1 <= self.API_WORKERS <= 16):
            warnings.append("API_WORKERS should be between 1 and 16")
        
        if not (1024 <= self.API_PORT <= 65535):
            warnings.append("API_PORT should be between 1024 and 65535")
        
        return warnings


# Global settings instance
settings = Settings()

# Validate settings on import
_validation_warnings = settings.validate_settings()
if _validation_warnings:
    print("⚠️  Configuration Warnings:")
    for warning in _validation_warnings:
        print(f"   - {warning}")
