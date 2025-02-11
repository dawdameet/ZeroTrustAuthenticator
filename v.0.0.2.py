from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Create SQLite DB
conn = sqlite3.connect("behavior.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_behavior (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        keystrokes TEXT,
        mouse_movements TEXT
    )
""")
conn.commit()

@app.route('/behavior', methods=['POST'])
def receive_behavior():
    data = request.json
    user_id = "user123"  # Change this to dynamic login later
    keystrokes = str(data.get("keystrokes", []))
    mouse_movements = str(data.get("mouseMovements", []))
    
    # Store in database
    cursor.execute("INSERT INTO user_behavior (user_id, keystrokes, mouse_movements) VALUES (?, ?, ?)", 
                   (user_id, keystrokes, mouse_movements))
    conn.commit()

    return jsonify({"message": "Behavior data stored"}), 200

if __name__ == "__main__":
    app.run(debug=True)
