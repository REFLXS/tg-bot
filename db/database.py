import sqlite3
from datetime import datetime


def get_connection():
    return sqlite3.connect("schedulerbot.db", check_same_thread=False)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            note_text TEXT,
            completed BOOLEAN DEFAULT 0,
            note_date DATETIME,
            note_end_date DATETIME
        )
    ''')
    conn.commit()
    conn.close()


def add_note(user_id: str, note_text: str, note_end_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO notes (user_id, note_text, note_date, note_end_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, note_text, now, note_end_date))
    conn.commit()
    conn.close()


def delete_note(note_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()


def delete_all_user_notes(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE user_id = ?', (user_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def get_user_notes(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, note_text, note_end_date FROM notes WHERE user_id = ? AND (completed IS NULL OR completed = 0) ORDER BY note_end_date',
        (user_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes


def get_all_pending_notes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notes WHERE completed IS NULL OR completed = 0')
    notes = cursor.fetchall()
    conn.close()
    return notes


def mark_note_completed(note_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE notes SET completed = 1 WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
