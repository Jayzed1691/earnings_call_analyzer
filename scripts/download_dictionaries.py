"""
Script to download and set up Loughran-McDonald Master Dictionary
"""
import requests
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


# Loughran-McDonald dictionary word lists (sample)
# In production, these would be downloaded from official source
# For now, we'll create starter dictionaries

LM_DICTIONARIES = {
    'negative': [
        'loss', 'losses', 'lost', 'decline', 'declined', 'declining', 'decrease',
        'decreased', 'decreasing', 'adverse', 'adversely', 'negative', 'negatively',
        'deteriorate', 'deteriorated', 'deteriorating', 'weak', 'weakness', 'weaken',
        'weakening', 'fail', 'failed', 'failure', 'failing', 'poor', 'poorly',
        'difficult', 'difficulty', 'challenge', 'challenged', 'challenging', 'uncertain',
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
        'approximately', 'uncertain', 'uncertainty', 'risk', 'risks', 'risky',
        'depends', 'depending', 'dependent', 'could', 'may', 'might', 'possibly',
        'perhaps', 'probable', 'probably', 'appears', 'appear', 'appearing',
        'unclear', 'unknown', 'unpredictable', 'indefinite', 'somewhere', 'somehow',
        'almost', 'possible', 'possibility', 'believe', 'believed', 'assumes',
        'assumption', 'tentative', 'preliminary'
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


def create_dictionaries():
    """Create Loughran-McDonald dictionary files"""
    dict_dir = settings.DICTIONARIES_DIR / "loughran_mcdonald"
    dict_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating Loughran-McDonald dictionaries...")
    print(f"Directory: {dict_dir}\n")
    
    for category, words in LM_DICTIONARIES.items():
        file_path = dict_dir / f"{category}.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for word in sorted(words):
                f.write(f"{word}\n")
        
        print(f"✓ Created {category}.txt ({len(words)} words)")
    
    print(f"\n✓ All dictionaries created successfully!")
    print(f"\nNote: These are starter dictionaries. For production use, download the")
    print(f"complete Loughran-McDonald Master Dictionary from:")
    print(f"https://sraf.nd.edu/loughranmcdonald-master-dictionary/")


def download_official_dictionaries():
    """
    Placeholder for downloading official LM dictionary
    
    Note: The official dictionary requires registration and is updated quarterly.
    Users should download manually from: https://sraf.nd.edu/loughranmcdonald-master-dictionary/
    """
    print("\nFor the official, complete Loughran-McDonald Master Dictionary:")
    print("1. Visit: https://sraf.nd.edu/loughranmcdonald-master-dictionary/")
    print("2. Download the latest version")
    print("3. Extract word lists for each category")
    print("4. Place .txt files in:", settings.DICTIONARIES_DIR / "loughran_mcdonald")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Set up Loughran-McDonald dictionaries')
    parser.add_argument('--create-starter', action='store_true', 
                       help='Create starter dictionaries for immediate use')
    
    args = parser.parse_args()
    
    if args.create_starter:
        create_dictionaries()
    else:
        print("Loughran-McDonald Dictionary Setup")
        print("=" * 80)
        print("\nOptions:")
        print("  1. Create starter dictionaries: python scripts/download_dictionaries.py --create-starter")
        print("  2. Download official dictionary (manual process)")
        print("\nChoose option 1 for immediate testing, option 2 for production use.\n")
        
        download_official_dictionaries()
