"""
AI-Driven Smart Career Recommendation & Talent Intelligence Platform
Main Flask Application
"""
import os
import sys
import json
import datetime
from functools import wraps

from flask import (Flask, render_template, request, jsonify, redirect,
                   url_for, session, flash, send_from_directory)
from werkzeug.utils import secure_filename
import bcrypt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ─── Database Setup ─────────────────────────────────────────
# Try MongoDB first, fall back to file-based JSON storage
db = None
mongo_available = False

try:
    from flask_pymongo import PyMongo
    mongo = PyMongo(app)
    # Test connection
    mongo.db.command('ping')
    db = mongo.db
    mongo_available = True
    print("MongoDB connected successfully.")
except Exception as e:
    print(f"MongoDB not available ({e}). Using file-based storage.")
    mongo_available = False


# ─── File-Based Storage Fallback ─────────────────────────────
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'app_database.json')


def _load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {'users': {}, 'predictions': [], 'resumes': []}


def _save_db(data):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)


# ─── Auth Helpers ────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    if 'user_id' not in session:
        return None
    if mongo_available:
        from bson.objectid import ObjectId
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if user:
            user['_id'] = str(user['_id'])
        return user
    else:
        data = _load_db()
        return data['users'].get(session['user_id'])


# ─── Initialize ML Engine ────────────────────────────────────
career_engine = None


def get_career_engine():
    global career_engine
    if career_engine is None:
        from ml_models.career_model import CareerRecommendationEngine
        career_engine = CareerRecommendationEngine()
        if not career_engine.is_trained:
            # Generate dataset if needed
            from data.generate_dataset import generate_dataset
            dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'career_dataset.csv')
            if not os.path.exists(dataset_path):
                generate_dataset(2000)
            career_engine.train()
    return career_engine


