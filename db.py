from typing import Dict, List
from TimeParser import TimeParser
import sqlite3

parser = TimeParser()

def get_connection():
    return sqlite3.connect("schedulerbot.db", check_same_thread=False)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS notes('
                   'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                   'user_id varchar(50),'
                   'note_text varchar(200),'
                   'completed, bool,'
                   'note_date DATETIME,'
                   'note_end_date DATETIME)')
    conn.commit()
    cursor.close()
    conn.close()

def add_note(message, datetime):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO notes('
                   'user_id, '
                   'note_text, '
                   'note_date,'
                   'note_end_date) VALUES '
                   '(?, ?, ?, ?)',
                    (
                        str(message.chat.id),
                        message.text,
                        now,
                        parser.parse(message.text),))
    conn.commit()
    cursor.close()
    conn.close()

def delete_note(note_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    cursor.close()
    conn.close()

def delete_all_user_notes(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE user_id = ?', (user_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return deleted_count

def get_user_notes(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, note_text, note_date FROM notes WHERE user_id = ?', (user_id,))
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return notes

def get_note_by_id(note_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
    note = cursor.fetchone()
    cursor.close()
    conn.close()
    return note