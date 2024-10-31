import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.preprocessing import MultiLabelBinarizer
import joblib

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory user storage
users = {}

# Load the datasets
symptoms_data = pd.read_csv('datasets/symptoms_diseases.csv')
precautions_data = pd.read_csv('datasets/disease_precautions.csv')

# Prepare the symptoms data
symptoms_data['Symptom_List'] = symptoms_data[['Symptom_1', 'Symptom_2', 'Symptom_3', 'Symptom_4',
                                                'Symptom_5', 'Symptom_6', 'Symptom_7', 'Symptom_8',
                                                'Symptom_9', 'Symptom_10', 'Symptom_11', 'Symptom_12',
                                                'Symptom_13', 'Symptom_14', 'Symptom_15', 'Symptom_16', 
                                                'Symptom_17']].apply(lambda x: [str(symptom) for symptom in x if pd.notnull(symptom)], axis=1)

# Use MultiLabelBinarizer to transform symptoms into a binary format
mlb = MultiLabelBinarizer()
X = mlb.fit_transform(symptoms_data['Symptom_List'])
y = symptoms_data['Disease']

# Load the trained model
model = joblib.load('disease_prediction_model.pkl')

# Get unique symptoms for the form
unique_symptoms = mlb.classes_

# Home route (login page)
@app.route('/')
def login():
    return render_template('login.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        if username in users:
            flash('Username already exists!')
            return redirect(url_for('register'))

        # Hash the password and store the user
        hashed_password = generate_password_hash(password)
        users[username] = hashed_password

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists and verify the password
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('main'))
        else:
            flash('Invalid username or password. Please try again.')
            return redirect(url_for('login'))
    return render_template('login.html')

# Main page for selecting symptoms and predicting disease
@app.route('/main')
def main():
    if 'username' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    return render_template('index.html', unique_symptoms=unique_symptoms)

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    selected_symptoms = request.form.getlist('symptoms')

    if not selected_symptoms:
        return render_template('index.html', unique_symptoms=unique_symptoms, message="Please select at least one symptom.")

    # Transform the selected symptoms to the same format used for training
    symptom_vector = mlb.transform([selected_symptoms])

    # Predict the disease
    predicted_disease = model.predict(symptom_vector)[0]

    # Retrieve precautions for the predicted disease
    precautions = precautions_data.loc[precautions_data['Disease'] == predicted_disease]

    if precautions.empty:
        precautions_list = ["No precautions found."]
    else:
        precautions_list = precautions.iloc[0, 1:].dropna().tolist()  # Get the precautions excluding the disease name

    return render_template('result.html', predicted_disease=predicted_disease, precautions=precautions_list)

# Route for disease information
@app.route('/disease_info/<disease>')
def disease_info(disease):
    # Assuming you have a separate dataset or method to retrieve disease details
    disease_details = symptoms_data[symptoms_data['Disease'] == disease].iloc[0]
    return render_template('disease_info.html', disease=disease, details=disease_details)

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)











