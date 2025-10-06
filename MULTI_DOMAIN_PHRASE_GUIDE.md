# Multi-Domain Phrase Configuration Guide

## Directory Structure for Your Use Case

```
data/
├── dictionaries/
│   └── loughran_mcdonald/              # Processed LM dictionaries
│       ├── negative.txt
│       ├── positive.txt
│       ├── uncertainty.txt
│       ├── litigious.txt
│       ├── strong_modal.txt
│       ├── weak_modal.txt
│       └── constraining.txt
│
└── nlp_config/                         # All JSON configuration files
    ├── financial_phrases.json          # General financial terms
    ├── oil_gas_phrases.json           # Oil & gas E&P specific
    ├── indonesian_titles.json         # Indonesian job titles
    └── custom_stopwords.json          # Stopword configuration
```

## 🛢️ Oil & Gas E&P Phrases

**File:** `data/nlp_config/oil_gas_phrases.json`

### Coverage (450+ phrases and acronyms)

#### Categories:
1. **Exploration & Development** (45 phrases)
   - Drilling operations, well types, subsea development
   - Examples: "exploration well", "horizontal drilling", "subsea completion"

2. **Production Operations** (55 phrases)
   - Production metrics, facilities, infrastructure
   - Examples: "gross production", "enhanced oil recovery", "floating production storage and offloading"

3. **Reserves & Resources** (35 phrases)
   - Reserve classifications, assessments
   - Examples: "proved reserves", "barrels of oil equivalent", "recovery factor"

4. **Metrics & KPIs** (50 phrases)
   - Production rates, costs, financial metrics
   - Examples: "barrels per day", "lifting costs", "operating netback"

5. **Reservoir & Geology** (45 phrases)
   - Geological terms, reservoir properties
   - Examples: "reservoir pressure", "hydrocarbon saturation", "structural trap"

6. **Technical Operations** (30 phrases)
   - Seismic, logging, testing
   - Examples: "three dimensional seismic", "formation evaluation", "well test"

7. **Commercial & Contractual** (45 phrases)
   - PSC, licenses, interests
   - Examples: "production sharing contract", "working interest", "cost recovery"

8. **Safety & Environment** (50 phrases)
   - HSE metrics, environmental compliance
   - Examples: "total recordable incident rate", "flare reduction", "carbon intensity"

9. **Corporate & Strategy** (45 phrases)
   - Portfolio management, capital allocation
   - Examples: "upstream portfolio", "exploration success rate", "infill drilling"

10. **Acronyms** (100+ items)
    - Industry-standard abbreviations
    - Examples: "bopd", "mmcfd", "fpso", "psc", "eor", "eur"

### Key Features:

**Multi-word phrases that must be recognized as units:**
- "production sharing contract" (not "production" + "sharing" + "contract")
- "enhanced oil recovery" (not "enhanced" + "oil" + "recovery")
- "floating production storage and offloading" (complete FPSO definition)

**Acronyms with context:**
- "bopd" (barrels of oil per day)
- "mmcfd" (million cubic feet per day)
- "fpso" (floating production storage and offloading)

## 🇮🇩 Indonesian Job Titles

**File:** `data/nlp_config/indonesian_titles.json`

### Coverage (150+ titles and variations)

#### Categories:

1. **Board of Commissioners** (Dewan Komisaris)
   - "komisaris utama" / "president commissioner"
   - "komisaris independen" / "independent commissioner"
   - Both Indonesian and English variations

2. **Board of Directors** (Dewan Direksi)
   - "direktur utama" / "president director"
   - "direktur keuangan" / "finance director" / "chief financial officer"
   - All functional directorates

3. **Oil & Gas Specific Directors**
   - "direktur hulu" / "upstream director"
   - "direktur eksplorasi" / "exploration director"
   - "direktur pemasaran dan niaga" / "marketing and trading director"

4. **Senior Management**
   - "senior vice president"
   - "general manager"
   - "kepala divisi" / "division head"

5. **Corporate Secretary**
   - "sekretaris perusahaan" / "corporate secretary"
   
6. **Audit & Compliance**
   - "kepala audit internal" / "head of internal audit"
   - "kepala manajemen risiko" / "head of risk management"

7. **Committee Positions**
   - "ketua komite audit" / "chairman of audit committee"
   - "komite manajemen" / "management committee"

### Why This Matters:

**Name-Title Recognition:**
```
"John Smith - Direktur Eksplorasi"
```
The preprocessor will recognize "direktur eksplorasi" as a single phrase (job title), preventing it from being split into "direktur" + "eksplorasi".

**Bilingual Support:**
Indonesian earnings calls often switch between languages:
```
"Direktur Utama, or President Director, will discuss..."
"The Upstream Director, atau Direktur Hulu, reported..."
```

Both variations are recognized.

---

## 🔧 Implementation

### Option 1: Load All Phrase Files (Recommended)

Update `advanced_preprocessing.py` to load multiple phrase files:

