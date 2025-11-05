import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("alerts.db")
    c = conn.cursor()

    # users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # alerts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            latitude REAL,
            longitude REAL,
            timestamp TEXT
        )
    """)

    # --- Create default user: test / test ---
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("test", "test"))
        print("✅ Default user created (test/test)")
    except:
        print("ℹ️ Default user already exists")

    conn.commit()
    conn.close()


init_db()

# ---------- ROUTES ----------

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing details"}), 400

    try:
        conn = sqlite3.connect("alerts.db")
        c = conn.cursor()
        c.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered"}), 201
    except:
        return jsonify({"error": "Username already exists"}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("alerts.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({"user_id": row[0], "message": "Login success"}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/alert", methods=["POST"])
def alert():
    data = request.json
    user_id = data.get("user_id")
    lat = data.get("lat")
    lng = data.get("lng")

    if not user_id or lat is None or lng is None:
        return jsonify({"error": "Missing data"}), 400

    conn = sqlite3.connect("alerts.db")
    c = conn.cursor()
    c.execute("INSERT INTO alerts(user_id, latitude, longitude, timestamp) VALUES (?,?,?,?)",
              (user_id, lat, lng, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"message": "Alert saved"}), 200


@app.route("/alerts", methods=["GET"])
def alerts_list():
    conn = sqlite3.connect("alerts.db")
    c = conn.cursor()
    c.execute("SELECT users.username, latitude, longitude, timestamp FROM alerts JOIN users ON alerts.user_id = users.id ORDER BY alerts.id DESC")
    rows = c.fetchall()
    conn.close()

    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
