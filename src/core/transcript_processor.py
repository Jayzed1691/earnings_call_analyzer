"""
Transcript processing module with input validation
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
from src.utils.text_utils import clean_text, tokenize_sentences, tokenize_words
from config.settings import settings


@dataclass
class TranscriptMetadata:
    """Metadata for a transcript"""
    company_name: Optional[str] = None
    ticker: Optional[str] = None
    quarter: Optional[str] = None
    year: Optional[int] = None
    date: Optional[str] = None
    analyst_firm: Optional[str] = None


@dataclass
class ProcessedTranscript:
    """Processed transcript with metadata"""
    raw_text: str
    cleaned_text: str
    sentences: List[str]
    words: List[str]
    word_count: int
    sentence_count: int
    metadata: TranscriptMetadata
    speakers: Dict[str, str]  # speaker_name -> full text
    sections: Dict[str, str]  # section_name -> full text


class TranscriptProcessor:
    """Process earnings call transcripts with validation"""

    # Maximum file size in bytes (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self):
        """Initialize transcript processor"""
        self.speaker_patterns = {
            'ceo': r'(?:Chief Executive Officer|CEO|President(?:\s+and\s+CEO)?)',
            'cfo': r'(?:Chief Financial Officer|CFO|Finance Director)',
            'coo': r'(?:Chief Operating Officer|COO)',
            'analyst': r'(?:Analyst)',
        }
    
    def validate_file(self, file_path: str) -> None:
        """
        Validate transcript file before processing

        Args:
            file_path: Path to transcript file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid (size, format, content)
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"Transcript file not found: {file_path}")

        # Check file format
        if path.suffix not in ['.txt', '.md']:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: .txt, .md"
            )

        # Check file size
        file_size = path.stat().st_size
        if file_size == 0:
            raise ValueError(f"File is empty: {file_path}")

        if file_size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            raise ValueError(
                f"File too large: {actual_mb:.2f} MB. "
                f"Maximum allowed: {max_mb:.0f} MB"
            )

    def validate_content(self, text: str) -> None:
        """
        Validate transcript content

        Args:
            text: Transcript text

        Raises:
            ValueError: If content is invalid
        """
        if not text or not text.strip():
            raise ValueError("Transcript content is empty")

        # Check word count
        word_count = len(text.split())

        if word_count < settings.MIN_TRANSCRIPT_LENGTH:
            raise ValueError(
                f"Transcript too short: {word_count} words. "
                f"Minimum required: {settings.MIN_TRANSCRIPT_LENGTH} words"
            )

        if word_count > settings.MAX_TRANSCRIPT_LENGTH:
            raise ValueError(
                f"Transcript too long: {word_count} words. "
                f"Maximum allowed: {settings.MAX_TRANSCRIPT_LENGTH} words"
            )

        # Check if text contains actual content (not just whitespace/special chars)
        alphanumeric_chars = sum(c.isalnum() for c in text)
        if alphanumeric_chars < 100:
            raise ValueError(
                "Transcript appears to contain invalid content "
                "(too few alphanumeric characters)"
            )

    def load_transcript(self, file_path: str) -> str:
        """
        Load and validate transcript from file

        Args:
            file_path: Path to transcript file (.txt or .md)

        Returns:
            Raw transcript text

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file or content is invalid
        """
        # Validate file
        self.validate_file(file_path)

        # Load content
        path = Path(file_path)
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()

        # Validate content
        self.validate_content(text)

        return text
    
    def extract_metadata(self, text: str) -> TranscriptMetadata:
        """
        Extract metadata from transcript header
        
        Args:
            text: Raw transcript text
            
        Returns:
            TranscriptMetadata object
        """
        metadata = TranscriptMetadata()
        
        # Try to extract company name
        company_match = re.search(r'Company:\s*([^\n]+)', text, re.IGNORECASE)
        if company_match:
            metadata.company_name = company_match.group(1).strip()
        
        # Try to extract ticker
        ticker_match = re.search(r'Ticker:\s*([A-Z]+)', text)
        if ticker_match:
            metadata.ticker = ticker_match.group(1).strip()
        
        # Try to extract quarter and year
        quarter_match = re.search(r'(Q[1-4])\s+(\d{4})', text)
        if quarter_match:
            metadata.quarter = quarter_match.group(1)
            metadata.year = int(quarter_match.group(2))
        
        # Try to extract date
        date_match = re.search(r'Date:\s*([^\n]+)', text, re.IGNORECASE)
        if date_match:
            metadata.date = date_match.group(1).strip()
        
        return metadata
    
    def identify_speakers(self, text: str) -> Dict[str, List[str]]:
        """
        Identify and extract speaker segments
        
        Args:
            text: Cleaned transcript text
            
        Returns:
            Dict mapping speaker names to their text segments
        """
        speakers = {}
        
        # Pattern: "Speaker Name (Title): text"
        # or "Speaker Name - Title: text"
        speaker_pattern = r'([A-Z][a-zA-Z\s\.]+?)(?:\s*[-–]\s*|\s*\()(.*?)(?:\)|:)\s*([^\n]+(?:\n(?![A-Z][a-zA-Z\s\.]+?(?:\s*[-–]\s*|\s*\()[^\n]*).)*)'
        
        matches = re.finditer(speaker_pattern, text, re.MULTILINE)
        
        for match in matches:
            speaker_name = match.group(1).strip()
            title = match.group(2).strip() if match.group(2) else ""
            content = match.group(3).strip()
            
            # Categorize speaker
            speaker_key = self._categorize_speaker(speaker_name, title)
            
            if speaker_key not in speakers:
                speakers[speaker_key] = []
            
            speakers[speaker_key].append(content)
        
        return speakers
    
    def _categorize_speaker(self, name: str, title: str) -> str:
        """
        Categorize speaker by role
        
        Args:
            name: Speaker name
            title: Speaker title
            
        Returns:
            Categorized speaker key (ceo, cfo, analyst, etc.)
        """
        title_lower = title.lower()
        
        for role, pattern in self.speaker_patterns.items():
            if re.search(pattern, title, re.IGNORECASE):
                return role
        
        # Default to name if no role match
        return name
    
    def split_sections(self, text: str) -> Dict[str, str]:
        """
        Split transcript into sections (prepared remarks, Q&A)
        
        Args:
            text: Cleaned transcript text
            
        Returns:
            Dict with section names and content
        """
        sections = {}
        
        # Look for common section markers
        qa_patterns = [
            r'Question[s]?\s+(?:and|&)\s+Answer[s]?',
            r'Q\s*&\s*A',
            r'Operator:',
        ]
        
        # Find Q&A start
        qa_start = None
        for pattern in qa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                qa_start = match.start()
                break
        
        if qa_start:
            sections['prepared_remarks'] = text[:qa_start].strip()
            sections['qa'] = text[qa_start:].strip()
        else:
            # If no clear Q&A section, treat entire text as prepared remarks
            sections['prepared_remarks'] = text
            sections['qa'] = ""
        
        return sections
    
    def process(self, file_path: str) -> ProcessedTranscript:
        """
        Process a transcript file end-to-end
        
        Args:
            file_path: Path to transcript file
            
        Returns:
            ProcessedTranscript object
        """
        # Load raw text
        raw_text = self.load_transcript(file_path)
        
        # Extract metadata
        metadata = self.extract_metadata(raw_text)
        
        # Clean text
        cleaned_text = clean_text(raw_text)
        
        # Tokenize
        sentences = tokenize_sentences(cleaned_text)
        words = tokenize_words(cleaned_text, lowercase=False, remove_punct=True)
        
        # Identify speakers and sections
        speakers = self.identify_speakers(cleaned_text)
        sections = self.split_sections(cleaned_text)
        
        # Convert speaker lists to concatenated strings
        speaker_texts = {
            name: ' '.join(segments)
            for name, segments in speakers.items()
        }
        
        return ProcessedTranscript(
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            sentences=sentences,
            words=words,
            word_count=len(words),
            sentence_count=len(sentences),
            metadata=metadata,
            speakers=speaker_texts,
            sections=sections
        )
    
    def validate_transcript(self, transcript: ProcessedTranscript) -> List[str]:
        """
        Validate transcript quality
        
        Args:
            transcript: Processed transcript
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check minimum length
        from config.settings import settings
        if transcript.word_count < settings.MIN_TRANSCRIPT_LENGTH:
            warnings.append(
                f"Transcript too short ({transcript.word_count} words). "
                f"Minimum {settings.MIN_TRANSCRIPT_LENGTH} words required."
            )
        
        # Check maximum length
        if transcript.word_count > settings.MAX_TRANSCRIPT_LENGTH:
            warnings.append(
                f"Transcript too long ({transcript.word_count} words). "
                f"Maximum {settings.MAX_TRANSCRIPT_LENGTH} words supported."
            )
        
        # Check for speaker identification
        if not transcript.speakers:
            warnings.append("No speakers identified. Results may be less accurate.")
        
        # Check for section split
        if not transcript.sections.get('qa'):
            warnings.append("No Q&A section identified. May affect analysis.")
        
        return warnings
