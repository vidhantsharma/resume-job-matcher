from flask import Flask, render_template, request, jsonify, g
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import sqlite3
import click
from utilties.resume_parser.resume_parser import ResumeParser

# Import the parser
from main import get_parsed_resume_data
from main import get_parsed_jd_data


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
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            total_experience VARCHAR, 
            degrees TEXT NOT NULL,            
            institutions TEXT NOT NULL,
            majors TEXT NOT NULL,
            skills TEXT NOT NULL,
            FOREIGN KEY(jd_id) REFERENCES job_descriptions(jd_id)
        )
    ''')

    conn.commit()

@app.cli.command('init-db')
def init_db_command():
    with app.app_context():
        init_db()
    click.echo('Initialized the database.')

# Load homepage 
@app.route('/')
def home():
    return render_template('index.html')

#form
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

        #function call from utilities to parse data using NLP (can be parsed without NLP too)
        parsed_data = get_parsed_resume_data(content) 
        
        # resume_info=ResumeParser.extract_resume_info(parsed_data)

        if "first_name" in parsed_data:
            first_name = parsed_data.get("first_name", "Unknown")
        if "last_name" in parsed_data:
            last_name=parsed_data.get("last_name", "Unknown")
        name=first_name +" "+ last_name

        if "email" in parsed_data:
            email=parsed_data.get("email", "Unknown")

        if "phone" in parsed_data:
            phone=parsed_data.get("phone", "Unknown")

        if "total_experience" in parsed_data:
            total_experience= str(parsed_data.get("total_experience", "Unknown"))

        if "degrees" in parsed_data:
            degrees=str(parsed_data.get("degrees", "Unknown"))

        if "institutions" in parsed_data:
            institutions=str(parsed_data.get("institutions", "Unknown"))

        if "majors" in parsed_data:
            majors=str(parsed_data.get("majors", "Unknown"))

        if "skills" in parsed_data:
            skills=str(parsed_data.get("skills", "Unknown"))
            

        #database debugger
        print("Inserting values:", (None, filename, name, email, phone, total_experience, degrees, institutions, majors, skills))

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO resumes (jd_id, filename, content, name, email, phone, total_experience, degrees, institutions, majors, skills) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (None, filename, content, name, email, phone, total_experience, degrees, institutions, majors, skills )
        )
        
        resume_id = cur.lastrowid
        conn.commit()
        
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

#JD
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
