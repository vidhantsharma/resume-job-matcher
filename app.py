from flask import Flask, render_template, request, jsonify, g
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import click

# Import DB helpers
from database.db import get_jd_db, get_resume_db, close_db

app = Flask(__name__)
CORS(app)

# BASE_DIR for reliable paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Ensure database folder exists
DB_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DB_DIR, exist_ok=True)


# Upload folder setup
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# CLI command to initialize both databases
def init_db_command():
    init_jd_db()
    init_resume_db()
    click.echo('JD and Resume databases initialized.')

@app.cli.command('init-db')
def init_db_command():
    with app.app_context():
        init_jd_db()
        init_resume_db()
    click.echo('JD and Resume databases initialized.')

# Ensure DB connections are closed on teardown
app.teardown_appcontext(close_db)

# -------------------------------
# Init DB Schemas (directly in code)
# -------------------------------

def init_jd_db():
    conn = get_jd_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            jd_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        );
    ''')
    conn.commit()


def init_resume_db():
    conn = get_resume_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
            jd_id INTEGER,
            filename TEXT NOT NULL,
            content BLOB NOT NULL,
            FOREIGN KEY(jd_id) REFERENCES job_descriptions(jd_id)
        );
    ''')
    conn.commit()

# -------------------------------
# Routes
# -------------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/init')
def init_tables():
    init_jd_db()
    init_resume_db()
    return 'JD and Resume tables created!'

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'message': 'Missing resume file'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    try:
        with open(save_path, 'rb') as f:
            content = f.read()

        conn = get_resume_db()
        cur = conn.cursor()
        # Insert with jd_id = NULL for now
        cur.execute(
            'INSERT INTO resumes (jd_id, filename, content) VALUES (?, ?, ?)',
            (None, filename, content)
        )
        resume_id = cur.lastrowid
        conn.commit()
        return jsonify({
            'message': f"File '{filename}' uploaded.",
            'resume_id': resume_id
        }), 200
    except Exception as e:
        print('Database error:', e)
        return jsonify({'message': 'Database error'}), 500

@app.route('/add_jd', methods=['POST'])
def add_jd():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    resume_id = data.get('resume_id')

    if not title or not description or not resume_id:
        return jsonify({'message': 'Missing title, description, or resume_id'}), 400

    try:
        conn_jd = get_jd_db()
        cur_jd = conn_jd.cursor()
        cur_jd.execute(
            'INSERT INTO job_descriptions (title, description) VALUES (?, ?)',
            (title, description)
        )
        jd_id = cur_jd.lastrowid
        conn_jd.commit()

        # Update resume entry with this jd_id
        conn_resume = get_resume_db()
        cur_resume = conn_resume.cursor()
        cur_resume.execute(
            'UPDATE resumes SET jd_id = ? WHERE resume_id = ?',
            (jd_id, resume_id)
        )
        conn_resume.commit()

        return jsonify({'message': 'JD received and linked to resume', 'jd_id': jd_id}), 200
    except Exception as e:
        print('Database error:', e)
        return jsonify({'message': 'Database error'}), 500


if __name__ == '__main__':
    # Initialize tables and run app
    with app.app_context():
            init_jd_db()
            init_resume_db()
    app.run(debug=True)
