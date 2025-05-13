from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import sqlite3


app=Flask(__name__)
UPLOAD_FOLDER = 'uploads'
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE='resumes.db'

#Creating Table for Resume Database (initialize database at beginning before loading page)
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL
            )
        """)
        conn.commit()


#Load Home page
@app.route('/')
def home():
    return render_template("index.html")

#Upload resume using POST
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO file_data (file_name, file_path, file_size) VALUES (?, ?, ?)",
                (filename, file_path, file_size)
            )
            conn.commit()
        return jsonify({"message": f"File '{filename}' uploaded successfully"}), 200
    except Exception as e:
        print("Database error:", e)
        return jsonify({"message": "Database error"}), 500


if __name__ == "__main__":
    init_db() # Ensure table is created before app starts
    app.run(debug=True)