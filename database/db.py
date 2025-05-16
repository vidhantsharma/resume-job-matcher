#Initialize DB from Flask
# database/db.py
import sqlite3
from flask import g

RESUME_DB = 'database/resume.db'
JD_DB='atabase/jd.db'

# Get or create a connection to the resume database
def get_resume_db():
    if 'resume_db' not in g:
        g.resume_db = sqlite3.connect(RESUME_DB)
        g.resume_db.row_factory = sqlite3.Row
    return g.resume_db

# Get or create a connection to the job descriptions database
def get_jd_db():
    if 'jd_db' not in g:
        g.jd_db = sqlite3.connect(JD_DB)
        g.jd_db.row_factory = sqlite3.Row
    return g.jd_db

# Close all open database connections on context teardown
def close_db(error=None):
    for key in ('resume_db', 'jd_db'):
        db = g.pop(key, None)
        if db is not None:
            db.close()
