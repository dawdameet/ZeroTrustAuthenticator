from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Directory to store collected data
DATA_DIR = './behavior_data'
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/collect', methods=['POST'])
def collect_data():
    data = request.json

    # Save data to a file (or database in production)
    user_id = 'user1'  # Replace with actual user identification logic
    file_path = os.path.join(DATA_DIR, f'{user_id}.json')

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.append(data)

    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=4)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)