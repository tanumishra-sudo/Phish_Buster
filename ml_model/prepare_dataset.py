"""
Dataset Preparation and Cleaning Module
Handles multiple CSV formats and performs data validation/cleaning
"""

import pandas as pd
import numpy as np
from urllib.parse import urlparse
import re


def prepare_dataset(input_csv, output_csv='phishing_urls_clean.csv'):
    """
    Load, clean, and prepare phishing dataset
    
    Args:
        input_csv (str): Path to input CSV file
        output_csv (str): Path to save cleaned dataset
        
    Returns:
        pd.DataFrame: Cleaned dataset
    """
    print("\n" + "="*80)
    print("📊 DATASET PREPARATION AND CLEANING")
    print("="*80 + "\n")
    
    print(f"📂 Loading dataset: {input_csv}\n")
    
    try:
        
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_csv, encoding=encoding, on_bad_lines='skip')
                used_encoding = encoding
                print(f"✅ Successfully loaded with {encoding} encoding")
                break
            except Exception as e:
                continue
        
        if df is None:
            print("❌ Failed to load CSV with any encoding")
            return None
        
        print(f"📈 Initial dataset shape: {df.shape}")
        print(f"📋 Columns: {df.columns.tolist()}\n")
        
        
        print("🔍 Identifying URL and Label columns...\n")
        
        url_col, label_col = identify_columns(df)
        
        if url_col is None:
            print("❌ Could not identify URL column")
            return None
        
        
        if 'PHISING URL' in df.columns and 'SAFE URL' in df.columns:
            print("📌 Detected PHISHING URL / SAFE URL format\n")
            data = []
            
           
            phishing_urls = df['PHISING URL'].dropna()
            print(f"   Processing {len(phishing_urls)} phishing URLs...")
            for url in phishing_urls:
                if pd.notna(url) and str(url).strip():
                    data.append({'url': str(url).strip(), 'label': 1})
            
        
            safe_urls = df['SAFE URL'].dropna()
            print(f"   Processing {len(safe_urls)} legitimate URLs...\n")
            for url in safe_urls:
                if pd.notna(url) and str(url).strip():
                    data.append({'url': str(url).strip(), 'label': 0})
            
            df = pd.DataFrame(data)
        else:
           
            if label_col is None:
                print("   No label column found, using default labels (0 = legitimate)\n")
                df['label'] = 0
                label_col = 'label'
            
            df = df.rename(columns={url_col: 'url', label_col: 'label'})
            df = df[['url', 'label']]
        
       
        
        print("🧹 Cleaning dataset...\n")
        
       
        initial_size = len(df)
        df = df.dropna(subset=['url', 'label'])
        print(f"   Removed {initial_size - len(df):,} rows with NaN values")
        
       
        before_empty = len(df)
        df = df[df['url'].str.strip() != '']
        print(f"   Removed {before_empty - len(df):,} empty URLs")
        
       
        print(f"   Validating URLs...")
        df = validate_urls(df)
        print(f"   ✅ {len(df):,} valid URLs")
        
       
        print(f"   Normalizing labels...")
        df['label'] = df['label'].apply(normalize_label)
        df = df[df['label'].isin([0, 1])]
        print(f"   ✅ Labels normalized\n")
        
       
        print(f"   Removing duplicates...")
        before_dedup = len(df)
        df = df.drop_duplicates(subset=['url'])
        print(f"   Removed {before_dedup - len(df):,} duplicate URLs\n")
        
        
        
        print("📊 CLASS DISTRIBUTION")
        print("="*80)
        
        legitimate = len(df[df['label'] == 0])
        phishing = len(df[df['label'] == 1])
        total = len(df)
        
        print(f"Legitimate URLs: {legitimate:,} ({legitimate/total*100:.2f}%)")
        print(f"Phishing URLs:   {phishing:,} ({phishing/total*100:.2f}%)")
        print(f"Total URLs:      {total:,}\n")
        
        
        balance_ratio = min(legitimate, phishing) / max(legitimate, phishing) if max(legitimate, phishing) > 0 else 0
        
        if balance_ratio > 0.8:
            print("✅ Dataset is WELL-BALANCED (>80% balance ratio)")
        elif balance_ratio > 0.6:
            print("⚠️  Dataset is SOMEWHAT IMBALANCED (60-80% balance ratio)")
        else:
            print("❌ Dataset is HIGHLY IMBALANCED (<60% balance ratio)")
            print("   → Consider using class_weight='balanced' in RandomForest\n")
        
       
        
        print("\n📈 URL STATISTICS")
        print("="*80)
        
        df['url_length'] = df['url'].str.len()
        
        print(f"URL Length Statistics:")
        print(f"   Min: {df['url_length'].min()}")
        print(f"   Max: {df['url_length'].max()}")
        print(f"   Mean: {df['url_length'].mean():.2f}")
        print(f"   Median: {df['url_length'].median():.0f}\n")
        
        
        df = df.drop('url_length', axis=1)
        
   
        
        print("💾 SAVING DATASET")
        print("="*80)
        
        df.to_csv(output_csv, index=False)
        print(f"✅ Dataset saved: {output_csv}")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Size: {len(df) * 2 / 1024:.2f} KB\n")
        
        print("="*80)
        print("✨ DATASET PREPARATION COMPLETE!")
        print("="*80 + "\n")
        
        return df
        
    except Exception as e:
        print(f"❌ Error preparing dataset: {e}")
        import traceback
        traceback.print_exc()
        return None


