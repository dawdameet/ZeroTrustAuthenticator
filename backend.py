from flask import Flask, request, jsonify
from pynput import keyboard, mouse
import time
import threading
import json

app = Flask(__name__)

# Store user behavior data
user_behavior = {"keystrokes": [], "mouse_movements": []}

# Keystroke tracking
def on_press(key):
    try:
        user_behavior["keystrokes"].append({
            "key": key.char if hasattr(key, 'char') else str(key),
            "time": time.time()
        })
    except Exception as e:
        print("Error recording keystroke:", e)

def on_release(key):
    pass  # Can be used for additional analysis

# Mouse movement tracking
def on_move(x, y):
    user_behavior["mouse_movements"].append({"x": x, "y": y, "time": time.time()})

def on_click(x, y, button, pressed):
    user_behavior["mouse_movements"].append({
        "x": x, "y": y, "button": str(button), "pressed": pressed, "time": time.time()
    })

def start_listeners():
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()

# API Endpoint to fetch behavior data
@app.route("/behavior", methods=["GET"])
def get_behavior():
    return jsonify(user_behavior)

# Start listeners in a separate thread
threading.Thread(target=start_listeners, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
