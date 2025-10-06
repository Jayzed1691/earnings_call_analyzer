# Enhanced NLP Features Guide

## Overview

This guide covers the enhanced NLP preprocessing capabilities added to the Earnings Call Analyzer, including:

1. **Full Loughran-McDonald Dictionary Integration**
2. **Advanced Text Preprocessing**
3. **Named Entity Recognition (NER)**
4. **Multi-word Financial Phrase Detection**
5. **Intelligent Stopword Management**
6. **Lemmatization**

---

## 1. Loughran-McDonald Dictionary Setup

### Processing the Full Dictionary

The system now supports the complete LM Master Dictionary (1993-2024).

#### Step 1: Download the Dictionary

1. Visit: https://sraf.nd.edu/loughranmcdonald-master-dictionary/
2. Download the latest CSV or XLSX file
3. Save it locally (e.g., `~/Downloads/LoughranMcDonald_MasterDictionary_1993-2024.csv`)

#### Step 2: Process the Dictionary

```bash
# Process from CSV
python scripts/download_dictionaries.py --process ~/Downloads/LoughranMcDonald_MasterDictionary_1993-2024.csv

# Or from XLSX
python scripts/download_dictionaries.py --process ~/Downloads/LoughranMcDonald_MasterDictionary_1993-2024.xlsx
```

This will:
- Extract all 7 sentiment categories
- Create lowercase, deduplicated word lists
- Save .txt files to `data/dictionaries/loughran_mcdonald/`

#### Expected Output

```
Processing Loughran-McDonald Master Dictionary...
Input: ~/Downloads/LoughranMcDonald_MasterDictionary_1993-2024.csv
Output: data/dictionaries/loughran_mcdonald

Loaded 195,878 words from master dictionary

✓ Created negative.txt (2,355 words)
✓ Created positive.txt (354 words)
✓ Created uncertainty.txt (285 words)
✓ Created litigious.txt (871 words)
✓ Created strong_modal.txt (19 words)
✓ Created weak_modal.txt (27 words)
✓ Created constraining.txt (184 words)

✓ Dictionary processing complete!
```

#### For Testing (Starter Dictionary)

If you just want to test the system without the full dictionary:

```bash
python scripts/download_dictionaries.py --create-starter
```

---

## 2. Advanced Preprocessing Setup

### Installation

#### Install Additional Dependencies

```bash
# Install pandas for CSV/Excel processing
pip install pandas openpyxl

# Download spaCy model for NER
python -m spacy download en_core_web_sm

# Download additional NLTK data
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```

### Configuration Files

#### Financial Phrases Configuration

Create `data/nlp_config/financial_phrases.json`:

```json
{
  "description": "Multi-word financial phrases",
  "version": "1.0",
  "phrases": [
    "earnings per share",
    "return on equity",
    "operating margin",
    "free cash flow",
    "year over year",
    ... more phrases ...
  ]
}
```

#### Custom Stopwords Configuration

Create `data/nlp_config/custom_stopwords.json`:

```json
{
  "description": "Custom stopword configuration",
  "version": "1.0",
  "preserve": [
    "not", "no", "up", "down", "more", "less",
    "positive", "negative", "strong", "weak"
  ],
  "financial": [
    "quarter", "year", "fiscal", "call", "today"
  ]
}
```

---

## 3. Using Advanced Preprocessing

### Basic Usage

```python
from pathlib import Path
from src.nlp.advanced_preprocessing import AdvancedTextPreprocessor

# Initialize preprocessor
preprocessor = AdvancedTextPreprocessor(
    phrases_file=Path("data/nlp_config/financial_phrases.json"),
    stopwords_file=Path("data/nlp_config/custom_stopwords.json"),
    enable_ner=True,
    enable_lemmatization=True
)

# Preprocess text
text = "Revenue increased 15% year over year to $1.5 billion in Q3."

result = preprocessor.preprocess(
    text,
    detect_phrases=True,
    remove_stopwords=False,  # Keep stopwords for sentiment analysis
    lemmatize=True,
    extract_entities=True
)

print(result['processed'])
# Output: "revenue increased 15% year_over_year to $1.5 billion in q3."

print(result['phrases'])
# Output: [('year over year', 26, 40)]

print(result['entities'])
# Output: {'money': ['$1.5 billion'], 'dates': ['Q3'], ...}
```

### Integration with Sentiment Analysis

```python
# For sentiment analysis, use specialized preprocessing
normalized_text = preprocessor.normalize_for_sentiment(text)

# This:
# - Preserves negations (not, no, never)
# - Detects financial phrases
# - Lemmatizes words
# - Does NOT remove stopwords (sentiment-bearing)
```

### Integration with Complexity Analysis

