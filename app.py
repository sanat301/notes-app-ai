import os
import sqlite3
import requests

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('data/notes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    notes = conn.execute('SELECT * FROM notes').fetchall()
    conn.close()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    note = request.form.get('note')
    if note:
        conn = get_db()
        conn.execute('INSERT INTO notes (content) VALUES (?)', (note,))
        conn.commit()
        conn.close()
    return redirect('/')

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, content TEXT)')
    conn.close()

@app.route('/summarize')
def summarize():
    conn = get_db()
    notes = conn.execute('SELECT content FROM notes').fetchall()
    conn.close()

    text = "\n".join([n["content"] for n in notes])

    if not text:
        return "No notes to summarize"

    try:
        response = requests.post(
            "http://192.168.0.10:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": f"Summarize these notes:\n{text}",
                "stream": False
            }
        )

        result = response.json()
        summary = result.get("response", "No response from model")

    except Exception as e:
        summary = "AI failed: " + str(e)

    return f"<h2>Summary:</h2><p>{summary}</p><a href='/'>Back</a>"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)