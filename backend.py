import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

# Simulate dataset
def simulate_data():
    np.random.seed(42)
    data = pd.DataFrame({
        'Location': np.random.choice(['Park', 'Market', 'Residential', 'School'], 100),
        'Time': np.random.choice(['Morning', 'Afternoon', 'Evening', 'Night'], 100),
        'Weather': np.random.choice(['Sunny', 'Rainy', 'Cloudy'], 100),
        'PopulationDensity': np.random.randint(100, 1000, 100),
        'PastIncidents': np.random.randint(0, 15, 100),
        'Incident': np.random.choice([0, 1], 100, p=[0.6, 0.4])
    })
    return data

# Encode categorical features
def preprocess_data(df):
    df_encoded = pd.get_dummies(df, columns=['Location', 'Time', 'Weather'], drop_first=True)
    return df_encoded

# Train model
def train_model():
    data = simulate_data()
    X = preprocess_data(data.drop('Incident', axis=1))
    y = data['Incident']
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    with open('PAWS_Project_Updated/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    return model, X.columns.tolist()

# Prediction function
def predict_incident(input_dict, feature_order):
    input_df = pd.DataFrame([input_dict])
    input_encoded = preprocess_data(input_df)
    for col in feature_order:
        if col not in input_encoded.columns:
            input_encoded[col] = 0
    input_encoded = input_encoded[feature_order]
    with open('PAWS_Project_Updated/model.pkl', 'rb') as f:
        model = pickle.load(f)
    prediction = model.predict(input_encoded)[0]
    confidence = model.predict_proba(input_encoded)[0][prediction]
    return prediction, confidence
