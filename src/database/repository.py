"""
Database Repository - Data Access Layer

Provides high-level interface for:
- Saving and retrieving analysis results
- Company management
- Historical data queries
- Sector benchmarking
- Peer comparison
"""

from sqlalchemy import create_engine, and_, or_, func, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager
import statistics
import json
from dataclasses import asdict

from src.database.models import Base, Company, AnalysisResult, Benchmark


class DatabaseRepository:
    """
    Repository pattern implementation for database operations
    
    Handles all database interactions with proper session management
    and error handling.
    """
    
    def __init__(self, database_url: str):
        """
        Initialize database repository
        
        Args:
            database_url: SQLAlchemy database URL
                Examples:
                - "sqlite:///./data/earnings_analyzer.db"
                - "postgresql://user:pass@localhost/earnings"
        """
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def _get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions with automatic commit/rollback

        Usage:
            with repository.get_session() as session:
                company = session.query(Company).filter_by(ticker='AAPL').first()
                # Session automatically commits on success or rolls back on error

        Yields:
            Session: Database session
        """
        session = self._get_session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    # ===== COMPANY OPERATIONS =====
    
    def save_company(
        self,
        name: str,
        ticker: str,
        sector: Optional[str] = None,
        industry: Optional[str] = None
    ) -> int:
        """
        Save or update a company

        Args:
            name: Company name
            ticker: Stock ticker symbol
            sector: Industry sector (optional)
            industry: Specific industry (optional)

        Returns:
            Company ID
        """
        with self.get_session() as session:
            # Check if company exists
            company = session.query(Company).filter_by(name=name).first()

            if company:
                # Update existing
                company.ticker = ticker
                if sector:
                    company.sector = sector
                if industry:
                    company.industry = industry
            else:
                # Create new
                company = Company(
                    name=name,
                    ticker=ticker,
                    sector=sector,
                    industry=industry
                )
                session.add(company)

            # Flush to get the ID before commit
            session.flush()
            return company.id
    
    def get_company(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None
    ) -> Optional[Company]:
        """
        Get company by name or ticker
        
        Args:
            name: Company name (optional)
            ticker: Stock ticker (optional)
            
        Returns:
            Company object or None
        """
        session = self._get_session()
        try:
            if name:
                return session.query(Company).filter_by(name=name).first()
            elif ticker:
                return session.query(Company).filter_by(ticker=ticker).first()
            return None
        finally:
            session.close()
    
    def get_all_companies(self) -> List[Company]:
        """Get all companies in database"""
        session = self._get_session()
        try:
            return session.query(Company).all()
        finally:
            session.close()
    
    def search_companies(self, query: str) -> List[Company]:
        """
        Search companies by name or ticker
        
        Args:
            query: Search term
            
        Returns:
            List of matching companies
        """
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
    
    def get_sector_companies(self, sector: str) -> List[Company]:
        """Get all companies in a sector"""
        session = self._get_session()
        try:
            return session.query(Company).filter_by(sector=sector).all()
        finally:
            session.close()
    
    # ===== ANALYSIS OPERATIONS =====
    
    def save_analysis(
        self,
        company_name: str,
        quarter: str,
        year: int,
        analysis_result: Any  # ComprehensiveAnalysisResult dataclass
    ) -> int:
        """
        Save comprehensive analysis result to database
        
        Args:
            company_name: Name of the company
            quarter: Quarter (Q1, Q2, Q3, Q4)
            year: Year (e.g., 2024)
            analysis_result: ComprehensiveAnalysisResult object
            
        Returns:
            Analysis ID
        """
        session = self._get_session()
        try:
            # Get or create company
            company = session.query(Company).filter_by(name=company_name).first()
            if not company:
                # Create company with minimal info
                company = Company(name=company_name, ticker="UNKNOWN")
                session.add(company)
                session.flush()
            
            # Check if analysis already exists for this quarter
            existing = session.query(AnalysisResult).filter(
                and_(
                    AnalysisResult.company_id == company.id,
                    AnalysisResult.quarter == quarter,
                    AnalysisResult.year == year
                )
            ).first()
            
            # Convert dataclass to dict
            result_dict = asdict(analysis_result)
            
            # Extract key findings as text
            key_findings = "\n".join(result_dict.get('insights', {}).get('key_findings', []))
            red_flags = "\n".join(result_dict.get('insights', {}).get('red_flags', []))
            strengths = "\n".join(result_dict.get('insights', {}).get('strengths', []))
            
            if existing:
                # Update existing analysis
                analysis = existing
            else:
                # Create new analysis
                analysis = AnalysisResult(
                    company_id=company.id,
                    quarter=quarter,
                    year=year
                )
                session.add(analysis)
            
            # Populate sentiment metrics
            if 'sentiment' in result_dict:
                sent = result_dict['sentiment']
                analysis.hybrid_sentiment_score = sent.get('hybrid_score')
                analysis.sentiment_label = sent.get('label')
                if 'lexicon' in sent:
                    analysis.lexicon_net_positivity = sent['lexicon'].get('net_positivity')
                if 'llm' in sent:
                    analysis.llm_sentiment_score = sent['llm'].get('score')
            
            # Populate complexity metrics
            if 'complexity' in result_dict:
                comp = result_dict['complexity']
                analysis.complexity_composite_score = comp.get('composite_score')
                analysis.complexity_level = comp.get('complexity_level')
                if 'metrics' in comp:
                    metrics = comp['metrics']
                    analysis.flesch_reading_ease = metrics.get('flesch_reading_ease')
                    analysis.flesch_kincaid_grade = metrics.get('flesch_kincaid_grade')
                    analysis.gunning_fog_index = metrics.get('gunning_fog_index')
                    analysis.smog_index = metrics.get('smog_index')
                    analysis.coleman_liau_index = metrics.get('coleman_liau_index')
            
            # Populate numerical metrics
            if 'numerical' in result_dict:
                num = result_dict['numerical']
                analysis.numeric_transparency_score = num.get('transparency_score')
                analysis.numerical_specificity_index = num.get('specificity_index')
                analysis.forward_looking_density = num.get('forward_looking_density')
                analysis.backward_looking_density = num.get('backward_looking_density')
                analysis.forward_to_backward_ratio = num.get('forward_to_backward_ratio')
                analysis.contextualization_quality_score = num.get('contextualization_quality')
                analysis.vs_sp500_benchmark = num.get('vs_sp500_benchmark')
            
            # Populate deception metrics (Phase 2A)
            if 'deception_risk' in result_dict:
                dec = result_dict['deception_risk']
                analysis.deception_risk_score = dec.get('overall_risk_score')
                analysis.deception_risk_level = dec.get('risk_level')
                analysis.deception_confidence = dec.get('confidence')
                
                if 'linguistic_markers' in dec:
                    ling = dec['linguistic_markers']
                    analysis.hedging_density = ling.get('hedging_density')
                    analysis.qualifier_density = ling.get('qualifier_density')
                    analysis.passive_voice_percentage = ling.get('passive_voice_percentage')
                    analysis.pronoun_distancing_percentage = ling.get('pronoun_distancing_percentage')
            
            # Populate evasiveness metrics (Phase 2A)
            if 'evasiveness' in result_dict:
                evas = result_dict['evasiveness']
                analysis.evasiveness_score = evas.get('overall_score')
                analysis.evasiveness_level = evas.get('level')
                analysis.evasiveness_vs_baseline = evas.get('vs_baseline')
            
            # Word and sentence counts
            analysis.word_count = result_dict.get('word_count')
            analysis.sentence_count = result_dict.get('sentence_count')
            
            # Store full results as JSON
            analysis.full_results_json = result_dict
            
            # Store text findings
            analysis.key_findings = key_findings
            analysis.red_flags = red_flags
            analysis.strengths = strengths
            
            session.commit()
            return analysis.id
        finally:
            session.close()
    
    def load_analysis(
        self,
        company_name: str,
        quarter: str,
        year: int
    ) -> Optional[AnalysisResult]:
        """
        Load a specific analysis
        
        Args:
            company_name: Company name
            quarter: Quarter (Q1, Q2, Q3, Q4)
            year: Year
            
        Returns:
            AnalysisResult or None
        """
        session = self._get_session()
        try:
            company = session.query(Company).filter_by(name=company_name).first()
            if not company:
                return None
            
            analysis = session.query(AnalysisResult).filter(
                and_(
                    AnalysisResult.company_id == company.id,
                    AnalysisResult.quarter == quarter,
                    AnalysisResult.year == year
                )
            ).first()
            
            return analysis
        finally:
            session.close()
    
    def load_historical_analyses(
        self,
        company_name: str,
        quarters: int = 4
    ) -> List[AnalysisResult]:
        """
        Load historical analyses for a company
        
        Args:
            company_name: Company name
            quarters: Number of recent quarters to load
            
        Returns:
            List of AnalysisResult objects (most recent first)
        """
        session = self._get_session()
        try:
            company = session.query(Company).filter_by(name=company_name).first()
            if not company:
                return []
            
            analyses = session.query(AnalysisResult)\
                .filter_by(company_id=company.id)\
                .order_by(desc(AnalysisResult.year), desc(AnalysisResult.quarter))\
                .limit(quarters)\
                .all()
            
            return analyses
        finally:
            session.close()
    
    def get_latest_analysis(self, company_name: str) -> Optional[AnalysisResult]:
        """
        Get most recent analysis for a company
        
        Args:
            company_name: Company name
            
        Returns:
            Most recent AnalysisResult or None
        """
        analyses = self.load_historical_analyses(company_name, quarters=1)
        return analyses[0] if analyses else None
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """
        Delete analysis by ID
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            True if deleted, False if not found
        """
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
    
    # ===== SECTOR/PEER OPERATIONS =====
    
    def calculate_sector_benchmark(
        self,
        sector: str,
        metric_name: str,
        quarter: str,
        year: int
    ) -> Dict[str, Any]:
        """
        Calculate sector benchmark statistics for a metric
        
        Args:
            sector: Sector name
            metric_name: Name of metric column (e.g., 'hybrid_sentiment_score')
            quarter: Quarter (Q1, Q2, Q3, Q4)
            year: Year
            
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
        """
        Get analyses for multiple companies in same quarter
        
        Args:
            company_names: List of company names
            quarter: Quarter (Q1, Q2, Q3, Q4)
            year: Year
            
        Returns:
            List of AnalysisResult objects
        """
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
    
    # ===== BENCHMARK OPERATIONS =====
    
    def save_benchmark(
        self,
        sector: str,
        metric_name: str,
        value: float,
        quarter: Optional[str] = None,
        year: Optional[int] = None
    ) -> int:
        """
        Save sector benchmark
        
        Args:
            sector: Sector name (e.g., "Technology", "S&P 500")
            metric_name: Metric name (e.g., "net_positivity")
            value: Benchmark value
            quarter: Optional quarter
            year: Optional year
            
        Returns:
            Benchmark ID
        """
        session = self._get_session()
        try:
            # Check if benchmark exists
            query = session.query(Benchmark)\
                .filter_by(sector=sector, metric_name=metric_name)
            
            if quarter:
                query = query.filter_by(quarter=quarter)
            if year:
                query = query.filter_by(year=year)
            
            benchmark = query.first()
            
            if benchmark:
                # Update existing
                benchmark.value = value
                benchmark.updated_at = datetime.now()
            else:
                # Create new
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
        """
        Get benchmark value
        
        Args:
            sector: Sector name
            metric_name: Metric name
            quarter: Optional quarter
            year: Optional year
            
        Returns:
            Benchmark object or None
        """
        session = self._get_session()
        try:
            query = session.query(Benchmark)\
                .filter_by(sector=sector, metric_name=metric_name)
            
            if quarter and year:
                query = query.filter_by(quarter=quarter, year=year)
            
            return query.first()
        finally:
            session.close()
    
    def get_all_benchmarks(self, sector: Optional[str] = None) -> List[Benchmark]:
        """
        Get all benchmarks, optionally filtered by sector
        
        Args:
            sector: Optional sector filter
            
        Returns:
            List of Benchmark objects
        """
        session = self._get_session()
        try:
            query = session.query(Benchmark)
            if sector:
                query = query.filter_by(sector=sector)
            return query.all()
        finally:
            session.close()
    
    # ===== UTILITY METHODS =====
    
    def get_database_stats(self) -> Dict[str, int]:
        """
        Get database statistics
        
        Returns:
            Dict with counts of companies, analyses, benchmarks
        """
        session = self._get_session()
        try:
            return {
                'companies': session.query(Company).count(),
                'analyses': session.query(AnalysisResult).count(),
                'benchmarks': session.query(Benchmark).count()
            }
        finally:
            session.close()
    
    def clear_all_data(self) -> None:
        """
        DANGER: Clear all data from database
        
        Use only for testing or reset purposes
        """
        session = self._get_session()
        try:
            session.query(AnalysisResult).delete()
            session.query(Company).delete()
            session.query(Benchmark).delete()
            session.commit()
        finally:
            session.close()
