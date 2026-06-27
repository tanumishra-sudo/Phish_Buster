"""
Prediction Script for Phishing Detection
Loads trained model and scaler, makes predictions on new URLs
"""

import sys
import json
import pickle
import numpy as np
import os
from feature_extraction import extract_features, get_feature_names


# Model and scaler paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'trained_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'scaler.pkl')
METADATA_PATH = os.path.join(os.path.dirname(__file__), 'model_metadata.pkl')


def load_model_and_scaler():
    """
    Load trained model and feature scaler
    
    Returns:
        tuple: (model, scaler) or (None, None) on error
    """
    try:
        # Load model
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        # Load scaler
        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}")
        
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        
        return model, scaler
        
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": f"Failed to load model: {str(e)}",
            "prediction": "error",
            "confidence": 0
        }))
        return None, None


def predict_url(url, model, scaler):
    """
    Predict if URL is phishing or legitimate
    
    Args:
        url (str): URL to analyze
        model: Trained RandomForest model
        scaler: StandardScaler for feature normalization
        
    Returns:
        dict: Prediction result with confidence and details
    """
    try:
        # Validate URL
        if not url or len(str(url).strip()) == 0:
            return {
                "status": "error",
                "error": "Empty URL provided",
                "prediction": "error",
                "confidence": 0
            }
        
        # Extract features
        features_dict = extract_features(str(url))
        
        # Convert to feature array in correct order
        feature_names = get_feature_names()
        feature_array = np.array([[features_dict[fname] for fname in feature_names]])
        
        # Scale features (CRITICAL: must use same scaler as training)
        feature_array_scaled = scaler.transform(feature_array)
        
        # Make prediction
        raw_prediction = model.predict(feature_array_scaled)[0]
        probabilities = model.predict_proba(feature_array_scaled)[0]
        
        # Get confidence
        confidence = max(probabilities) * 100
        phishing_probability = probabilities[1] * 100  # Probability of phishing
        legitimate_probability = probabilities[0] * 100  # Probability of legitimate
        
        # Map prediction to label
        label = "Phishing" if raw_prediction == 1 else "Legitimate"
        
        # Determine risk level
        if phishing_probability >= 80:
            risk_level = "CRITICAL"
        elif phishing_probability >= 60:
            risk_level = "HIGH"
        elif phishing_probability >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        result = {
            "status": "success",
            "url": url,
            "prediction": label,
            "confidence": round(confidence, 2),
            "phishing_probability": round(phishing_probability, 2),
            "legitimate_probability": round(legitimate_probability, 2),
            "risk_level": risk_level,
            "raw_prediction": int(raw_prediction),
            "features": features_dict,
            "top_features": get_top_features(features_dict, model)
        }
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "prediction": "error",
            "confidence": 0,
            "url": url
        }


def get_top_features(features_dict, model):
    """
    Get top 5 features that influenced the prediction
    
    Args:
        features_dict (dict): Extracted features
        model: Trained model
        
    Returns:
        dict: Top 5 features with their importance
    """
    try:
        feature_names = get_feature_names()
        importances = model.feature_importances_
        
        # Get top 5 features
        top_indices = np.argsort(importances)[::-1][:5]
        
        top_features = {}
        for idx in top_indices:
            feature_name = feature_names[idx]
            top_features[feature_name] = {
                "value": features_dict[feature_name],
                "importance": round(float(importances[idx]), 4)
            }
        
        return top_features
        
    except:
        return {}


def main():
    """
    Main function - handle command line arguments
    """
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "error": "No URL provided. Usage: python predict.py <URL>",
            "prediction": "error"
        }))
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Load model and scaler
    model, scaler = load_model_and_scaler()
    if model is None or scaler is None:
        sys.exit(1)
    
    # Make prediction
    result = predict_url(url, model, scaler)
    
    # Print JSON result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()