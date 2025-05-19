from flask import Flask, render_template, request, jsonify, g
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import sqlite3
import click

# Import the parser
from main import get_parsed_resume_data
from main import get_parsed_jd_data  # assuming you have a function to parse JD PDFs


app = Flask(__name__)
CORS(app)

# Uploads and DB config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER_RESUME = os.path.join(BASE_DIR, 'uploads', 'resumes')
UPLOAD_FOLDER_JD = os.path.join(BASE_DIR, 'uploads', 'job_descriptions')
DATABASE_FOLDER = os.path.join(BASE_DIR, 'database')

os.makedirs(UPLOAD_FOLDER_RESUME, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_JD, exist_ok=True)
os.makedirs(DATABASE_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER_RESUME'] = UPLOAD_FOLDER_RESUME
app.config['UPLOAD_FOLDER_JD'] = UPLOAD_FOLDER_JD

DB_PATH = os.path.join(DATABASE_FOLDER, 'app.db')

# -----------------------
# DB Functions
# -----------------------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db:
        db.close()

# -----------------------
# Init DB Tables
# -----------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            jd_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description BLOB NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
            jd_id INTEGER,
            filename TEXT NOT NULL,
            content BLOB NOT NULL,
            FOREIGN KEY(jd_id) REFERENCES job_descriptions(jd_id)
        )
    ''')

    conn.commit()

@app.cli.command('init-db')
def init_db_command():
    with app.app_context():
        init_db()
    click.echo('Initialized the database.')

# -----------------------
# Routes
# -----------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'message': 'Missing resume file'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER_RESUME'], filename)
    file.save(file_path)

    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO resumes (jd_id, filename, content) VALUES (?, ?, ?)',
            (None, filename, content)
        )
        resume_id = cur.lastrowid
        conn.commit()

        parsed_data = get_parsed_resume_data(content)
        return jsonify({
            'message': f"File '{filename}' uploaded.",
            'resume_id': resume_id,
            'parsed_data': parsed_data
        }), 200

    except Exception as e:
        print("Upload error:", e)
        return jsonify({'message': 'Internal error'}), 500

@app.route('/update_resume_info', methods=['POST'])
def update_resume_info():
    data = request.get_json()
    resume_id = data.get('resume_id')
    edited_text = data.get('edited_text')

    if not resume_id or not edited_text:
        return jsonify({'message': 'Missing resume_id or text'}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE resumes SET content = ? WHERE resume_id = ?',
            (edited_text, resume_id)
        )
        conn.commit()
        return jsonify({'message': 'Resume updated successfully'}), 200
    except Exception as e:
        print("Update error:", e)
        return jsonify({'message': 'Failed to update resume'}), 500

@app.route('/add_jd', methods=['POST'])
def add_jd():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    resume_id = data.get('resume_id')

    if not title or not description or not resume_id:
        return jsonify({'message': 'Missing fields'}), 400

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            'INSERT INTO job_descriptions (title, description) VALUES (?, ?)',
            (title, description)
        )
        jd_id = cur.lastrowid

        cur.execute(
            'UPDATE resumes SET jd_id = ? WHERE resume_id = ?',
            (jd_id, resume_id)
        )

        conn.commit()
        return jsonify({'message': 'JD added and linked', 'jd_id': jd_id}), 200
    except Exception as e:
        print("JD error:", e)
        return jsonify({'message': 'Failed to store JD'}), 500
    
@app.route('/parse_jd_file', methods=['POST'])
def parse_jd_file():
    if 'jd_file' not in request.files:
        return jsonify({'message': 'No JD file provided'}), 400

    file = request.files['jd_file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER_JD'], filename)
    file.save(file_path)

    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # Assuming your parse_jd_pdf function takes bytes and returns a string
        parsed_description = get_parsed_jd_data(content)

        return jsonify({
            'message': f"JD file '{filename}' parsed.",
            'description': parsed_description
        }), 200

    except Exception as e:
        print("JD parse error:", e)
        return jsonify({'message': 'Internal JD parse error'}), 500

# -----------------------
# Run the App
# -----------------------

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
