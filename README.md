# Zero-Trust AI Authentication System

This project implements a Zero-Trust AI Authentication System that authenticates users based on their mouse movements and triggers Multi-Factor Authentication (MFA) for suspicious behavior.

## Features
- Collects user behavior data (mouse movements, clicks).
- Authenticates users without CAPTCHA.
- Triggers MFA (via OTP) for suspicious behavior.
- Uses a machine learning model to classify legitimate vs suspicious behavior.

## Project Structure
```
project/
│
├── behavior_data/               # Directory for raw behavioral data
│   └── user1.json               # Raw behavioral data
│
├── labeled_behavior_data.csv    # Preprocessed and labeled data
├── behavior_model.pkl           # Trained AI model
│
├── app.py                       # Flask backend
├── generate_data.py             # Script to generate random data
├── train_model.py               # Script to train the model
├── index.html                   # Frontend
└── README.md                    # This file
```

## Setup Instructions

### Prerequisites
- Python 3.x
- Install dependencies:
  ```bash
  pip install flask scikit-learn pandas numpy pyotp twilio joblib
  ```

### Steps to Run the Project

1. **Generate Random Data**:
   Run the following script to generate synthetic behavioral data:
   ```bash
   python generate_data.py
   ```

2. **Train the Model**:
   Train the AI model using the generated data:
   ```bash
   python train_model.py
   ```

3. **Run the Flask App**:
   Start the Flask backend:
   ```bash
   python app.py
   ```

4. **Open the Frontend**:
   Open `index.html` in your browser.

5. **Test the System**:
   - Move your mouse or click on the page.
   - Observe the status message updating in real-time.

6. **Trigger MFA**:
   If the model detects suspicious behavior, an OTP will be sent to the user's phone via Twilio.

## Notes
- Replace Twilio credentials (`account_sid`, `auth_token`, `from_`, `to`) with your actual details.
- Ensure the `behavior_model.pkl` file exists before running the Flask app.

## Future Improvements
- Add support for keystroke dynamics and other behavioral data.
- Use more advanced models like LSTM or Transformer.
- Deploy the system on a cloud platform (e.g., AWS, GCP).

## License
This project is open-source and available under the MIT License.
```