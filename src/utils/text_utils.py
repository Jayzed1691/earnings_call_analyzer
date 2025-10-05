"""
Text processing utilities
"""
import re
from typing import List, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from config.settings import settings

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep sentence punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'\"$%]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text.strip()


def tokenize_sentences(text: str) -> List[str]:
    """
    Split text into sentences
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    return sent_tokenize(text)


def tokenize_words(text: str, lowercase: bool = True, remove_punct: bool = False) -> List[str]:
    """
    Split text into words
    
    Args:
        text: Input text
        lowercase: Convert to lowercase
        remove_punct: Remove punctuation
        
    Returns:
        List of words
    """
    words = word_tokenize(text)
    
    if lowercase:
        words = [w.lower() for w in words]
    
    if remove_punct:
        words = [w for w in words if w.isalnum()]
    
    return words


def count_syllables(word: str) -> int:
    """
    Count syllables in a word using rule-based approach
    
    Args:
        word: Word to analyze
        
    Returns:
        Number of syllables
    """
    word = word.lower().strip()
    
    # Check exceptions first
    if word in settings.SYLLABLE_EXCEPTIONS:
        return settings.SYLLABLE_EXCEPTIONS[word]
    
    # Remove non-alphabetic characters
    word = re.sub(r'[^a-z]', '', word)
    
    if len(word) == 0:
        return 0
    
    # Count vowel groups
    vowels = "aeiouy"
    syllable_count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    # Special cases
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        syllable_count += 1
    
    # Every word has at least one syllable
    return max(1, syllable_count)


def extract_numerical_tokens(text: str) -> List[Tuple[str, str]]:
    """
    Extract numerical tokens from text with context
    
    Args:
        text: Input text
        
    Returns:
        List of tuples (number, context_sentence)
    """
    sentences = tokenize_sentences(text)
    numerical_tokens = []
    
    # Patterns for different number types
    patterns = [
        r'\$\s*\d+(?:\.\d+)?(?:\s*(?:million|billion|trillion|M|B|T))?',  # Currency
        r'\d+(?:\.\d+)?%',  # Percentages
        r'\d+(?:\.\d+)?(?:\s*(?:million|billion|trillion|M|B|T))?',  # Plain numbers with scale
        r'\d+(?:,\d{3})*(?:\.\d+)?',  # Numbers with commas
    ]
    
    combined_pattern = '|'.join(patterns)
    
    for sentence in sentences:
        matches = re.findall(combined_pattern, sentence, re.IGNORECASE)
        for match in matches:
            # Skip dates (simple heuristic)
            if not re.match(r'^\d{4}$', match.strip()):
                numerical_tokens.append((match, sentence))
    
    return numerical_tokens


def count_complex_words(words: List[str]) -> int:
    """
    Count words with 3+ syllables (for Gunning Fog)
    
    Args:
        words: List of words
        
    Returns:
        Count of complex words
    """
    complex_count = 0
    
    for word in words:
        # Skip proper nouns (capitalized), numbers, and very short words
        if word[0].isupper() or not word.isalpha() or len(word) <= 3:
            continue
            
        syllables = count_syllables(word)
        if syllables >= 3:
            complex_count += 1
    
    return complex_count


def count_polysyllabic_words(words: List[str]) -> int:
    """
    Count words with 3+ syllables (for SMOG)
    
    Args:
        words: List of words
        
    Returns:
        Count of polysyllabic words
    """
    return sum(1 for word in words if count_syllables(word) >= 3)


def split_into_chunks(text: str, chunk_size: int = 512, overlap: int = 128) -> List[str]:
    """
    Split text into overlapping chunks for LLM processing
    
    Args:
        text: Input text
        chunk_size: Maximum chunk size in words
        overlap: Overlap size in words
        
    Returns:
        List of text chunks
    """
    words = tokenize_words(text, lowercase=False, remove_punct=False)
    chunks = []
    
    i = 0
    while i < len(words):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    
    return chunks


def calculate_word_character_ratio(text: str) -> Tuple[float, float]:
    """
    Calculate characters per word for Coleman-Liau Index
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (chars per 100 words, sentences per 100 words)
    """
    words = tokenize_words(text, lowercase=False, remove_punct=False)
    sentences = tokenize_sentences(text)
    
    if len(words) == 0:
        return 0.0, 0.0
    
    # Count only alphabetic characters
    total_chars = sum(len(re.sub(r'[^a-zA-Z]', '', word)) for word in words)
    
    l = (total_chars / len(words)) * 100  # Letters per 100 words
    s = (len(sentences) / len(words)) * 100  # Sentences per 100 words
    
    return l, s


def identify_forward_looking_statements(text: str) -> List[str]:
    """
    Identify sentences containing forward-looking language
    
    Args:
        text: Input text
        
    Returns:
        List of forward-looking sentences
    """
    forward_keywords = [
        'expect', 'anticipate', 'forecast', 'guidance', 'outlook',
        'will', 'plan to', 'intend', 'project', 'estimate',
        'believe', 'target', 'goal', 'objective', 'future'
    ]
    
    sentences = tokenize_sentences(text)
    forward_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in forward_keywords):
            forward_sentences.append(sentence)
    
    return forward_sentences


def identify_backward_looking_statements(text: str) -> List[str]:
    """
    Identify sentences containing backward-looking language
    
    Args:
        text: Input text
        
    Returns:
        List of backward-looking sentences
    """
    backward_keywords = [
        'was', 'were', 'had', 'did', 'reported', 'achieved',
        'completed', 'delivered', 'generated', 'posted',
        'last quarter', 'previous', 'prior', 'historical'
    ]
    
    sentences = tokenize_sentences(text)
    backward_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in backward_keywords):
            backward_sentences.append(sentence)
    
    return backward_sentences