```python
# For readability/complexity, use minimal preprocessing
normalized_text = preprocessor.normalize_for_complexity(text)

# This:
# - Detects phrases but doesn't replace them
# - Preserves original sentence structure
# - Minimal normalization only
```

---

## 4. Named Entity Recognition

### Extracting Entities

```python
from src.nlp.advanced_preprocessing import NamedEntityRecognizer

ner = NamedEntityRecognizer()

text = "Apple Inc. reported $89.5 billion in revenue. Tim Cook discussed Q4 results."

entities = ner.extract_entities(text)

print(entities)
# {
#   'companies': ['Apple Inc.'],
#   'people': ['Tim Cook'],
#   'money': ['$89.5 billion'],
#   'dates': ['Q4'],
#   'percentages': [],
#   'locations': [],
#   'products': []
# }
```

### Masking Sensitive Entities

```python
# Mask company and people names for anonymized analysis
masked_text = ner.mask_entities(text, entity_types=['companies', 'people'])

print(masked_text)
# "[COMPANY] reported $89.5 billion in revenue. [PERSON] discussed Q4 results."
```

---

## 5. Multi-word Phrase Detection

### Why It Matters

Without phrase detection:
- "earnings per share" → 3 separate words
- Loses semantic meaning
- Dilutes sentiment analysis

With phrase detection:
- "earnings per share" → "earnings_per_share" (single token)
- Preserves meaning
- More accurate analysis

### Usage

```python
from src.nlp.advanced_preprocessing import FinancialPhraseDetector

detector = FinancialPhraseDetector()

text = "Earnings per share increased to $2.50, up 15% year over year."

# Detect phrases
phrases = detector.detect_phrases(text)
print(phrases)
# [('earnings per share', 0, 19), ('year over year', 49, 63)]

# Replace with tokens
tokenized = detector.replace_with_tokens(text)
print(tokenized)
# "earnings_per_share increased to $2.50, up 15% year_over_year."
```

### Adding Custom Phrases

Edit `data/nlp_config/financial_phrases.json`:

```json
{
  "phrases": [
    "existing phrase 1",
    "existing phrase 2",
    "your custom phrase",
    "another custom term"
  ]
}
```

---

## 6. Intelligent Stopword Management

### The Problem with Standard Stopwords

