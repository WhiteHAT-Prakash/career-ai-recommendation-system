# CareerAI - AI Career Recommendation & Talent Intelligence Platform

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation (New PC)](#setup--installation-new-pc)
- [How to Run](#how-to-run)
- [Architecture Overview](#architecture-overview)
- [Module Breakdown](#module-breakdown)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

CareerAI is a Flask-based web application that uses machine learning and NLP to provide personalized career guidance. Users take an assessment quiz, upload resumes for analysis, explore job listings, prepare for interviews with adaptive questions, and follow personalized career roadmaps.

The ML engine uses an **ensemble voting classifier** (Decision Tree + KNN + Random Forest) trained on a synthetic dataset of 2000 samples covering **20 career paths**.

---

## Features

| Feature | Description |
|---|---|
| **Career Prediction** | Ensemble ML model predicts top 3 careers with confidence scores based on a multi-step assessment |
| **Resume Analysis** | NLP-powered resume parsing extracts skills, education, experience and scores the resume out of 100 |
| **Job Explorer** | Live job listings from Adzuna/Remotive APIs with salary and location filters |
| **Interview Prep** | 150+ adaptive interview questions (technical, HR, scenario) tailored to skill gaps |
| **Career Roadmap** | 3-phase learning paths (Beginner, Intermediate, Advanced) with tools, certifications, and projects |
| **User Authentication** | Secure registration/login with bcrypt password hashing |
| **Prediction History** | Tracks all past career predictions per user |

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python, Flask, Flask-Login, Flask-WTF |
| **ML/Data** | scikit-learn (Ensemble: DT + KNN + RF), pandas, numpy, joblib |
| **NLP** | spaCy (NER), NLTK (tokenization, lemmatization, stopwords) |
| **Database** | MongoDB (primary), JSON file fallback |
| **Document Parsing** | pdfplumber (PDF), python-docx (Word) |
| **Frontend** | HTML, CSS (dark glassmorphism theme), vanilla JavaScript |
| **APIs** | Adzuna Job API, Remotive API |

---

## Project Structure

```
career_platform/
|
|-- app.py                     # Main Flask app with all routes
|-- config.py                  # Configuration (env vars, paths, API keys)
|-- setup.py                   # One-click dependency installer & model trainer
|-- run.bat                    # Windows launcher script
|-- requirements.txt           # Python dependencies
|-- .env                       # Environment variables (SECRET_KEY, API keys)
|
|-- ml_models/
|   |-- career_model.py        # Ensemble ML model (train + predict)
|   |-- ensemble_model.pkl     # Trained ensemble model
|   |-- dt_model.pkl           # Decision Tree model
|   |-- knn_model.pkl          # KNN model
|   |-- scaler.pkl             # Feature scaler
|   |-- label_encoder.pkl      # Career label encoder
|   |-- feature_names.pkl      # Feature column names
|   |-- metrics.json           # Model accuracy/precision/recall
|   +-- *_encoder.pkl          # Categorical encoders (degree, stream, work_pref)
|
|-- nlp_engine/
|   |-- resume_parser.py       # Resume text extraction, skill matching, scoring
|   +-- __init__.py
|
|-- data/
|   |-- generate_dataset.py    # Synthetic dataset generator (2000 samples)
|   |-- career_dataset.csv     # Generated training data
|   +-- app_database.json      # JSON fallback database (users, predictions)
|
|-- services/
|   |-- job_market.py          # Job listing fetcher (Adzuna + Remotive + fallback)
|   |-- interview_generator.py # Adaptive interview question generator
|   +-- roadmap_generator.py   # Personalized career roadmap builder
|
|-- templates/
|   |-- base.html              # Master layout (navbar, flash messages)
|   |-- landing.html           # Home page with hero section
|   |-- register.html          # User registration form
|   |-- login.html             # User login form
|   |-- dashboard.html         # User dashboard with feature cards
|   |-- assessment.html        # 6-step career assessment quiz
|   |-- results.html           # ML prediction results display
|   |-- resume.html            # Resume upload & analysis results
|   |-- jobs.html              # Job explorer with filters
|   |-- interview.html         # Interview prep questions
|   |-- roadmap.html           # Career roadmap visualization
|   +-- 404.html               # Custom error page
|
+-- static/
    |-- css/style.css          # Dark glassmorphism theme
    |-- js/app.js              # Frontend utilities
    +-- uploads/               # User-uploaded resumes (created at setup)
```

---

## Setup & Installation (New PC)

### Prerequisites

- **Python 3.10 - 3.12** (recommended). Python 3.13+ may have compatibility issues with spaCy.
- **pip** (comes with Python)
- **MongoDB** (optional - the app falls back to a JSON file database if MongoDB is not running)
- **Git** (optional, for cloning)

### Step-by-Step Setup

#### 1. Install Python

Download Python 3.12 from [python.org](https://www.python.org/downloads/).

During installation, **check "Add Python to PATH"**.

Verify installation:
```bash
python --version
pip --version
```

#### 2. Get the Project Files

Copy the `career_platform` folder to your PC, or clone from your repository:
```bash
git clone <your-repo-url>
cd career_platform
```

#### 3. Run Automated Setup

**Option A - Double-click (Windows):**
```
Double-click run.bat
```
This handles everything automatically on first run.

**Option B - Manual:**
```bash
python setup.py
```

The setup script will:
1. Install all Python packages from `requirements.txt`
2. Download spaCy English language model (`en_core_web_sm`)
3. Download NLTK data (punkt, wordnet, stopwords, taggers)
4. Generate the synthetic training dataset (2000 samples)
5. Train the ML ensemble model and save `.pkl` files
6. Create the `static/uploads/` directory

#### 4. Configure Environment Variables (Optional)

Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb://localhost:27017/career_platform
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_API_KEY=your-adzuna-api-key
```

- **SECRET_KEY**: Flask session secret (auto-generated if not set)
- **MONGO_URI**: MongoDB connection string (app uses JSON fallback if MongoDB is unavailable)
- **ADZUNA keys**: For live job listings (app uses fallback data if not set)

#### 5. Install MongoDB (Optional)

Download from [mongodb.com](https://www.mongodb.com/try/download/community) and start the service. The app works without it using JSON file storage.

---

## How to Run

### Start the Server

**Windows:**
```bash
run.bat
```

**Manual:**
```bash
python app.py
```

### Access the App

Open your browser and go to:
```
http://localhost:5000
```

### Usage Flow

1. **Register** an account on the registration page
2. **Login** with your credentials
3. Go to **Dashboard** to access all features
4. Take the **Career Assessment** (6-step quiz covering academics, skills, interests, aptitude, preferences)
5. View **Results** with top 3 predicted careers and confidence scores
6. **Upload Resume** for NLP analysis, skill extraction, and scoring
7. **Explore Jobs** filtered by your predicted career
8. **Practice Interviews** with adaptive questions based on your skill gaps
9. **Follow the Roadmap** for a structured learning path toward your career goal

---

## Architecture Overview

```
User Browser
    |
    v
Flask App (app.py)
    |
    |-- Authentication (bcrypt, Flask-Login)
    |-- Routes (pages + JSON APIs)
    |
    |-- ML Engine (ml_models/career_model.py)
    |     |-- Decision Tree
    |     |-- KNN (k=7)
    |     +-- Random Forest (100 trees)
    |          --> Ensemble Voting Classifier
    |
    |-- NLP Engine (nlp_engine/resume_parser.py)
    |     |-- spaCy NER (names, orgs, dates)
    |     |-- NLTK (tokenization, lemmatization)
    |     +-- Skill Matching (80+ tech skills, 16 soft skills)
    |
    |-- Services
    |     |-- Job Market (Adzuna API + Remotive API + fallback)
    |     |-- Interview Generator (150+ questions, 3 difficulty levels)
    |     +-- Roadmap Generator (3-phase paths, 8 careers)
    |
    +-- Database
          |-- MongoDB (primary)
          +-- JSON File (fallback)
```

---

## Module Breakdown

### ML Model (`ml_models/career_model.py`)

- **Training data**: 2000 synthetic samples across 20 careers
- **Features**: degree, stream, CGPA, aptitude, 50+ binary skill columns, work preference, derived features (skill_density, tech_soft_ratio, aptitude_index)
- **Ensemble**: Soft-voting classifier combining Decision Tree (max_depth=20), KNN (k=7, distance-weighted), Random Forest (100 estimators)
- **Output**: Top 3 career predictions with confidence percentages, feature importance, per-model comparisons
- **Metrics**: Saved to `metrics.json` (accuracy, precision, recall, F1 for each model)

### NLP Resume Parser (`nlp_engine/resume_parser.py`)

- **Text extraction**: PDF (pdfplumber), DOCX (python-docx)
- **Entity extraction**: spaCy NER for names, organizations, dates, locations; regex for emails and phones
- **Skill extraction**: Pattern matching against 80+ tech skills (6 categories) and 16 soft skills
- **Resume scoring**: 0-100 based on skills (40pts), education (20pts), experience (25pts), contact info (10pts), structure (5pts)
- **Career matching**: Calculates skill match percentage against required skills for any of the 20 careers
- **Fallback**: Works without spaCy/NLTK using regex-based extraction

### Job Market Service (`services/job_market.py`)

- **Adzuna API**: Real job listings (requires API key)
- **Remotive API**: Free remote job listings (no key needed)
- **Fallback**: Generates realistic placeholder listings when APIs are unavailable
- **Caching**: 10-minute TTL to reduce API calls
- **Market insights**: Demand level, salary ranges, growth trends, top locations, remote availability

### Interview Generator (`services/interview_generator.py`)

- **Question bank**: Technical (easy/medium/hard), HR, and scenario questions
- **Personalization**: Adapts to user's skill gaps and strengths
- **Careers covered**: Software Engineer, Data Scientist, Web Developer, Cybersecurity Analyst (+ generic fallback)
- **Difficulty mix**: 3 easy, 4 medium, 2 hard (default)

### Roadmap Generator (`services/roadmap_generator.py`)

- **3 phases**: Beginner (0-6 months), Intermediate (6-12 months), Advanced (12-24 months)
- **Per phase**: Skills, tools, certifications, projects
- **Personalization**: Marks already-known skills as completed, prioritizes skill gaps
- **Level assessment**: Auto-detects user's current level based on existing skills
- **Careers covered**: 8 detailed roadmaps (Software Engineer, Data Scientist, Web Developer, Cybersecurity Analyst, Cloud Architect, DevOps Engineer, AI/ML Engineer, Mobile App Developer)

---

## API Endpoints

### Pages

| Method | Route | Description |
|---|---|---|
| GET | `/` | Landing page |
| GET | `/register` | Registration form |
| POST | `/register` | Process registration |
| GET | `/login` | Login form |
| POST | `/login` | Authenticate user |
| GET | `/logout` | Log out |
| GET | `/dashboard` | User dashboard |
| GET | `/assessment` | Career assessment quiz |
| GET | `/results` | Prediction results |
| GET | `/resume` | Resume upload page |
| GET | `/interview` | Interview prep page |
| GET | `/jobs` | Job explorer |
| GET | `/roadmap` | Career roadmap |

### JSON APIs

| Method | Route | Description |
|---|---|---|
| POST | `/api/predict` | Run ML prediction on assessment data |
| GET | `/api/model-metrics` | Get model accuracy/precision/recall |
| POST | `/api/resume/upload` | Upload and analyze resume |
| GET | `/api/jobs?career=...&location=...` | Fetch job listings |
| GET | `/api/jobs/insights?career=...` | Get market insights |
| POST | `/api/interview/questions` | Generate interview questions |
| POST | `/api/roadmap` | Generate personalized roadmap |
| GET | `/api/user/profile` | Get user profile |
| POST | `/api/user/profile` | Update user profile |
| GET | `/api/user/history` | Get prediction history |

---

## Database Schema

### MongoDB Collections

**users**
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "password": "bcrypt hash",
  "created_at": "datetime",
  "profile": {},
  "predictions": [],
  "resumes": []
}
```

**predictions**
```json
{
  "user_id": "string",
  "input": { "...assessment fields" },
  "result": {
    "predictions": [{"career": "...", "confidence": 85.2}, ...],
    "feature_importance": [...],
    "model_comparison": {...}
  },
  "timestamp": "datetime"
}
```

**resumes**
```json
{
  "user_id": "string",
  "filename": "string",
  "analysis": { "skills": {...}, "score": 75, "..." },
  "target_career": "string",
  "timestamp": "datetime"
}
```

### JSON Fallback (`data/app_database.json`)

Used when MongoDB is unavailable. Same structure stored as nested JSON objects keyed by UUID.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `scikit-learn` fails to install | Use Python 3.10-3.12. Version 3.13+ may require newer package versions. |
| spaCy crashes on import | Python 3.14 is incompatible with spaCy's Pydantic V1 dependency. The app auto-falls back to regex-based NLP. |
| `Microsoft Visual C++ 14.0 required` | Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or use Python 3.12 which has pre-built wheels. |
| MongoDB connection error | The app works without MongoDB using JSON file storage. No action needed. |
| Job listings show placeholder data | Set `ADZUNA_APP_ID` and `ADZUNA_API_KEY` in `.env` for real listings. The Remotive API also works without a key. |
| Model not found errors | Run `python setup.py` to generate the dataset and train models. |
| Resume upload fails | Ensure `static/uploads/` directory exists. Supported formats: PDF, DOCX. Max size: 16MB. |
| Port 5000 already in use | Change the port in `app.py` or kill the existing process using port 5000. |
