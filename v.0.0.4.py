from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import numpy as np
import json
from scipy.spatial.distance import euclidean

app = Flask(__name__)
CORS(app)

# Connect to SQLite DB
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

def parse_behavior(behavior_str):
    """Convert stored behavior JSON string back to Python list."""
    if not behavior_str:
        return []
    try:
        return json.loads(behavior_str)
    except json.JSONDecodeError:
        return []  # Return empty list on invalid JSON


@app.route('/behavior', methods=['POST'])
def receive_behavior():
    data = request.json
    user_id = "user123"  # Replace with real authentication later
    keystrokes = json.dumps(data.get("keystrokes", []))  # Convert to JSON
    mouse_movements = json.dumps(data.get("mouseMovements", []))

    # Retrieve previous behavior
    cursor.execute("SELECT keystrokes, mouse_movements FROM user_behavior WHERE user_id=?", (user_id,))
    past_behavior = cursor.fetchall()

    if past_behavior:
        # Convert past behavior to lists
        past_keystrokes = parse_behavior(past_behavior[-1][0])
        past_mouse_movements = parse_behavior(past_behavior[-1][1])

        # Convert new behavior to lists
        current_keystrokes = data.get("keystrokes", [])
        current_mouse_movements = data.get("mouseMovements", [])

        # Compute similarity using Euclidean distance
        keystroke_diff = (
            euclidean(
                [k["time"] for k in past_keystrokes] if past_keystrokes else [0],
                [k["time"] for k in current_keystrokes] if current_keystrokes else [0],
            )
            if past_keystrokes and current_keystrokes
            else float("inf")
        )

        mouse_diff = (
            euclidean(
                [m["time"] for m in past_mouse_movements] if past_mouse_movements else [0],
                [m["time"] for m in current_mouse_movements] if current_mouse_movements else [0],
            )
            if past_mouse_movements and current_mouse_movements
            else float("inf")
        )

        threshold = 5000  # Adjustable threshold

        if keystroke_diff < threshold and mouse_diff < threshold:
            auth_status = "Authenticated"
            reason = "Behavior matches previous interactions."
        else:
            auth_status = "Rejected"
            reason = "Significant deviation from previous behavior detected."

        return jsonify({
            "message": auth_status,
            "reason": reason,
            "keystroke_diff": keystroke_diff,
            "mouse_diff": mouse_diff,
            "threshold": threshold
        }), 200

    # Store new behavior data
    cursor.execute("INSERT INTO user_behavior (user_id, keystrokes, mouse_movements) VALUES (?, ?, ?)", 
                   (user_id, keystrokes, mouse_movements))
    conn.commit()

    return jsonify({
        "message": "First-time behavior recorded",
        "reason": "No previous data found. This will be used as reference for future authentication."
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
