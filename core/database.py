import sqlite3
import json

DB_NAME = "career_compass.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # In a real production app we'd use migrations.
    # Removed DROP TABLE to preserve data in production.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            recommended_path TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_tag TEXT,
            top_subjects TEXT,
            path_scores TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_recommendation(student_name, recommended_path, session_tag="Unknown", top_subjects="[]", path_scores="{}"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recommendations (student_name, recommended_path, session_tag, top_subjects, path_scores)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_name, recommended_path, session_tag, top_subjects, path_scores))
    conn.commit()
    conn.close()

def get_all_recommendations():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, student_name, recommended_path, date, session_tag, top_subjects, path_scores 
        FROM recommendations 
        ORDER BY date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_report_sessions():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_tag, COUNT(*) as student_count, MAX(date) as last_date 
        FROM recommendations 
        GROUP BY session_tag
        ORDER BY last_date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_recommendations_by_session(session_tag):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, student_name, recommended_path, date, top_subjects, path_scores 
        FROM recommendations 
        WHERE session_tag = ?
        ORDER BY date DESC
    ''', (session_tag,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_session(session_tag):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recommendations WHERE session_tag = ?', (session_tag,))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
