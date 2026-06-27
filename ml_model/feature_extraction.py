"""
Enhanced Feature Extraction Module for Phishing Detection
Extracts 24+ sophisticated features from URLs for ML model prediction
Includes: entropy analysis, domain reputation, suspicious patterns, keyword detection
"""

from urllib.parse import urlparse
import re
import numpy as np
from collections import Counter

def extract_features(url):
    """
    Extract 24+ features from URL for ML model
    
    Returns:
        dict: Dictionary of extracted features with feature names as keys
    """
    features = {}
    
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        query = parsed_url.query.lower()
        full_url = url.lower()
        
        # ============ BASIC URL STRUCTURE FEATURES ============
        
        # 1. URL Length (phishing URLs often have unusual lengths)
        features['url_length'] = len(url)
        
        # 2. Domain Length
        features['domain_length'] = len(domain)
        
        # 3. Path Length
        features['path_length'] = len(path)
        
        # 4. Number of dots in URL (subdomains indicator)
        features['num_dots'] = url.count('.')
        
        # ============ DOMAIN ANALYSIS FEATURES ============
        
        # 5. Number of hyphens in domain (common in phishing URLs)
        features['num_hyphens_domain'] = domain.count('-')
        
        # 6. Number of subdomains (phishing often uses suspicious subdomains)
        domain_parts = domain.split('.')
        features['num_subdomains'] = max(0, len(domain_parts) - 2)
        
        # 7. Domain Entropy - high entropy indicates random/suspicious domain
        features['domain_entropy'] = calculate_entropy(domain)
        
        # 8. Presence of dash in domain (brand-mimicry indicator)
        features['has_dash_in_domain'] = 1 if '-' in domain else 0
        
        # 9. Double dots (malformed domain)
        features['double_dot'] = 1 if '..' in url else 0
        
        # ============ TLD AND IP ANALYSIS ============
        
        # 10. Suspicious TLD detection
        if len(domain_parts) > 0:
            tld = domain_parts[-1]
            suspicious_tlds = ['tk', 'ml', 'ga', 'cf', 'info', 'xyz', 'top', 'work', 
                             'download', 'science', 'date', 'party', 'stream', 'gq']
            features['suspicious_tld'] = 1 if tld in suspicious_tlds else 0
        else:
            features['suspicious_tld'] = 0
        
        # 11. Presence of IP address instead of domain
        features['has_ip_address'] = 1 if is_ip_address(domain) else 0
        
        # 12. Obfuscated IP detection (hex, octal formats)
        features['has_obfuscated_ip'] = 1 if is_obfuscated_ip(domain) else 0
        
        # ============ PROTOCOL AND CONNECTION FEATURES ============
        
        # 13. HTTPS usage (legitimate sites typically use HTTPS)
        features['uses_https'] = 1 if parsed_url.scheme == 'https' else 0
        
        # 14. Port detection (explicit ports are suspicious)
        features['has_explicit_port'] = 1 if parsed_url.port else 0
        
        # ============ SPECIAL CHARACTER AND ENCODING ============
        
        # 15. Presence of @ symbol (redirect in URL)
        features['has_at_symbol'] = 1 if '@' in url else 0
        
        # 16. Presence of // in unusual places
        features['double_slash_count'] = url.count('//') - 1  # -1 for protocol
        
        # 17. Percent encoding (obfuscation indicator)
        features['percent_encoding_count'] = url.count('%')
        
        # 18. Number of query parameters
        features['query_param_count'] = len(query.split('&')) if query else 0
        
        # 19. Number of semicolons (parameter separator)
        features['semicolon_count'] = url.count(';')
        
        # 20. Ampersand count
        features['ampersand_count'] = url.count('&')
        
        # ============ CHARACTER DISTRIBUTION FEATURES ============
        
        # 21. Digit ratio (phishing often uses digits for obfuscation)
        digit_count = sum(1 for c in url if c.isdigit())
        features['digit_ratio'] = digit_count / len(url) if len(url) > 0 else 0
        
        # 22. Uppercase character ratio
        uppercase_count = sum(1 for c in url if c.isupper())
        features['uppercase_ratio'] = uppercase_count / len(url) if len(url) > 0 else 0
        
        # 23. Vowel to consonant ratio (unusual patterns indicate obfuscation)
        vowel_count = sum(1 for c in url.lower() if c in 'aeiou')
        consonant_count = sum(1 for c in url.lower() if c.isalpha() and c not in 'aeiou')
        features['vowel_consonant_ratio'] = vowel_count / max(consonant_count, 1)
        
        # ============ URL PATH FEATURES ============
        
        # 24. Path depth (number of directories)
        features['path_depth'] = len([p for p in path.split('/') if p])
        
        # 25. Ratio of path to domain length
        features['path_domain_ratio'] = len(path) / max(len(domain), 1)
        
        # ============ SUSPICIOUS CONTENT PATTERNS ============
        
        # 26. Presence of suspicious keywords
        suspicious_keywords = [
            'verify', 'confirm', 'account', 'update', 'urgent', 'action',
            'suspicious', 'secure', 'click', 'login', 'payment', 'click',
            'bank', 'amazon', 'apple', 'google', 'microsoft', 'paypal',
            'password', 'credential', 'sensitive', 'information', 'alert'
        ]
        features['has_suspicious_keywords'] = 1 if any(
            keyword in full_url for keyword in suspicious_keywords
        ) else 0
        
        # 27. URL shortener detection
        shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly', 'short.link',
                     'buff.ly', 'adf.ly', 'cutt.ly', 'is.gd']
        features['is_url_shortener'] = 1 if any(
            shortener in domain for shortener in shorteners
        ) else 0
        
        # 28. International domain (punycode/IDN) - homograph attack indicator
        features['is_international_domain'] = 1 if 'xn--' in domain else 0
        
        # ============ SPECIAL FEATURES ============
        
        # 29. Having TLD (basic validation)
        features['has_tld'] = 1 if '.' in domain else 0
        
        # 30. Presence of query string (legitimate sites often have them)
        features['has_query_string'] = 1 if query else 0
        
        # 31. Total special characters count
        special_chars = len(re.findall(r'[!@#$%^&*()_+=\[\]{};:\'",.<>?/\\|`~-]', url))
        features['special_char_count'] = special_chars
        
        # 32. Ratio of special characters
        features['special_char_ratio'] = special_chars / len(url) if len(url) > 0 else 0
        
    except Exception as e:
        print(f"⚠️ Error extracting features for URL: {e}")
        return get_default_features()
    
    return features


