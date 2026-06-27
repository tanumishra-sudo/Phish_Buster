# PhishGuard — Phishing Website Detection using Machine Learning

![Cyber Security](https://img.shields.io/badge/Subject-Cyber%20Security-red)
![Node.js](https://img.shields.io/badge/Backend-Node.js%20%2B%20Express-339933)
![Python](https://img.shields.io/badge/ML-Python%20%2B%20Scikit--learn-blue)
![ML](https://img.shields.io/badge/Model-Random%20Forest-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 📌 Project Overview

Phishing is a cyber-attack where attackers deceive users into revealing sensitive information. This project implements a sophisticated **Machine Learning-based detection system** that analyzes URL patterns, domain characteristics, and security features to classify websites as **Legitimate** or **Phishing** in real-time.

The system uses a **Node.js (Express)** backend that bridges to a **Python (Scikit-learn)** ML model via child process spawning, with a clean **vanilla HTML/CSS/JS** frontend.

## 🛠️ Tech Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) | Single-page interface — no framework |
| **Backend** | Node.js + Express.js | REST API server with security middleware |
| **ML Model** | Python + Scikit-learn | Random Forest classifier with GridSearchCV tuning |
| **Node ↔ Python Bridge** | `child_process.spawn` | Backend spawns Python `predict.py` for each prediction |
| **Model Serialization** | Pickle (`.pkl`) | Trained model, scaler, and metadata stored as `.pkl` files |
| **Feature Scaling** | StandardScaler (Scikit-learn) | Applied before prediction to match training distribution |

### Backend Dependencies (Node.js)

| Package | Purpose |
| :--- | :--- |
| `express` ^4.18.2 | Web server & REST API framework |
| `python-shell` ^5.0.0 | Python integration (available, but `child_process.spawn` is used in production) |
| `helmet` ^7.1.0 | HTTP security headers |
| `express-rate-limit` ^7.1.5 | API rate limiting (100 requests / 15 min) |
| `cors` ^2.8.5 | Cross-Origin Resource Sharing |
| `axios` ^1.6.2 | HTTP client |
| `dotenv` ^16.3.1 | Environment variable management |
| `body-parser` ^1.20.2 | Request body parsing |
| `uuid` ^9.0.1 | Unique ID generation |
| `nodemon` ^3.0.2 *(dev)* | Auto-restart during development |

### ML Dependencies (Python)

| Package | Purpose |
| :--- | :--- |
| `scikit-learn` 1.3.2 | Random Forest model, StandardScaler, GridSearchCV, metrics |
| `pandas` 2.1.3 | Dataset loading & manipulation |
| `numpy` 1.24.3 | Numerical computation & feature arrays |
| `python-dotenv` 1.0.0 | Environment configuration |

---

## 🏗️ Architecture

```
┌──────────────────────┐
│   Frontend (Browser)  │
│  HTML5 / CSS3 / JS   │
└─────────┬────────────┘
          │  HTTP (fetch)
          ▼
┌──────────────────────┐
│  Backend (Node.js)   │
│  Express.js Server   │
│  Port: 5000          │
│  ┌────────────────┐  │
│  │ Helmet (HTTPS) │  │
│  │ Rate Limiter   │  │
│  │ CORS           │  │
│  │ Body Parser    │  │
│  └────────────────┘  │
└─────────┬────────────┘
          │  child_process.spawn
          ▼
┌──────────────────────┐
│  ML Model (Python)   │
│  predict.py          │
│  ┌────────────────┐  │
│  │ Feature Ext.   │──┤──▶ 32 URL features
│  │ StandardScaler │  │
│  │ Random Forest  │  │
│  └────────────────┘  │
│  trained_model.pkl   │
│  scaler.pkl          │
└──────────────────────┘
```

---

## 📂 Directory Structure

```text
phishing-detection-project/
├── backend/
│   ├── config/
│   │   └── database.js             # Database configuration
│   ├── controllers/
│   │   └── predictionController.js # Prediction logic & Python bridge
│   ├── middleware/
│   │   └── validation.js           # Input validation middleware
│   ├── routes/
│   │   ├── predictions.js          # /api/predict & /api/predict-batch
│   │   └── health.js               # /health endpoint
│   ├── utils/
│   │   └── logger.js               # Logging utility
│   ├── logs/                       # Server log files
│   ├── server.js                   # Express app entry point
│   ├── package.json                # Node.js dependencies
│   └── .env                        # Environment variables
│
├── frontend/
│   ├── index.html                  # Main user interface
│   ├── style.css                   # UI styling
│   └── script.js                   # Client-side API interaction
│
├── ml_model/
│   ├── dataset/
│   │   └── phishing_urls_clean.csv # Labeled URL dataset
│   ├── feature_extraction.py       # Extracts 32 features from URLs
│   ├── train_model.py              # Training pipeline with GridSearchCV
│   ├── predict.py                  # Prediction script (called by backend)
│   ├── download_and_create_dataset.py  # Dataset acquisition script
│   ├── prepare_dataset.py          # Dataset preprocessing
│   ├── trained_model.pkl           # Serialized Random Forest model
│   ├── scaler.pkl                  # Fitted StandardScaler
│   ├── model_metadata.pkl          # Training metadata & metrics
│   ├── requirements.txt            # Python dependencies
│   └── venv/                       # Python virtual environment
│
├── trained_model.pkl               # Copy of trained model (root level)
└── Readme.md                       # Project documentation
```

---

## 📌 Project Methodology

The project follows a standard Data Science pipeline optimized for Cyber Security:

1. **Data Collection:** Utilizing datasets containing thousands of verified phishing and legitimate URLs (e.g., PhishTank, UCI Repository).
2. **Feature Extraction:** Raw URLs are parsed into **32 numerical features** that a machine learning model can understand.
3. **Data Preprocessing:** Handling missing values, deduplication, label normalization, feature scaling with `StandardScaler`, and stratified train-test split (80/20).
4. **Model Training:** Random Forest classifier optimized via `GridSearchCV` with 5-fold cross-validation across hyperparameters (`n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf`, `max_features`).
5. **Performance Evaluation:** Measuring success based on Accuracy, Precision, Recall, F1-Score, and ROC-AUC.

---

## 🧪 Feature Engineering (32 Features)

The core of this project lies in transforming a URL string into **32 unique features** categorized into:

### Address Bar & URL Structure
- `url_length`, `domain_length`, `path_length` — Length-based indicators
- `num_dots`, `num_hyphens_domain`, `num_subdomains` — Structural counts
- `path_depth`, `path_domain_ratio` — Path analysis

### Domain Analysis
- `domain_entropy` — Shannon entropy (high = random/suspicious)
- `has_dash_in_domain`, `double_dot` — Malformed domain patterns
- `suspicious_tld` — Detection of high-risk TLDs (`.tk`, `.ml`, `.xyz`, etc.)
- `is_international_domain` — Punycode/IDN homograph attack detection

### IP & Protocol Analysis
- `has_ip_address`, `has_obfuscated_ip` — Raw & obfuscated IP detection
- `uses_https`, `has_explicit_port` — Protocol & port analysis

### Special Characters & Encoding
- `has_at_symbol`, `double_slash_count` — Redirect indicators
- `percent_encoding_count` — URL obfuscation detection
- `query_param_count`, `semicolon_count`, `ampersand_count` — Query analysis
- `special_char_count`, `special_char_ratio` — Overall special character density

### Character Distribution
- `digit_ratio`, `uppercase_ratio` — Character type ratios
- `vowel_consonant_ratio` — Linguistic pattern analysis

### Content & Pattern Detection
- `has_suspicious_keywords` — Detection of keywords like `verify`, `login`, `bank`, `paypal`, etc.
- `is_url_shortener` — Detection of services like `bit.ly`, `tinyurl`, etc.
- `has_tld`, `has_query_string` — Basic structural validation

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API info & available endpoints |
| `GET` | `/health` | Server health check |
| `POST` | `/api/predict` | Single URL prediction |
| `POST` | `/api/predict-batch` | Batch URL prediction |

### Example Request

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://amaz0n-verify-account.tk/login"}'
```

### Example Response

```json
{
  "success": true,
  "url": "https://amaz0n-verify-account.tk/login",
  "prediction": "Phishing",
  "confidence": 97.5,
  "features": { "..." },
  "timestamp": "2025-01-01T00:00:00.000Z"
}
```

---

## 📊 Model Performance

The production model is a **Random Forest** classifier trained with `class_weight='balanced'` and hyperparameter optimization via `GridSearchCV`.

| Metric | Score |
| :--- | :--- |
| **Accuracy** | ~97%+ |
| **Precision** | ~0.97+ |
| **Recall** | ~0.96+ |
| **F1-Score** | ~0.97+ |

> **Note:** Exact metrics depend on the dataset used during training. The training pipeline prints detailed metrics including confusion matrix and feature importances.

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** (v16+)
- **Python** (3.8+)
- **npm** (comes with Node.js)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd phishing-detection-project

# 2. Install backend dependencies
cd backend
npm install

# 3. Set up Python environment
cd ../ml_model
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
pip install -r requirements.txt

# 4. Train the model (if trained_model.pkl doesn't exist)
python train_model.py

# 5. Start the server
cd ../backend
npm start
# or for development:
npm run dev
```

### Environment Variables (`.env`)

```env
PORT=5000
NODE_ENV=development
PYTHON_PATH=python
PYTHON_SCRIPT_PATH=../ml_model/predict.py
LOG_LEVEL=debug
CORS_ORIGIN=http://localhost:5000
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

---

## 📄 License

This project is licensed under the MIT License.