Standard stopword lists (e.g., NLTK's English stopwords) remove words like:
- "not" - Critical for sentiment!
- "no" - Critical for sentiment!
- "up", "down" - Directional indicators!
- "more", "less" - Comparative indicators!

### Our Solution

**Preserve sentiment-bearing words:**
```python
stopword_manager = FinancialStopwords()

print(stopword_manager.is_stopword("not"))   # False (preserved)
print(stopword_manager.is_stopword("the"))   # True (removed)
print(stopword_manager.is_stopword("up"))    # False (preserved)
```

**Remove financial filler words:**
```python
print(stopword_manager.is_stopword("quarter"))  # True
print(stopword_manager.is_stopword("fiscal"))   # True
print(stopword_manager.is_stopword("call"))     # True
```

---

## 7. Lemmatization

### Benefits

Reduces words to their base form:
- "running" → "run"
- "improved" → "improve"
- "better" → "good"

This:
- Reduces vocabulary size
- Improves dictionary matching
- Normalizes tense variations

### Usage

```python
words = ["growing", "improved", "strongest", "weakening"]

preprocessor = AdvancedTextPreprocessor(enable_lemmatization=True)

result = preprocessor.preprocess(" ".join(words), lemmatize=True)
print(result['processed_words'])
# ['grow', 'improve', 'strong', 'weaken']
```

---

## 8. Integration with Existing Analysis

### Updating the Sentiment Analyzer

```python
from src.analysis.sentiment.lexicon_analyzer import LexiconSentimentAnalyzer
from src.nlp.advanced_preprocessing import AdvancedTextPreprocessor

class EnhancedLexiconAnalyzer(LexiconSentimentAnalyzer):
    def __init__(self):
        super().__init__()
        self.preprocessor = AdvancedTextPreprocessor()
    
    def analyze(self, text: str):
        # Preprocess for sentiment
        normalized = self.preprocessor.normalize_for_sentiment(text)
        
        # Use parent's analysis on normalized text
        return super().analyze(normalized)
```

### Updating the Complexity Analyzer

```python
from src.analysis.complexity.readability import ComplexityAnalyzer
from src.nlp.advanced_preprocessing import AdvancedTextPreprocessor

class EnhancedComplexityAnalyzer(ComplexityAnalyzer):
    def __init__(self):
        super().__init__()
        self.preprocessor = AdvancedTextPreprocessor()
    
    def analyze(self, text: str):
        # Minimal preprocessing for complexity
        normalized = self.preprocessor.normalize_for_complexity(text)
        
        # Use parent's analysis
        return super().analyze(normalized)
```

---

## 9. Best Practices

### When to Use Which Features

| Analysis Type | Phrase Detection | Stopword Removal | Lemmatization | NER |
|--------------|------------------|------------------|---------------|-----|
| **Sentiment** | ✅ Yes | ❌ No (preserve negations) | ✅ Yes | Optional |
| **Complexity** | ⚠️ Detect only | ❌ No (preserve structure) | ❌ No (preserve forms) | ❌ No |
| **Numerical** | ✅ Yes | ❌ No (context matters) | ⚠️ Optional | ✅ Yes (for context) |
| **Entity Extraction** | ✅ Yes | ❌ No | ⚠️ Optional | ✅ Yes |

### Configuration Recommendations

**For Production:**
```python
preprocessor = AdvancedTextPreprocessor(
    phrases_file=Path("data/nlp_config/financial_phrases.json"),
    stopwords_file=Path("data/nlp_config/custom_stopwords.json"),
    enable_ner=True,
    enable_lemmatization=True
)
```

**For Fast Processing:**
```python
preprocessor = AdvancedTextPreprocessor(
    enable_ner=False,  # Skip NER (slower)
    enable_lemmatization=True
)
```

**For Maximum Accuracy:**
```python
preprocessor = AdvancedTextPreprocessor(
    phrases_file=Path("data/nlp_config/financial_phrases.json"),
    stopwords_file=Path("data/nlp_config/custom_stopwords.json"),
    enable_ner=True,
    enable_lemmatization=True
)
```

---

## 10. Performance Considerations

### Speed Comparison

| Component | Overhead | Impact on 10K word transcript |
|-----------|----------|-------------------------------|
| **Phrase Detection** | Low | +0.5 seconds |
| **Lemmatization** | Low | +1 second |
| **NER (spaCy)** | Medium | +3-5 seconds |
| **Stopword Removal** | Minimal | +0.1 seconds |

### Memory Usage

- **Standard Processing**: ~50 MB
- **With NER Enabled**: ~200 MB (spaCy model)
- **With Full LM Dictionary**: +10 MB

### Optimization Tips

1. **Disable NER for batch processing** if entities aren't needed
2. **Cache preprocessed results** for repeated analyses
3. **Use multiprocessing** for large batches
4. **Load spaCy model once** at startup, not per-document

---

## 11. Troubleshooting

### Issue: spaCy Model Not Found

```bash
# Error: Can't find model 'en_core_web_sm'
# Solution:
python -m spacy download en_core_web_sm
```

### Issue: NLTK Data Missing

```python
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
```

### Issue: Phrases Not Detected

1. Check phrases file path is correct
2. Verify JSON format is valid
3. Ensure phrases are lowercase
4. Check for typos in phrase list

### Issue: Poor Performance with NER

```python
# Disable NER for faster processing
preprocessor = AdvancedTextPreprocessor(enable_ner=False)
```

---

## 12. Examples

### Complete Analysis Pipeline

```python
from pathlib import Path
from src.nlp.advanced_preprocessing import AdvancedTextPreprocessor
from src.analysis.sentiment.lexicon_analyzer import LexiconSentimentAnalyzer

# Load transcript
with open('transcript.txt', 'r') as f:
    text = f.read()

# Initialize components
preprocessor = AdvancedTextPreprocessor(
    phrases_file=Path("data/nlp_config/financial_phrases.json"),
    enable_ner=True,
    enable_lemmatization=True
)

# Full preprocessing
result = preprocessor.preprocess(
    text,
    detect_phrases=True,
    extract_entities=True
)

print(f"Detected {len(result['phrases'])} financial phrases")
print(f"Found {len(result['entities']['companies'])} companies")
print(f"Found {len(result['entities']['money'])} monetary values")

# Sentiment analysis on preprocessed text
sentiment_text = preprocessor.normalize_for_sentiment(text)
analyzer = LexiconSentimentAnalyzer()
sentiment = analyzer.analyze(sentiment_text)

print(f"Net Positivity: {sentiment.net_positivity:.2f}")
```

---

## 13. Future Enhancements

Planned improvements:

1. **Industry-Specific Phrase Libraries**
   - Tech sector phrases
   - Financial services phrases
   - Healthcare/pharma phrases

2. **Contextual Embeddings**
   - Word2Vec/GloVe trained on earnings calls
   - BERT-based phrase detection

3. **Automated Phrase Discovery**
   - Statistical extraction of frequent phrases
   - TF-IDF based phrase importance

4. **Enhanced Entity Linking**
   - Link companies to tickers
   - Resolve person names to roles

---

## Questions?

For issues or questions:
1. Check the troubleshooting section
2. Review the examples
3. Examine the test cases in `tests/test_preprocessing.py`