# ─── Routes: Pages ────────────────────────────────────────────
@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if mongo_available:
            if db.users.find_one({'email': email}):
                flash('Email already registered.', 'error')
                return render_template('register.html')
            result = db.users.insert_one({
                'name': name,
                'email': email,
                'password': hashed,
                'created_at': datetime.datetime.utcnow().isoformat(),
                'profile': {},
                'predictions': [],
                'resumes': []
            })
            session['user_id'] = str(result.inserted_id)
            session['user_name'] = name
        else:
            file_db = _load_db()
            for uid, user in file_db['users'].items():
                if user['email'] == email:
                    flash('Email already registered.', 'error')
                    return render_template('register.html')
            import uuid
            uid = str(uuid.uuid4())
            file_db['users'][uid] = {
                'name': name,
                'email': email,
                'password': hashed,
                'created_at': datetime.datetime.utcnow().isoformat(),
                'profile': {},
                'predictions': [],
                'resumes': []
            }
            _save_db(file_db)
            session['user_id'] = uid
            session['user_name'] = name

        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = None
        user_id = None

        if mongo_available:
            user = db.users.find_one({'email': email})
            if user:
                user_id = str(user['_id'])
        else:
            file_db = _load_db()
            for uid, u in file_db['users'].items():
                if u['email'] == email:
                    user = u
                    user_id = uid
                    break

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user_id
            session['user_name'] = user.get('name', 'User')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('landing'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    return render_template('dashboard.html', user=user)


@app.route('/assessment')
@login_required
def assessment():
    from data.generate_dataset import (ALL_TECH_SKILLS, ALL_SOFT_SKILLS,
                                       ALL_INTERESTS, ALL_DEGREES,
                                       ALL_STREAMS, ALL_WORK_PREFS)
    return render_template('assessment.html',
                           tech_skills=ALL_TECH_SKILLS,
                           soft_skills=ALL_SOFT_SKILLS,
                           interests=ALL_INTERESTS,
                           degrees=ALL_DEGREES,
                           streams=ALL_STREAMS,
                           work_prefs=ALL_WORK_PREFS)


@app.route('/results')
@login_required
def results():
    return render_template('results.html')


@app.route('/resume')
@login_required
def resume_page():
    return render_template('resume.html')


@app.route('/interview')
@login_required
def interview():
    return render_template('interview.html')


@app.route('/jobs')
@login_required
def jobs():
    return render_template('jobs.html')


@app.route('/roadmap')
@login_required
def roadmap():
    return render_template('roadmap.html')


# ─── API Routes ───────────────────────────────────────────────

@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    """Career prediction endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        engine = get_career_engine()
        result = engine.predict(data)

        # Store prediction
        prediction_record = {
            'user_id': session['user_id'],
            'input': data,
            'result': result,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }

        if mongo_available:
            db.predictions.insert_one(prediction_record)
            db.users.update_one(
                {'_id': __import__('bson').objectid.ObjectId(session['user_id'])},
                {'$push': {'predictions': prediction_record}}
            )
        else:
            file_db = _load_db()
            file_db['predictions'].append(prediction_record)
            if session['user_id'] in file_db['users']:
                file_db['users'][session['user_id']].setdefault('predictions', []).append(prediction_record)
            _save_db(file_db)

        # Store in session for results page
        session['last_prediction'] = result
        session['last_assessment'] = data

        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/model-metrics')
@login_required
def api_model_metrics():
    """Get model evaluation metrics."""
    try:
        engine = get_career_engine()
        return jsonify(engine.metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/resume/upload', methods=['POST'])
@login_required
def api_resume_upload():
    """Resume upload and analysis endpoint."""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400

        filename = secure_filename(f"{session['user_id']}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        target_career = request.form.get('target_career', None)

        from nlp_engine.resume_parser import resume_parser
        analysis = resume_parser.analyze_resume(filepath, target_career)

        if 'error' in analysis:
            return jsonify(analysis), 400

        # Store analysis
        resume_record = {
            'user_id': session['user_id'],
            'filename': filename,
            'analysis': analysis,
            'target_career': target_career,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }

        if mongo_available:
            db.resumes.insert_one(resume_record)
        else:
            file_db = _load_db()
            file_db['resumes'].append(resume_record)
            _save_db(file_db)

        session['last_resume_analysis'] = analysis

        return jsonify(analysis)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
@login_required
def api_jobs():
    """Fetch job listings."""
    try:
        career = request.args.get('career', 'Software Engineer')
        location = request.args.get('location', 'us')
        page = int(request.args.get('page', 1))

        from services.job_market import job_market_service
        result = job_market_service.get_jobs(career, location, page)

        return jsonify(result or {'jobs': [], 'total': 0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/insights', methods=['GET'])
@login_required
def api_job_insights():
    """Get market insights for a career."""
    try:
        career = request.args.get('career', 'Software Engineer')
        from services.job_market import job_market_service
        insights = job_market_service.get_market_insights(career)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/questions', methods=['POST'])
@login_required
def api_interview_questions():
    """Generate interview questions."""
    try:
        data = request.get_json() or {}
        career = data.get('career', 'Software Engineer')
        user_skills = data.get('skills', [])
        skill_gaps = data.get('skill_gaps', [])

        from services.interview_generator import interview_generator
        questions = interview_generator.generate_questions(career, user_skills, skill_gaps)

        return jsonify(questions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/roadmap', methods=['POST'])
@login_required
def api_roadmap():
    """Generate career roadmap."""
    try:
        data = request.get_json() or {}
        career = data.get('career', 'Software Engineer')
        current_skills = data.get('current_skills', [])
        skill_gaps = data.get('skill_gaps', [])

        from services.roadmap_generator import roadmap_generator
        roadmap_data = roadmap_generator.generate_roadmap(career, current_skills, skill_gaps)

        return jsonify(roadmap_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/profile', methods=['GET', 'POST'])
@login_required
def api_user_profile():
    """Get or update user profile."""
    if request.method == 'GET':
        user = get_current_user()
        if user:
            user.pop('password', None)
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404

    if request.method == 'POST':
        data = request.get_json()
        if mongo_available:
            from bson.objectid import ObjectId
            db.users.update_one(
                {'_id': ObjectId(session['user_id'])},
                {'$set': {'profile': data}}
            )
        else:
            file_db = _load_db()
            if session['user_id'] in file_db['users']:
                file_db['users'][session['user_id']]['profile'] = data
                _save_db(file_db)

        return jsonify({'status': 'updated'})


@app.route('/api/user/history')
@login_required
def api_user_history():
    """Get user prediction history."""
    if mongo_available:
        predictions = list(db.predictions.find(
            {'user_id': session['user_id']},
            {'_id': 0}
        ).sort('timestamp', -1).limit(20))
    else:
        file_db = _load_db()
        predictions = [p for p in file_db['predictions']
                       if p.get('user_id') == session['user_id']]
        predictions = sorted(predictions, key=lambda x: x.get('timestamp', ''), reverse=True)[:20]

    return jsonify(predictions)


# ─── Error Handlers ───────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ─── Main ─────────────────────────────────────────────────────
if __name__ == '__main__':
    # Pre-train model on startup
    print("Initializing Career Recommendation Engine...")
    try:
        engine = get_career_engine()
        print("Engine ready.")
    except Exception as e:
        print(f"Warning: Could not pre-initialize engine: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)
