import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Load labeled data
def load_labeled_data(file_path):
    data = pd.read_csv(file_path)
    X = data.drop(columns=['label'])
    y = data['label']
    return X, y

# Train the model
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    return model

# Save the trained model
def save_model(model, file_path):
    joblib.dump(model, file_path)

if __name__ == '__main__':
    # Load labeled data
    labeled_data_file = 'labeled_behavior_data.csv'
    X, y = load_labeled_data(labeled_data_file)

    # Train the model
    model = train_model(X, y)

    # Save the trained model
    save_model(model, 'behavior_model.pkl')

    print("Model trained and saved successfully!")