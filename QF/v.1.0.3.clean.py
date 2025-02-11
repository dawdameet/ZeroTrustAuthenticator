from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import pyotp
from twilio.rest import Client

app = Flask(__name__)
CORS(app)

# Directory to store collected data
DATA_DIR = './behavior_data'
os.makedirs(DATA_DIR, exist_ok=True)

# Load the trained model
def load_model():
    try:
        model = joblib.load('behavior_model.pkl')
        return model
    except FileNotFoundError:
        raise Exception("Model file 'behavior_model.pkl' not found. Please train the model first.")

# Feature extraction
def extract_features(data):
    df = pd.DataFrame([data])

    # Example features for mouse movements
    df['mouse_speed'] = np.sqrt(df[df['type'] == 'mouse']['x'].diff()**2 + df[df['type'] == 'mouse']['y'].diff()**2) / df[df['type'] == 'mouse']['timestamp'].diff()

    # Replace NaN or infinite values with 0
    df['mouse_speed'] = df['mouse_speed'].fillna(0).replace([np.inf, -np.inf], 0)

    # Aggregate features
    features = {
        'avg_mouse_speed': df['mouse_speed'].mean(),
        'click_frequency': df[df['type'] == 'click'].shape[0] / df.shape[0]
    }
    return pd.DataFrame([features])
# Normalize features
def normalize_features(features):
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Convert back to DataFrame with feature names
    feature_names = ['avg_mouse_speed', 'click_frequency']
    return pd.DataFrame(scaled_features, columns=feature_names)
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
        from_='+918007852752',
        to=phone_number
    )
    return message.sid

# Endpoint to collect behavioral data
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


@app.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        data = request.json
        print("Received data:", data)

        # Preprocess incoming data
        features = extract_features(data)
        normalized_features = normalize_features(features)

        # Load the trained model
        model = load_model()

        # Predict using the trained model
        prediction = model.predict(normalized_features)[0]
        print("Prediction:", prediction)

        if prediction == 'suspicious':
            # Trigger MFA
            secret_key = 'JBSWY3DPEHPK3PXP'
            otp = generate_otp(secret_key)
            phone_number = '+1234567890'  # Replace with user's phone number
            send_otp(phone_number, otp)

            return jsonify({'status': 'anomaly_detected', 'message': 'MFA triggered. Check your phone for OTP.'}), 403
        else:
            return jsonify({'status': 'authenticated', 'message': 'User authenticated successfully.'}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)