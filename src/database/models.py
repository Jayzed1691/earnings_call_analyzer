"""
SQLAlchemy ORM Models for Earnings Call Analyzer

Defines database schema for:
- Companies (company metadata)
- AnalysisResults (comprehensive analysis data)
- Benchmarks (sector/industry benchmarks)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Company(Base):
    """Company entity - stores metadata about analyzed companies"""
    
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    ticker = Column(String(10), unique=True, index=True)
    sector = Column(String(100))
    industry = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    analyses = relationship(
        "AnalysisResult",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', ticker='{self.ticker}')>"


class AnalysisResult(Base):
    """
    Analysis result entity - stores comprehensive analysis for a company's earnings call
    
    Includes all metrics from:
    - Phase 1: Sentiment, Complexity, Numerical analysis
    - Phase 2A: Deception detection, Evasiveness, Q&A analysis
    """
    
    __tablename__ = 'analysis_results'
    
    # Primary key and foreign keys
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    
    # Time period
    quarter = Column(String(2), nullable=False)  # Q1, Q2, Q3, Q4
    year = Column(Integer, nullable=False)
    analysis_date = Column(DateTime, nullable=False, default=datetime.now)
    
    # === SENTIMENT METRICS (Phase 1) ===
    hybrid_sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    lexicon_net_positivity = Column(Float)
    llm_sentiment_score = Column(Float)
    
    # === COMPLEXITY METRICS (Phase 1) ===
    complexity_composite_score = Column(Float)
    complexity_level = Column(String(20))
    flesch_reading_ease = Column(Float)
    flesch_kincaid_grade = Column(Float)
    gunning_fog_index = Column(Float)
    smog_index = Column(Float)
    coleman_liau_index = Column(Float)
    
    # === NUMERICAL METRICS (Phase 1) ===
    numeric_transparency_score = Column(Float)
    numerical_specificity_index = Column(Float)
    forward_looking_density = Column(Float)
    backward_looking_density = Column(Float)
    forward_to_backward_ratio = Column(Float)
    contextualization_quality_score = Column(Float)
    vs_sp500_benchmark = Column(String(10))  # above, at, below
    
    # === DECEPTION METRICS (Phase 2A) ===
    deception_risk_score = Column(Float)
    deception_risk_level = Column(String(20))
    deception_confidence = Column(Float)
    
    # Linguistic markers
    hedging_density = Column(Float)
    qualifier_density = Column(Float)
    passive_voice_percentage = Column(Float)
    pronoun_distancing_percentage = Column(Float)
    
    # === EVASIVENESS METRICS (Phase 2A) ===
    evasiveness_score = Column(Float)
    evasiveness_level = Column(String(20))
    evasiveness_vs_baseline = Column(String(10))  # above, at, below
    
    # === COUNTS ===
    word_count = Column(Integer)
    sentence_count = Column(Integer)
    
    # === STORAGE FOR DETAILED DATA ===
    # Full results as JSON (contains all nested data structures)
    full_results_json = Column(JSON)
    
    # Key text findings (for quick access without parsing JSON)
    key_findings = Column(Text)  # Newline-separated insights
    red_flags = Column(Text)     # Newline-separated red flags
    strengths = Column(Text)     # Newline-separated strengths
    
    # Relationships
    company = relationship("Company", back_populates="analyses")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_company_quarter', 'company_id', 'year', 'quarter'),
        Index('idx_analysis_date', 'analysis_date'),
    )
    
    def __repr__(self):
        return (f"<AnalysisResult(id={self.id}, "
                f"company_id={self.company_id}, "
                f"quarter='{self.quarter}', year={self.year})>")


class Benchmark(Base):
    """
    Benchmark entity - stores sector/industry benchmark values
    
    Used for comparative analysis against S&P 500, sector averages, etc.
    """
    
    __tablename__ = 'benchmarks'
    
    id = Column(Integer, primary_key=True)
    sector = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    
    # Optional time period (None = general benchmark)
    quarter = Column(String(2))
    year = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Indexes for efficient lookups
    __table_args__ = (
        Index('idx_sector_metric', 'sector', 'metric_name'),
        Index('idx_sector_time', 'sector', 'year', 'quarter'),
    )
    
    def __repr__(self):
        return (f"<Benchmark(sector='{self.sector}', "
                f"metric='{self.metric_name}', value={self.value})>")