def identify_columns(df):
    """
    Identify URL and label columns by common names
    
    Args:
        df (pd.DataFrame): Dataset
        
    Returns:
        tuple: (url_column, label_column) or (None, None)
    """
    url_candidates = ['url', 'URL', 'urls', 'URLs', 'webpage', 'link', 'website', 
                     'Url', 'website_url', 'web_address']
    label_candidates = ['label', 'Label', 'class', 'Class', 'target', 'phishing',
                       'type', 'classification', 'Status', 'status', 'category']
    
    url_col = None
    label_col = None
    
 
    for col in url_candidates:
        if col in df.columns:
            url_col = col
            print(f"   ✓ URL column: '{url_col}'")
            break
    
   
    for col in label_candidates:
        if col in df.columns:
            label_col = col
            print(f"   ✓ Label column: '{label_col}'")
            break
    
   
    if url_col is None:
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = str(df[col].iloc[0]).lower()
                if 'http' in sample or ('.' in sample and len(sample) > 10):
                    url_col = col
                    print(f"   ✓ URL column (auto-detected): '{url_col}'")
                    break
    
    if label_col is None:
       
        label_col = df.columns[-1]
        print(f"   ✓ Label column (auto-detected): '{label_col}'")
    
    return url_col, label_col


def validate_urls(df):
    """
    Remove invalid URLs
    
    Args:
        df (pd.DataFrame): Dataset with 'url' column
        
    Returns:
        pd.DataFrame: Dataset with only valid URLs
    """
    def is_valid_url(url):
        try:
            url_str = str(url).strip()
            
            
            if not url_str or len(url_str) < 4:
                return False
            
            
            result = urlparse(url_str)
            
            
            if not result.netloc:
                return False
            
            return True
            
        except:
            return False
    
    initial_count = len(df)
    df['valid'] = df['url'].apply(is_valid_url)
    df = df[df['valid'] == True].drop('valid', axis=1)
    removed = initial_count - len(df)
    
    return df


def normalize_label(label):
    """
    Convert label to binary (0 = legitimate, 1 = phishing)
    
    Args:
        label: Label value (string, int, etc.)
        
    Returns:
        int: 0 or 1
    """
    label_str = str(label).lower().strip()
    
    phishing_indicators = ['phishing', '1', 'phish', 'malicious', 'suspicious', 
                          'bad', 'attack', 'fraud', 'scam']
    legitimate_indicators = ['legitimate', '0', 'legit', 'safe', 'benign', 
                            'good', 'clean', 'authentic']
    
    if any(x in label_str for x in phishing_indicators):
        return 1
    elif any(x in label_str for x in legitimate_indicators):
        return 0
    else:
        try:
            val = int(label)
            return 1 if val > 0 else 0
        except:
            return 0


if __name__ == "__main__":
 
    df = prepare_dataset(
        'dataset/phishing_urls_clean.csv',
        'dataset/phishing_urls_clean.csv'
    )
    
    if df is not None:
        print("✅ Dataset ready for training!")