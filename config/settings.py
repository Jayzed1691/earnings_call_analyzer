"""
Configuration management for Earnings Call Analyzer
"""
from pathlib import Path
from typing import Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml


class Settings(BaseSettings):
    """Application settings"""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DICTIONARIES_DIR: Path = DATA_DIR / "dictionaries"
    BENCHMARKS_DIR: Path = DATA_DIR / "benchmarks"
    TRANSCRIPTS_DIR: Path = DATA_DIR / "transcripts"
    
    # Ollama settings
    OLLAMA_HOST: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    SENTIMENT_MODEL: str = Field(default="llama3.1:8b", env="SENTIMENT_MODEL")
    CONTEXTUALIZATION_MODEL: str = Field(default="llama3.1:8b", env="CONTEXTUALIZATION_MODEL")
    OLLAMA_TIMEOUT: int = Field(default=120, env="OLLAMA_TIMEOUT")
    
    # Analysis settings
    HYBRID_SENTIMENT_WEIGHT_LEXICON: float = 0.3
    HYBRID_SENTIMENT_WEIGHT_LLM: float = 0.7
    MIN_TRANSCRIPT_LENGTH: int = 100  # minimum words
    MAX_TRANSCRIPT_LENGTH: int = 50000  # maximum words
    
    # LLM settings
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 500
    LLM_CHUNK_SIZE: int = 512
    LLM_CHUNK_OVERLAP: int = 128
    
    # Syllable counting
    SYLLABLE_EXCEPTIONS: Dict[str, int] = {
        "business": 2,
        "interest": 2,
        "chocolate": 2,
    }
    
    # Benchmarks (S&P 500 Q4 2024 from PRD)
    SP500_NET_POSITIVITY: float = 1.22
    SP500_NUMERIC_TRANSPARENCY: float = 2.22
    SP500_EVASIVENESS_BASELINE: float = 11.0
    
    # Sector benchmarks (GICS)
    SECTOR_NUMERIC_TRANSPARENCY: Dict[str, float] = {
        "Utilities": 2.61,
        "Energy": 2.45,
        "Financials": 2.38,
        "Industrials": 2.25,
        "Materials": 2.18,
        "Information Technology": 2.15,
        "Health Care": 2.08,
        "Consumer Discretionary": 1.98,
        "Communication Services": 1.87,
        "Real Estate": 1.85,
        "Consumer Staples": 1.76,
    }
    
    # Alert thresholds
    COMPLEXITY_ALERT_THRESHOLD: int = 70  # Composite score
    DECEPTION_RISK_CRITICAL: int = 70
    DECEPTION_RISK_WARNING: int = 50
    EVASIVENESS_ALERT: float = 15.0
    QUESTION_AVOIDANCE_ALERT: float = 40.0
    
    # Report settings
    REPORT_HISTORICAL_QUARTERS: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def load_model_config() -> Dict[str, Any]:
    """Load model configurations from YAML"""
    config_path = Path(__file__).parent / "models.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


# Global settings instance
settings = Settings()
