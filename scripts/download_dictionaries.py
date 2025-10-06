"""
Script to process Loughran-McDonald Master Dictionary from CSV/XLSX
"""
import pandas as pd
from pathlib import Path
import sys
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


def process_lm_master_dictionary(file_path: str, output_format: str = 'txt'):
    """
    Process the LM Master Dictionary CSV/XLSX file
    
    Args:
        file_path: Path to the master dictionary file
        output_format: 'txt' or 'json'
    """
    dict_dir = settings.DICTIONARIES_DIR / "loughran_mcdonald"
    dict_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing Loughran-McDonald Master Dictionary...")
    print(f"Input: {file_path}")
    print(f"Output: {dict_dir}\n")
    
    # Read the file
    file_path_obj = Path(file_path)
    if file_path_obj.suffix == '.csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    elif file_path_obj.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path_obj.suffix}")
    
    print(f"Loaded {len(df)} words from master dictionary\n")
    
    # Categories to extract
    categories = [
        'Negative', 'Positive', 'Uncertainty', 'Litigious',
        'Strong_Modal', 'Weak_Modal', 'Constraining'
    ]
    
    # Extract words for each category
    for category in categories:
        if category in df.columns:
            # Get words where category column > 0
            category_words = df[df[category] > 0]['Word'].tolist()
            
            # Convert to lowercase and remove duplicates
            category_words = sorted(set(word.lower() for word in category_words))
            
            # Save to file
            output_file = dict_dir / f"{category.lower()}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                for word in category_words:
                    f.write(f"{word}\n")
            
            print(f"✓ Created {category.lower()}.txt ({len(category_words)} words)")
        else:
            print(f"⚠️  Warning: Column '{category}' not found in dictionary file")
    
    print(f"\n✓ Dictionary processing complete!")
    print(f"Files saved to: {dict_dir}")


def create_starter_dictionaries():
    """Create minimal starter dictionaries for testing"""
    dict_dir = settings.DICTIONARIES_DIR / "loughran_mcdonald"
    dict_dir.mkdir(parents=True, exist_ok=True)
    
    LM_STARTER = {
        'negative': [
            'loss', 'losses', 'lost', 'decline', 'declined', 'declining', 'decrease',
            'decreased', 'decreasing', 'adverse', 'adversely', 'negative', 'negatively',
            'deteriorate', 'deteriorated', 'deteriorating', 'weak', 'weakness', 'weaken',
            'weakening', 'fail', 'failed', 'failure', 'failing', 'poor', 'poorly',
            'difficult', 'difficulty', 'challenge', 'challenged', 'challenging',
            'uncertainty', 'risk', 'risks', 'risky', 'concern', 'concerned', 'concerning',
            'problem', 'problems', 'issue', 'issues', 'deficit', 'shortage', 'shortages'
        ],
        'positive': [
            'profit', 'profits', 'profitable', 'profitability', 'growth', 'grow', 'growing',
            'grew', 'excellent', 'strong', 'stronger', 'strongest', 'improve', 'improved',
            'improving', 'improvement', 'increase', 'increased', 'increasing', 'gain',
            'gained', 'gains', 'benefit', 'benefits', 'benefited', 'success', 'successful',
            'successfully', 'achieve', 'achieved', 'achievement', 'good', 'better', 'best',
            'great', 'greater', 'greatest', 'leading', 'leader', 'opportunity',
            'opportunities', 'progress', 'advanced', 'advancement', 'favorable'
        ],
        'uncertainty': [
            'approximately', 'uncertain', 'uncertainty', 'depends', 'depending', 'dependent',
            'could', 'may', 'might', 'possibly', 'perhaps', 'probable', 'probably',
            'appears', 'appear', 'appearing', 'unclear', 'unknown', 'unpredictable',
            'indefinite', 'somewhere', 'somehow', 'almost', 'possible', 'possibility',
            'believe', 'believed', 'assumes', 'assumption', 'tentative', 'preliminary'
        ],
        'litigious': [
            'litigation', 'lawsuit', 'lawsuits', 'sue', 'sued', 'suing', 'plaintiff',
            'defendant', 'court', 'courts', 'trial', 'trials', 'regulatory', 'regulation',
            'regulations', 'compliance', 'compliant', 'investigate', 'investigation',
            'enforcement', 'penalty', 'penalties', 'fine', 'fines', 'illegal',
            'illegally', 'violation', 'violations', 'violate', 'violated', 'fraud',
            'fraudulent', 'settlement', 'settle', 'settled'
        ],
        'strong_modal': [
            'must', 'shall', 'will', 'always', 'definitely', 'certainly', 'clearly',
            'undoubtedly', 'inevitably', 'necessarily', 'absolutely', 'unquestionably',
            'assured', 'assure', 'assures', 'guarantee', 'guarantees', 'guaranteed'
        ],
        'weak_modal': [
            'might', 'could', 'may', 'possibly', 'perhaps', 'maybe', 'potentially',
            'probable', 'probably', 'sometimes', 'occasionally', 'appears', 'seem',
            'seems', 'seemed', 'would', 'should'
        ],
        'constraining': [
            'limited', 'limiting', 'limits', 'limit', 'restricted', 'restricting',
            'restriction', 'restrictions', 'restrict', 'constrained', 'constraining',
            'constraint', 'constraints', 'cannot', 'unable', 'difficulty', 'impede',
            'impeded', 'impediment', 'hamper', 'hampered', 'hinder', 'hindered',
            'prevent', 'prevented', 'preventing', 'bar', 'barred', 'barrier'
        ]
    }
    
    print("Creating starter dictionaries for testing...")
    print(f"Directory: {dict_dir}\n")
    
    for category, words in LM_STARTER.items():
        file_path = dict_dir / f"{category}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            for word in sorted(words):
                f.write(f"{word}\n")
        print(f"✓ Created {category}.txt ({len(words)} words)")
    
    print(f"\n✓ Starter dictionaries created!")
    print(f"\nNote: For production, process the full LM Master Dictionary:")
    print(f"  python scripts/download_dictionaries.py --process /path/to/LoughranMcDonald_MasterDictionary.csv")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process Loughran-McDonald Master Dictionary')
    parser.add_argument('--process', type=str, help='Path to LM Master Dictionary CSV/XLSX file')
    parser.add_argument('--create-starter', action='store_true', 
                       help='Create starter dictionaries for immediate use')
    
    args = parser.parse_args()
    
    if args.process:
        process_lm_master_dictionary(args.process)
    elif args.create_starter:
        create_starter_dictionaries()
    else:
        print("Loughran-McDonald Dictionary Setup")
        print("=" * 80)
        print("\nOptions:")
        print("  1. Process full dictionary: python scripts/download_dictionaries.py --process /path/to/LM_Dictionary.csv")
        print("  2. Create starter dictionaries: python scripts/download_dictionaries.py --create-starter")
        print("\nUse option 1 for production, option 2 for testing.\n")
