from flask import Flask, request, jsonify
import json
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pyotp
from twilio.rest import Client
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Directory to store collected data
DATA_DIR = './behavior_data'
os.makedirs(DATA_DIR, exist_ok=True)

# Load trained model (replace with your trained model)
def load_model():
    # Example: Load a pre-trained Random Forest model
    data = pd.read_csv('labeled_behavior_data.csv')
    X = data.drop(columns=['label'])
    y = data['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

# Feature extraction
def extract_features(df):
    # Example features for keystrokes
    df['key_press_duration'] = df[df['type'] == 'key']['duration']
    df['inter_key_timing'] = df[df['type'] == 'key']['timestamp'].diff()

    # Example features for mouse movements
    df['mouse_speed'] = np.sqrt(df[df['type'] == 'mouse']['x'].diff()**2 + df[df['type'] == 'mouse']['y'].diff()**2) / df[df['type'] == 'mouse']['timestamp'].diff()

    # Aggregate features
    features = {
        'avg_key_press_duration': df['key_press_duration'].mean(),
        'std_inter_key_timing': df['inter_key_timing'].std(),
        'avg_mouse_speed': df['mouse_speed'].mean(),
        'click_frequency': df[df['type'] == 'click'].shape[0] / df.shape[0]
    }
    return pd.DataFrame([features])

# Normalize features
def normalize_features(features):
    scaler = StandardScaler()
    return scaler.fit_transform(features)

# Generate OTP
def generate_otp(secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.now()

# Send OTP via SMS (Twilio example)
def send_otp(phone_number, otp):
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f'Your OTP is: {otp}',
        from_='+1234567890',
        to=phone_number
    )
    return message.sid

# Load the trained model
model = load_model()

# Endpoint to collect behavioral data
@app.route('/collect', methods=['POST'])
def collect_data():
    data = request.json

    print("Received data:", data)  # Debug: Print received data

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

    print(f"Data saved to {file_path}")  # Debug: Confirm file save
    return jsonify({'status': 'success'}), 200
# Endpoint for real-time monitoring and anomaly detection
@app.route('/monitor', methods=['POST'])
def monitor():
    data = request.json

    # Preprocess incoming data
    df = pd.DataFrame([data])
    features = extract_features(df)
    normalized_features = normalize_features(features)

    # Predict using the trained model
    prediction = model.predict(normalized_features)[0]

    if prediction == 'suspicious':
        # Trigger MFA
        secret_key = 'JBSWY3DPEHPK3PXP'
        otp = generate_otp(secret_key)
        phone_number = '+1234567890'  # Replace with user's phone number
        send_otp(phone_number, otp)

        return jsonify({'status': 'anomaly_detected', 'message': 'MFA triggered. Check your phone for OTP.'}), 403
    else:
        return jsonify({'status': 'behavior_normal'}), 200

if __name__ == '__main__':
    app.run(debug=True)