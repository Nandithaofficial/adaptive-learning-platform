from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

# Database location
DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

app = Flask(__name__)
CORS(app)


# -----------------------------
# DATABASE
# -----------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -----------------------------
# SIGNUP
# -----------------------------

@app.route("/api/auth/signup", methods=["POST"])
def signup():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Check required fields
    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    conn = get_db()

    # Check if email already exists
    existing = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if existing:
        conn.close()

        return jsonify({
            "message": "Email already in use"
        }), 400

    # Hash password
    hashed_password = generate_password_hash(password)

    # Store user
    conn.execute(
        """
        INSERT INTO users (name, email, password)
        VALUES (?, ?, ?)
        """,
        (name, email, hashed_password)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Signup successful"
    }), 201


# -----------------------------
# LOGIN
# -----------------------------

@app.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    # User doesn't exist
    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    # Password doesn't match
    if not check_password_hash(user["password"], password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    # Send user information to frontend
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200


# -----------------------------
# GET CURRENT USER
# -----------------------------

@app.route("/api/auth/user/<int:user_id>", methods=["GET"])
def get_user(user_id):

    conn = get_db()

    user = conn.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200


# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":
    app.run(
        host="localhost",
        port=5000,
        debug=True
    )