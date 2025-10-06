"""
Advanced NLP Preprocessing Module - UPDATED FOR MULTIPLE PHRASE FILES
Includes: NER, lemmatization, multi-word phrase detection, custom stopwords
"""
import re
import json
from typing import List, Dict, Tuple, Set, Optional, Union
from pathlib import Path
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('wordnet', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('omw-1.4', quiet=True)

# Try to import spaCy for NER
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        print("Warning: spaCy model 'en_core_web_sm' not found. NER will be disabled.")
        print("Install with: python -m spacy download en_core_web_sm")
        SPACY_AVAILABLE = False
        nlp = None
except ImportError:
    print("Warning: spaCy not installed. NER will be disabled.")
    SPACY_AVAILABLE = False
    nlp = None


class FinancialPhraseDetector:
    """Detects multi-word financial and accounting phrases - SUPPORTS MULTIPLE FILES"""
    
    def __init__(self, phrases_files: Union[Path, List[Path], None] = None):
        """
        Initialize phrase detector with support for multiple phrase files
        
        Args:
            phrases_files: Single Path, list of Paths, or None
        """
        # Convert single Path to list for uniform handling
        if isinstance(phrases_files, Path):
            phrases_files = [phrases_files]
        elif phrases_files is None:
            phrases_files = []
        
        self.phrases = self._load_financial_phrases(phrases_files)
        # Sort by length (longest first) for proper matching
        self.sorted_phrases = sorted(self.phrases, key=len, reverse=True)
        
        print(f"✓ Phrase detector initialized with {len(self.phrases)} total phrases")
    
    def _load_financial_phrases(self, phrases_files: List[Path]) -> Set[str]:
        """
        Load financial phrases from multiple JSON files
        
        Args:
            phrases_files: List of Path objects to phrase JSON files
            
        Returns:
            Set of all phrases (lowercase)
        """
        all_phrases = set()
        
        if not phrases_files:
            print("No phrase files specified, loading default phrases...")
            return self._get_default_phrases()
        
        for phrase_file in phrases_files:
            if not phrase_file.exists():
                print(f"⚠️  Warning: Phrase file not found: {phrase_file}")
                continue
            
            try:
                with open(phrase_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                phrases = []
                
                # Handle different JSON structures
                if 'phrases' in data:
                    # Simple list format (e.g., financial_phrases.json)
                    phrases = data['phrases']
                    
                elif 'categories' in data:
                    # Categorized format (e.g., oil_gas_phrases.json, indonesian_titles.json)
                    for category, phrase_list in data['categories'].items():
                        if isinstance(phrase_list, list):
                            phrases.extend(phrase_list)
                        else:
                            print(f"⚠️  Warning: Category '{category}' in {phrase_file.name} is not a list")
                
                else:
                    print(f"⚠️  Warning: Unknown JSON format in {phrase_file.name}")
                    print(f"    Expected 'phrases' (list) or 'categories' (dict) at top level")
                    continue
                
                # Add to set (lowercased for case-insensitive matching)
                phrase_count = len(phrases)
                all_phrases.update(p.lower() for p in phrases if isinstance(p, str))
                
                print(f"✓ Loaded {phrase_count} phrases from {phrase_file.name}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON from {phrase_file.name}: {e}")
            except Exception as e:
                print(f"❌ Error loading {phrase_file.name}: {e}")
        
        if not all_phrases:
            print("⚠️  No phrases loaded from files, using default phrases")
            return self._get_default_phrases()
        
        return all_phrases
    
    def _get_default_phrases(self) -> Set[str]:
        """Get default financial phrases if no files loaded"""
        return {
            # Core financial metrics
            'earnings per share', 'eps', 'return on equity', 'roe',
            'return on assets', 'roa', 'return on investment', 'roi',
            'gross margin', 'operating margin', 'net margin',
            'operating income', 'net income', 'operating cash flow',
            'free cash flow', 'revenue growth', 'year over year', 'yoy',
            'quarter over quarter', 'qoq',
            
            # Financial statements
            'balance sheet', 'income statement', 'cash flow statement',
            
            # Business metrics
            'market share', 'customer acquisition', 'customer retention',
            'average revenue per user', 'arpu',
            
            # Accounting
            'generally accepted accounting principles', 'gaap',
            'non gaap', 'adjusted earnings', 'adjusted ebitda',
            
            # Corporate actions
            'share repurchase', 'stock buyback', 'capital expenditure', 'capex',
            'research and development', 'r and d', 'r&d'
        }
    
    def detect_phrases(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Detect financial phrases in text
        
        Args:
            text: Input text
            
        Returns:
            List of (phrase, start_pos, end_pos) tuples
        """
        text_lower = text.lower()
        detected = []
        
        for phrase in self.sorted_phrases:
            # Find all occurrences
            start = 0
            while True:
                pos = text_lower.find(phrase, start)
                if pos == -1:
                    break
                detected.append((phrase, pos, pos + len(phrase)))
                start = pos + 1
        
        # Remove overlapping detections (keep longer phrases)
        detected.sort(key=lambda x: (x[1], -(x[2] - x[1])))
        non_overlapping = []
        
        for phrase, start, end in detected:
            # Check if overlaps with any existing detection
            overlaps = False
            for _, existing_start, existing_end in non_overlapping:
                if not (end <= existing_start or start >= existing_end):
                    overlaps = True
                    break
            
            if not overlaps:
                non_overlapping.append((phrase, start, end))
        
        return non_overlapping
    
    def replace_with_tokens(self, text: str) -> str:
        """
        Replace multi-word phrases with single tokens
        
        Args:
            text: Input text
            
        Returns:
            Text with phrases replaced by underscore-connected tokens
        """
        phrases_found = self.detect_phrases(text)
        
        if not phrases_found:
            return text
        
        # Sort by position (reverse) to replace from end to start
        phrases_found.sort(key=lambda x: x[1], reverse=True)
        
        result = text
        for phrase, start, end in phrases_found:
            # Replace spaces with underscores in the phrase
            token = phrase.replace(' ', '_')
            result = result[:start] + token + result[end:]
        
        return result


class FinancialStopwords:
    """Custom stopword management for financial text"""
    
    def __init__(self, custom_stopwords_file: Optional[Path] = None):
        """
        Initialize stopword manager
        
        Args:
            custom_stopwords_file: Path to JSON with custom stopwords config
        """
        # Get standard English stopwords
        self.standard_stopwords = set(stopwords.words('english'))
        
        # Words to preserve (sentiment-bearing or important)
        self.preserve_words = {
            'not', 'no', 'nor', 'neither', 'never', 'none', 'nobody', 'nothing',
            'up', 'down', 'above', 'below', 'more', 'less', 'most', 'least',
            'very', 'too', 'against', 'before', 'after', 'during', 'until',
            'positive', 'negative', 'good', 'bad', 'better', 'worse', 'best', 'worst'
        }
        
        # Financial stopwords to remove
        self.financial_stopwords = {
            'quarter', 'year', 'fiscal', 'period', 'company', 'business',
            'call', 'today', 'discussion', 'presentation', 'slide'
        }
        
        # Load custom configuration if provided
        if custom_stopwords_file and custom_stopwords_file.exists():
            try:
                with open(custom_stopwords_file, 'r') as f:
                    config = json.load(f)
                    self.preserve_words.update(config.get('preserve', []))
                    self.financial_stopwords.update(config.get('financial', []))
                    print(f"✓ Loaded custom stopwords from {custom_stopwords_file.name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not load stopwords config: {e}")
        
        # Final stopword set
        self.stopwords = (self.standard_stopwords | self.financial_stopwords) - self.preserve_words
    
    def is_stopword(self, word: str) -> bool:
        """Check if word is a stopword"""
        return word.lower() in self.stopwords
    
    def remove_stopwords(self, words: List[str]) -> List[str]:
        """Remove stopwords from word list"""
        return [word for word in words if not self.is_stopword(word)]


class NamedEntityRecognizer:
    """Extract named entities from financial text"""
    
    def __init__(self):
        """Initialize NER"""
        self.enabled = SPACY_AVAILABLE and nlp is not None
        if self.enabled:
            print("✓ Named Entity Recognition enabled (spaCy)")
        else:
            print("⚠️  Named Entity Recognition disabled (spaCy not available)")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities
        
        Args:
            text: Input text
            
        Returns:
            Dict mapping entity types to lists of entities
        """
        if not self.enabled:
            return {}
        
        doc = nlp(text)
        
        entities = {
            'companies': [],
            'people': [],
            'money': [],
            'dates': [],
            'percentages': [],
            'locations': [],
            'products': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entities['companies'].append(ent.text)
            elif ent.label_ == 'PERSON':
                entities['people'].append(ent.text)
            elif ent.label_ == 'MONEY':
                entities['money'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'PERCENT':
                entities['percentages'].append(ent.text)
            elif ent.label_ in ('GPE', 'LOC'):
                entities['locations'].append(ent.text)
            elif ent.label_ == 'PRODUCT':
                entities['products'].append(ent.text)
        
        return entities
    
    def mask_entities(self, text: str, entity_types: List[str] = None) -> str:
        """
        Mask specific entity types with generic tokens
        
        Args:
            text: Input text
            entity_types: Types to mask (e.g., ['companies', 'people'])
            
        Returns:
            Text with entities masked
        """
        if not self.enabled:
            return text
        
        entity_types = entity_types or []
        doc = nlp(text)
        
        # Create mapping of entity types to mask tokens
        mask_map = {
            'ORG': 'COMPANY',
            'PERSON': 'PERSON',
            'GPE': 'LOCATION',
            'LOC': 'LOCATION'
        }
        
        # Reverse process from end to start
        result = text
        for ent in reversed(doc.ents):
            if ent.label_ in mask_map:
                mask_token = f'[{mask_map[ent.label_]}]'
                result = result[:ent.start_char] + mask_token + result[ent.end_char:]
        
        return result


class AdvancedTextPreprocessor:
    """Complete advanced preprocessing pipeline - UPDATED FOR MULTIPLE PHRASE FILES"""
    
    def __init__(
        self,
        phrases_files: Union[Path, List[Path], None] = None,
        stopwords_file: Optional[Path] = None,
        enable_ner: bool = True,
        enable_lemmatization: bool = True
    ):
        """
        Initialize preprocessor
        
        Args:
            phrases_files: Single Path, list of Paths to phrase JSON files, or None
            stopwords_file: Path to custom stopwords JSON
            enable_ner: Whether to use NER
            enable_lemmatization: Whether to lemmatize words
        """
        print("\n" + "="*60)
        print("INITIALIZING ADVANCED TEXT PREPROCESSOR")
        print("="*60)
        
        self.phrase_detector = FinancialPhraseDetector(phrases_files)
        self.stopword_manager = FinancialStopwords(stopwords_file)
        self.ner = NamedEntityRecognizer() if enable_ner else None
        
        self.enable_lemmatization = enable_lemmatization
        if enable_lemmatization:
            self.lemmatizer = WordNetLemmatizer()
            print("✓ Lemmatization enabled")
        else:
            self.lemmatizer = None
            print("⚠️  Lemmatization disabled")
        
        print("="*60 + "\n")
    
    def preprocess(
        self,
        text: str,
        detect_phrases: bool = True,
        remove_stopwords: bool = False,
        lemmatize: bool = True,
        extract_entities: bool = False
    ) -> Dict[str, any]:
        """
        Full preprocessing pipeline
        
        Args:
            text: Input text
            detect_phrases: Whether to detect multi-word phrases
            remove_stopwords: Whether to remove stopwords
            lemmatize: Whether to lemmatize
            extract_entities: Whether to extract named entities
            
        Returns:
            Dict with processed text and metadata
        """
        result = {
            'original': text,
            'processed': text,
            'phrases': [],
            'entities': {},
            'statistics': {}
        }
        
        # Detect phrases
        if detect_phrases:
            result['phrases'] = self.phrase_detector.detect_phrases(text)
            result['processed'] = self.phrase_detector.replace_with_tokens(text)
        
        # Extract entities
        if extract_entities and self.ner:
            result['entities'] = self.ner.extract_entities(text)
        
        # Tokenize
        from src.utils.text_utils import tokenize_words
        words = tokenize_words(result['processed'], lowercase=True, remove_punct=True)
        
        # Remove stopwords
        if remove_stopwords:
            original_count = len(words)
            words = self.stopword_manager.remove_stopwords(words)
            result['statistics']['stopwords_removed'] = original_count - len(words)
        
        # Lemmatize
        if lemmatize and self.lemmatizer:
            words = [self.lemmatizer.lemmatize(word) for word in words]
        
        result['processed_words'] = words
        result['statistics']['word_count'] = len(words)
        result['statistics']['phrase_count'] = len(result['phrases'])
        
        return result
    
    def normalize_for_sentiment(self, text: str) -> str:
        """
        Preprocessing optimized for sentiment analysis
        Preserves sentiment-bearing words and phrases
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Detect and preserve financial phrases
        text_with_phrases = self.phrase_detector.replace_with_tokens(text)
        
        # Don't remove stopwords for sentiment (negations are important!)
        # But do lemmatize
        from src.utils.text_utils import tokenize_words
        words = tokenize_words(text_with_phrases, lowercase=True, remove_punct=True)
        
        if self.lemmatizer:
            words = [self.lemmatizer.lemmatize(word) for word in words]
        
        return ' '.join(words)
    
    def normalize_for_complexity(self, text: str) -> str:
        """
        Preprocessing for complexity analysis
        Minimal processing to preserve original structure
        
        Args:
            text: Input text
            
        Returns:
            Lightly normalized text
        """
        # Detect phrases but don't replace (just for awareness)
        phrases = self.phrase_detector.detect_phrases(text)
        
        # Light cleaning only
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