```python
from pathlib import Path
import json

class FinancialPhraseDetector:
    def __init__(self, phrases_files: list = None):
        """
        Initialize with multiple phrase files
        
        Args:
            phrases_files: List of Path objects to phrase JSON files
        """
        self.phrases = self._load_multiple_phrase_files(phrases_files)
        self.sorted_phrases = sorted(self.phrases, key=len, reverse=True)
    
    def _load_multiple_phrase_files(self, phrases_files: list) -> set:
        """Load and merge phrases from multiple JSON files"""
        all_phrases = set()
        
        if not phrases_files:
            return self._load_default_phrases()
        
        for phrase_file in phrases_files:
            if not phrase_file.exists():
                print(f"Warning: Phrase file not found: {phrase_file}")
                continue
            
            with open(phrase_file, 'r') as f:
                data = json.load(f)
                
                # Handle different JSON structures
                if 'phrases' in data:
                    # Simple list format
                    phrases = data['phrases']
                elif 'categories' in data:
                    # Categorized format (oil_gas, indonesian_titles)
                    phrases = []
                    for category, phrase_list in data['categories'].items():
                        phrases.extend(phrase_list)
                else:
                    print(f"Warning: Unknown JSON format in {phrase_file}")
                    continue
                
                # Add to set (lowercased)
                all_phrases.update(p.lower() for p in phrases)
                
                print(f"Loaded {len(phrases)} phrases from {phrase_file.name}")
        
        return all_phrases
```

### Option 2: Initialize with Multiple Files

```python
from pathlib import Path
from src.nlp.advanced_preprocessing import AdvancedTextPreprocessor

# Define phrase files for your industry
phrase_files = [
    Path("data/nlp_config/financial_phrases.json"),      # General financial
    Path("data/nlp_config/oil_gas_phrases.json"),        # Oil & gas E&P
    Path("data/nlp_config/indonesian_titles.json")       # Indonesian titles
]

# Initialize preprocessor
preprocessor = AdvancedTextPreprocessor(
    phrases_files=phrase_files,  # Pass list instead of single file
    stopwords_file=Path("data/nlp_config/custom_stopwords.json"),
    enable_ner=True,
    enable_lemmatization=True
)
```

### Option 3: Merge Phrase Files

Create a combined file for your specific use case:

```bash
# Create combined phrase file
python scripts/merge_phrase_files.py \
    --input data/nlp_config/financial_phrases.json \
            data/nlp_config/oil_gas_phrases.json \
            data/nlp_config/indonesian_titles.json \
    --output data/nlp_config/oil_gas_indonesia_combined.json
```

---

## 📊 Usage Examples

### Example 1: Oil & Gas Production Update

**Input Text:**
```
Our gross production reached 150,000 barrels of oil equivalent per day in Q3, 
with upstream operations showing strong performance. The Direktur Hulu reported 
that the floating production storage and offloading facility achieved 95% uptime. 
Enhanced oil recovery projects contributed an additional 12,000 bopd.
```

**Without Phrase Detection:**
- Tokens: "gross", "production", "reached", "150,000", "barrels", "of", "oil", ...
- Phrases split up, meaning lost

**With Oil & Gas Phrase Detection:**
- Phrases detected:
  - "barrels of oil equivalent per day" → single token
  - "upstream operations" → single token
  - "direktur hulu" → single token (job title)
  - "floating production storage and offloading" → single token
  - "enhanced oil recovery" → single token
  - "bopd" → recognized acronym

**Result:** Much better semantic understanding and sentiment analysis.

### Example 2: Indonesian Executive Commentary

**Input Text:**
```
Komisaris Utama and President Commissioner John Doe stated that the 
Direktur Keuangan will present the financial results. The Chief Financial 
Officer noted strong free cash flow generation.
```

**Phrases Detected:**
- "komisaris utama" (Indonesian)
- "president commissioner" (English)
- "direktur keuangan" (Indonesian)
- "chief financial officer" (English)
- "free cash flow" (financial metric)

**Result:** All job title variations recognized correctly, preventing fragmentation.

### Example 3: Production Sharing Contract Discussion

**Input Text:**
```
Under our production sharing contract, the working interest production 
averaged 85,000 boepd. Cost recovery mechanisms and profit oil distribution 
were in line with the PSA terms. Net revenue interest calculations reflected 
the government take provisions.
```

**Phrases Detected:**
- "production sharing contract" / "psc" (contractual)
- "working interest production" (metric)
- "boepd" (acronym for barrels of oil equivalent per day)
- "cost recovery" (PSC term)
- "profit oil" (PSC term)
- "net revenue interest" (ownership term)
- "government take" (fiscal term)

---

## 🎯 Best Practices

### 1. Use All Relevant Phrase Files

For Indonesian oil & gas companies, load all three:
```python
phrase_files = [
    Path("data/nlp_config/financial_phrases.json"),
    Path("data/nlp_config/oil_gas_phrases.json"),
    Path("data/nlp_config/indonesian_titles.json")
]
```

### 2. Verify Phrase Loading

