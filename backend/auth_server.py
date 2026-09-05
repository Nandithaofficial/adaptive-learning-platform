from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
CORS(app)

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    conn = get_db()
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if existing:
        conn.close()
        return jsonify({"message": "Email already in use"}), 400

    hashed_password = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hashed_password)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Signup successful"}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 400

    if not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials"}), 400

    return jsonify({"message": "Login successful"}), 200


if __name__ == "__main__":
    app.run(port=5001, debug=True)