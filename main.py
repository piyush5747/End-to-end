from flask import Flask, request, render_template, jsonify
from cryptography.fernet import Fernet
import sqlite3
import os

app = Flask(__name__)

# Encryption Key (Generate using Fernet.generate_key())
SECRET_KEY = b'your-generated-key-here'
cipher = Fernet(SECRET_KEY)

# Initialize Database
DB_FILE = "chat.db"
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            encrypted_msg TEXT)''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_message():
    msg = request.form.get('message')
    encrypted_msg = cipher.encrypt(msg.encode()).decode()
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO messages (encrypted_msg) VALUES (?)", (encrypted_msg,))
        conn.commit()
    
    return jsonify({'status': 'success', 'message': 'Encrypted message sent!'})

@app.route('/receive', methods=['GET'])
def receive_messages():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT encrypted_msg FROM messages")
        messages = [cipher.decrypt(row[0].encode()).decode() for row in cursor.fetchall()]
    
    return jsonify({'messages': messages})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)