```python
detector = FinancialPhraseDetector(phrases_files=phrase_files)
print(f"Total phrases loaded: {len(detector.phrases)}")
# Should be ~600+ phrases (200 financial + 450 oil/gas + 150 Indonesian)

# Test specific phrases
test_phrases = [
    "production sharing contract",
    "direktur utama",
    "enhanced oil recovery",
    "barrels of oil equivalent per day"
]

for phrase in test_phrases:
    if phrase in detector.phrases:
        print(f"✓ '{phrase}' loaded")
    else:
        print(f"✗ '{phrase}' NOT found")
```

### 3. Check Detection in Real Text

```python
text = """
The President Director reported that gross production reached 
150,000 bopd under our production sharing contract.
"""

detected = detector.detect_phrases(text)
print(f"Detected {len(detected)} phrases:")
for phrase, start, end in detected:
    print(f"  - '{phrase}' at position {start}-{end}")
```

Expected output:
```
Detected 3 phrases:
  - 'president director' at position 4-21
  - 'gross production' at position 36-52
  - 'bopd' at position 68-72
  - 'production sharing contract' at position 82-111
```

### 4. Industry-Specific Stopwords

Consider adding Indonesian filler words to stopwords:

```json
{
  "financial": [
    "quarter", "fiscal", "call",
    "yang", "dan", "dari", "untuk",
    "adalah", "dengan", "pada", "ini", "itu"
  ]
}
```

---

## 📁 Complete File Placement Checklist

### Step 1: Create Directory Structure
```bash
mkdir -p data/nlp_config
mkdir -p data/dictionaries/loughran_mcdonald
```

### Step 2: Place LM Dictionary (One Time)
```bash
# You download this file from:
# https://sraf.nd.edu/loughranmcdonald-master-dictionary/
# Save it anywhere, then process it:

python scripts/download_dictionaries.py --process \
    ~/Downloads/LoughranMcDonald_MasterDictionary_1993-2024.csv

# This creates 7 .txt files in data/dictionaries/loughran_mcdonald/
```

### Step 3: Place NLP Config Files
```bash
# Copy the JSON files
cp financial_phrases.json data/nlp_config/
cp oil_gas_phrases.json data/nlp_config/
cp indonesian_titles.json data/nlp_config/
cp custom_stopwords.json data/nlp_config/
```

### Step 4: Verify
```bash
# Check LM dictionaries
ls -la data/dictionaries/loughran_mcdonald/
# Should show 7 .txt files

# Check NLP configs
ls -la data/nlp_config/
# Should show 4 .json files

# Verify with script
python scripts/setup_nlp.py --verify
```

### Step 5: Test
```bash
# Test phrase detection
python -c "
from pathlib import Path
from src.nlp.advanced_preprocessing import FinancialPhraseDetector

files = [
    Path('data/nlp_config/financial_phrases.json'),
    Path('data/nlp_config/oil_gas_phrases.json'),
    Path('data/nlp_config/indonesian_titles.json')
]

detector = FinancialPhraseDetector(phrases_files=files)
print(f'Loaded {len(detector.phrases)} total phrases')
"
```

Expected output:
```
Loaded 200 phrases from financial_phrases.json
Loaded 450 phrases from oil_gas_phrases.json
Loaded 150 phrases from indonesian_titles.json
Loaded 800 total phrases
```

---

## 🔍 Quick Reference

### File Locations

| File Type | Location | Purpose |
|-----------|----------|---------|
| **LM Dictionary CSV/XLSX** | Anywhere (temp) | Source file you download |
| **Processed LM dictionaries** | `data/dictionaries/loughran_mcdonald/*.txt` | Auto-created by script |
| **Phrase configs** | `data/nlp_config/*.json` | Multi-word phrases |
| **Stopwords config** | `data/nlp_config/custom_stopwords.json` | Stopword rules |

### Phrase Files Summary

| File | Phrases | Focus |
|------|---------|-------|
| `financial_phrases.json` | ~200 | General financial terms |
| `oil_gas_phrases.json` | ~450 | Oil & gas E&P operations |
| `indonesian_titles.json` | ~150 | Indonesian job titles (bilingual) |
| **Total** | **~800** | **Comprehensive coverage** |

---

## 🚀 Next Steps

1. **Place all files** in correct directories (see checklist above)
2. **Process LM Dictionary** (one-time setup)
3. **Update preprocessing code** to load multiple phrase files
4. **Test on sample transcripts** from Indonesian oil & gas companies
5. **Customize** as needed for your specific companies/terminology

---

## 💡 Tips

1. **Start comprehensive:** Load all three phrase files from the beginning
2. **Monitor detection:** Check which phrases are being detected in your transcripts
3. **Add custom phrases:** Edit JSON files to add company-specific terms
4. **Test bilingual:** Verify both Indonesian and English title variations work
5. **Combine with NER:** Use entity recognition to identify company and executive names

---

## ❓ Questions?

- **Q: Can I add more phrases?**
  - A: Yes! Just edit the JSON files directly

- **Q: What if a phrase isn't being detected?**
  - A: Check it's in the JSON file and in lowercase

- **Q: Do I need all three files?**
  - A: For Indonesian O&G companies, yes. For other industries, customize as needed

- **Q: Where does the LM dictionary CSV go?**
  - A: Anywhere temporarily. The script reads it once and creates the .txt files in `data/dictionaries/loughran_mcdonald/`