def calculate_entropy(text):
    """
    Calculate Shannon entropy of text
    Higher entropy = more random/suspicious
    
    Args:
        text (str): Text to analyze
        
    Returns:
        float: Entropy value (0-8 typically)
    """
    if not text:
        return 0.0
    
    # Calculate frequency of each character
    char_freq = Counter(text.lower())
    
    # Calculate entropy
    entropy = 0.0
    text_len = len(text)
    
    for count in char_freq.values():
        probability = count / text_len
        entropy -= probability * np.log2(probability)
    
    return entropy


def is_ip_address(domain):
    """
    Check if domain is an IPv4 address
    
    Args:
        domain (str): Domain to check
        
    Returns:
        bool: True if domain is IP address
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if re.match(pattern, domain):
        try:
            # Validate IP octets are in valid range
            octets = domain.split('.')
            return all(0 <= int(octet) <= 255 for octet in octets)
        except (ValueError, AttributeError):
            return False
    
    return False


def is_obfuscated_ip(domain):
    """
    Check for obfuscated IP addresses (hex, octal, decimal formats)
    
    Args:
        domain (str): Domain to check
        
    Returns:
        bool: True if domain appears to be obfuscated IP
    """
    # Hexadecimal IP (e.g., 0xC0A80101)
    if re.match(r'^0x[0-9a-fA-F]+$', domain):
        return True
    
    # Octal format (e.g., 0300.0250.0001.0001)
    if re.match(r'^0\d+\.\d+\.\d+\.\d+$', domain):
        return True
    
    # Decimal format (e.g., 3232235777 = 192.168.1.1)
    if re.match(r'^\d{10,}$', domain) and len(domain) > 9:
        return True
    
    return False


def get_default_features():
    """
    Return dictionary with all features set to 0 (for error handling)
    
    Returns:
        dict: All features with value 0
    """
    return {
        'url_length': 0, 'domain_length': 0, 'path_length': 0,
        'num_dots': 0, 'num_hyphens_domain': 0, 'num_subdomains': 0,
        'domain_entropy': 0, 'has_dash_in_domain': 0, 'double_dot': 0,
        'suspicious_tld': 0, 'has_ip_address': 0, 'has_obfuscated_ip': 0,
        'uses_https': 0, 'has_explicit_port': 0, 'has_at_symbol': 0,
        'double_slash_count': 0, 'percent_encoding_count': 0, 'query_param_count': 0,
        'semicolon_count': 0, 'ampersand_count': 0, 'digit_ratio': 0,
        'uppercase_ratio': 0, 'vowel_consonant_ratio': 0, 'path_depth': 0,
        'path_domain_ratio': 0, 'has_suspicious_keywords': 0, 'is_url_shortener': 0,
        'is_international_domain': 0, 'has_tld': 0, 'has_query_string': 0,
        'special_char_count': 0, 'special_char_ratio': 0
    }


def get_feature_names():
    """
    Get ordered list of all feature names
    IMPORTANT: Must match order of features in extract_features()
    
    Returns:
        list: Feature names in correct order
    """
    return [
        'url_length', 'domain_length', 'path_length', 'num_dots',
        'num_hyphens_domain', 'num_subdomains', 'domain_entropy',
        'has_dash_in_domain', 'double_dot', 'suspicious_tld',
        'has_ip_address', 'has_obfuscated_ip', 'uses_https',
        'has_explicit_port', 'has_at_symbol', 'double_slash_count',
        'percent_encoding_count', 'query_param_count', 'semicolon_count',
        'ampersand_count', 'digit_ratio', 'uppercase_ratio',
        'vowel_consonant_ratio', 'path_depth', 'path_domain_ratio',
        'has_suspicious_keywords', 'is_url_shortener', 'is_international_domain',
        'has_tld', 'has_query_string', 'special_char_count', 'special_char_ratio'
    ]


if __name__ == "__main__":
    # Test feature extraction
    test_urls = [
        "https://www.google.com/search?q=test",
        "http://192.168.1.1/admin",
        "https://amaz0n-verify-account.tk/login",
        "http://bit.ly/phishing",
    ]
    
    print("Testing feature extraction...\n")
    for url in test_urls:
        features = extract_features(url)
        print(f"URL: {url}")
        print(f"Features extracted: {len(features)}")
        print(f"Sample features: url_length={features['url_length']}, "
              f"has_ip={features['has_ip_address']}, "
              f"domain_entropy={features['domain_entropy']:.2f}\n")