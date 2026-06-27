"""
Complete Training Pipeline for Phishing Detection Model
Includes: data loading, feature extraction, scaling, hyperparameter tuning,
evaluation metrics, feature importance analysis, and model serialization
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, f1_score, confusion_matrix, 
                            precision_score, recall_score, roc_auc_score)
from feature_extraction import extract_features, get_feature_names

warnings.filterwarnings('ignore')


def load_and_prepare_dataset(input_csv):
    """
    Load dataset from CSV and handle various formats
    
    Args:
        input_csv (str): Path to CSV file
        
    Returns:
        pd.DataFrame: Clean dataset with 'url' and 'label' columns
    """
    print("\n" + "="*80)
    print("📂 LOADING DATASET")
    print("="*80 + "\n")
    
    try:
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_csv, encoding=encoding, on_bad_lines='skip')
                print(f"✅ Loaded with {encoding} encoding")
                break
            except:
                continue
        
        if df is None:
            raise ValueError("Could not load CSV with any encoding")
        
        print(f"📊 Initial shape: {df.shape}")
        print(f"📋 Columns: {df.columns.tolist()}\n")
        
        
        url_col = None
        label_col = None
        
        url_candidates = ['url', 'URL', 'urls', 'URLs', 'webpage', 'link', 'website', 'Url']
        for col in url_candidates:
            if col in df.columns:
                url_col = col
                break
        
        label_candidates = ['label', 'Label', 'class', 'Class', 'target', 'phishing', 
                           'type', 'classification', 'Status', 'status']
        for col in label_candidates:
            if col in df.columns:
                label_col = col
                break
        
        if 'PHISING URL' in df.columns and 'SAFE URL' in df.columns:
            print("📌 Detected PHISHING URL / SAFE URL format\n")
            data = []
            
            if pd.notna(df['PHISING URL']).any():
                for url in df['PHISING URL'].dropna():
                    if str(url).strip():
                        data.append({'url': str(url).strip(), 'label': 1})
            
            if pd.notna(df['SAFE URL']).any():
                for url in df['SAFE URL'].dropna():
                    if str(url).strip():
                        data.append({'url': str(url).strip(), 'label': 0})
            
            df = pd.DataFrame(data)
        
        if url_col is None:
            if len(df.columns) > 0:
                url_col = df.columns[0]
                print(f"⚠️  Auto-detected URL column: {url_col}\n")
            else:
                raise ValueError("No suitable URL column found")
        
        if label_col is None:
            if len(df.columns) > 1:
                label_col = df.columns[-1]
                print(f"⚠️  Auto-detected Label column: {label_col}\n")
            else:
                raise ValueError("No suitable Label column found")
        
        df = df.rename(columns={url_col: 'url', label_col: 'label'})
        df = df[['url', 'label']]
        
        
        print("🧹 Cleaning dataset...\n")
        
        initial_len = len(df)
        df = df.dropna(subset=['url', 'label'])
        print(f"   Removed {initial_len - len(df)} rows with NaN values")
        
        before_dedup = len(df)
        df = df.drop_duplicates(subset=['url'])
        print(f"   Removed {before_dedup - len(df)} duplicate URLs")
        
        df['label'] = df['label'].apply(_normalize_label)
        
        df = df[df['label'].isin([0, 1])]
        print(f"   Final clean dataset: {len(df)} URLs\n")
        
        
        legitimate = len(df[df['label'] == 0])
        phishing = len(df[df['label'] == 1])
        total = len(df)
        
        print("📊 Class Distribution:")
        print(f"   Legitimate: {legitimate:,} ({legitimate/total*100:.2f}%)")
        print(f"   Phishing:   {phishing:,} ({phishing/total*100:.2f}%)")
        print(f"   Total:      {total:,}\n")
        
        if min(legitimate, phishing) / max(legitimate, phishing) < 0.7:
            print("⚠️  WARNING: Dataset is imbalanced - using class_weight='balanced'\n")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None


def _normalize_label(label):
    """Convert label to 0 (legitimate) or 1 (phishing)"""
    label_str = str(label).lower().strip()
    
    phishing_indicators = ['phishing', '1', 'phish', 'malicious', 'suspicious', 'bad']
    legitimate_indicators = ['legitimate', '0', 'legit', 'safe', 'benign', 'good']
    
    if any(x in label_str for x in phishing_indicators):
        return 1
    elif any(x in label_str for x in legitimate_indicators):
        return 0
    else:
        try:
            return int(label)
        except:
            return 0


def extract_features_batch(urls):
    """
    Extract features from batch of URLs
    
    Args:
        urls (list): List of URLs
        
    Returns:
        tuple: (feature_array, failed_count)
    """
    print("\n🔧 Extracting Features")
    print("="*80)
    
    X = []
    failed_count = 0
    
    for idx, url in enumerate(urls):
        if idx % 2000 == 0 and idx > 0:
            print(f"   Progress: {idx:,}/{len(urls):,} ({idx/len(urls)*100:.1f}%)")
        
        try:
            features = extract_features(str(url))
            feature_vector = [features[fname] for fname in get_feature_names()]
            X.append(feature_vector)
        except Exception as e:
            failed_count += 1
            X.append([0] * len(get_feature_names()))
    
    print(f"   ✅ Completed: {len(X):,} URLs processed")
    if failed_count > 0:
        print(f"   ⚠️  Failed: {failed_count} URLs\n")
    
    return np.array(X), failed_count


def train_model_full():
    """
    Complete training pipeline with hyperparameter optimization
    """
    print("\n" + "="*80)
    print("🤖 PHISHING DETECTION MODEL - TRAINING PIPELINE")
    print("="*80)
    
    
    df = load_and_prepare_dataset('dataset/phishing_urls_clean.csv')
    if df is None:
        return None
    
    
    X, failed_count = extract_features_batch(df['url'].values)
    y = df['label'].values
    
    print(f"✅ Features extracted: {X.shape}")
    print(f"   Shape: {X.shape[0]} samples × {X.shape[1]} features\n")
    
    
    print("📐 Scaling Features")
    print("="*80)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"✅ StandardScaler fitted")
    print(f"   Feature means: min={scaler.mean_.min():.4f}, max={scaler.mean_.max():.4f}")
    print(f"   Feature stds:  min={scaler.scale_.min():.4f}, max={scaler.scale_.max():.4f}\n")
    
    
    print("📊 Train-Test Split")
    print("="*80)
    
    if len(np.unique(y)) > 1:
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y,
            test_size=0.2,
            random_state=42
        )
    
    print(f"✅ Split completed")
    print(f"   Train: {len(X_train):,} samples")
    print(f"   Test:  {len(X_test):,} samples")
    print(f"   Train/Test ratio: {len(X_train)/len(X_test):.2f}\n")
    
    
    print("🔍 Hyperparameter Optimization (GridSearchCV)")
    print("="*80)
    
    param_grid = {
        'n_estimators': [150, 200, 250],
        'max_depth': [20, 25, 30],
        'min_samples_split': [8, 10, 12],
        'min_samples_leaf': [4, 5, 6],
        'max_features': ['sqrt', 'log2']
    }
    
    rf_base = RandomForestClassifier(
        random_state=42,
        class_weight='balanced',
        n_jobs=-1,
        verbose=0
    )
    
    grid_search = GridSearchCV(
        rf_base,
        param_grid,
        cv=5,
        scoring='f1',
        n_jobs=-1,
        verbose=1
    )
    
    print("   Starting grid search (this may take 10-30 minutes)...\n")
    grid_search.fit(X_train, y_train)
    
    print(f"\n✅ Grid search completed!")
    print(f"   Best F1-Score (CV): {grid_search.best_score_:.4f}")
    print(f"   Best Parameters: {grid_search.best_params_}\n")
    
    model = grid_search.best_estimator_
    
    
    print("🚀 Training Final Model")
    print("="*80)
    print(f"   Using best parameters: {grid_search.best_params_}\n")
    
    model.fit(X_train, y_train)
    print("✅ Final model trained!\n")
    
    
    print("📈 MODEL EVALUATION")
    print("="*80 + "\n")
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    try:
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    except:
        y_pred_proba = None
    
    
    train_acc = accuracy_score(y_train, y_pred_train)
    train_f1 = f1_score(y_train, y_pred_train, zero_division=0)
    
    print("TRAINING SET:")
    print(f"   Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
    print(f"   F1-Score: {train_f1:.4f}\n")
    
    
    test_acc = accuracy_score(y_test, y_pred_test)
    test_f1 = f1_score(y_test, y_pred_test, zero_division=0)
    test_precision = precision_score(y_test, y_pred_test, zero_division=0)
    test_recall = recall_score(y_test, y_pred_test, zero_division=0)
    
    print("TEST SET:")
    print(f"   Accuracy:  {test_acc:.4f} ({test_acc*100:.2f}%)")
    print(f"   F1-Score:  {test_f1:.4f}")
    print(f"   Precision: {test_precision:.4f}")
    print(f"   Recall:    {test_recall:.4f}")
    
    if y_pred_proba is not None:
        try:
            auc = roc_auc_score(y_test, y_pred_proba)
            print(f"   ROC-AUC:   {auc:.4f}")
        except:
            pass
    
    print()
    
    
    cm = confusion_matrix(y_test, y_pred_test)
    
    print("CONFUSION MATRIX:")
    print("                  Predicted Legitimate  Predicted Phishing")
    print(f"Actual Legitimate       {cm[0,0]:>6}                {cm[0,1]:>6}")
    print(f"Actual Phishing         {cm[1,0]:>6}                {cm[1,1]:>6}\n")
    
    if cm[0,0] + cm[0,1] > 0:
        tnr = cm[0,0] / (cm[0,0] + cm[0,1])
        print(f"True Negative Rate (Specificity): {tnr:.4f}")
    
    if cm[1,0] + cm[1,1] > 0:
        tpr = cm[1,1] / (cm[1,0] + cm[1,1])
        print(f"True Positive Rate (Sensitivity): {tpr:.4f}\n")
    
    
    print("🎯 FEATURE IMPORTANCE (Top 15)")
    print("="*80)
    
    feature_names = get_feature_names()
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:15]
    
    total_importance = importances[indices].sum()
    
    for i, idx in enumerate(indices, 1):
        importance_pct = (importances[idx] / total_importance) * 100
        bar = "█" * int(importance_pct / 2)
        print(f"{i:2d}. {feature_names[idx]:.<30} {importances[idx]:.4f} {bar}")
    
    print()
    
    
    print("💾 SAVING MODELS")
    print("="*80)
    
    try:
        
        model_path = 'trained_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f, protocol=4)
        
        model_size = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✅ Model saved: {model_path}")
        print(f"   Size: {model_size:.2f} MB")
        print(f"   Path: {os.path.abspath(model_path)}")
        

        scaler_path = 'scaler.pkl'
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f, protocol=4)
        
        scaler_size = os.path.getsize(scaler_path) / (1024 * 1024)
        print(f"\n✅ Scaler saved: {scaler_path}")
        print(f"   Size: {scaler_size:.4f} MB")
        print(f"   Path: {os.path.abspath(scaler_path)}")
        
       
        metadata = {
            'features': feature_names,
            'n_features': len(feature_names),
            'test_accuracy': float(test_acc),
            'test_f1': float(test_f1),
            'best_params': grid_search.best_params_,
            'class_distribution': {'legitimate': int((y==0).sum()), 'phishing': int((y==1).sum())}
        }
        
        metadata_path = 'model_metadata.pkl'
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f, protocol=4)
        
        print(f"\n✅ Metadata saved: {metadata_path}\n")
        
    except Exception as e:
        print(f"❌ Error saving models: {e}\n")
        return None
    
    print("="*80)
    print("✨ TRAINING COMPLETE!")
    print("="*80)
    print(f"\n📊 SUMMARY:")
    print(f"   Test Accuracy: {test_acc*100:.2f}%")
    print(f"   Test F1-Score: {test_f1:.4f}")
    print(f"   Model saved: {model_path}")
    print(f"   Scaler saved: {scaler_path}\n")
    
    return model, scaler


if __name__ == "__main__":
    train_model_full()