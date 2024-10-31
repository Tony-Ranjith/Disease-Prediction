import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MultiLabelBinarizer
import joblib

# Load the datasets
symptoms_data = pd.read_csv('datasets/symptoms_diseases.csv')

# Prepare the symptoms data
symptoms_data['Symptom_List'] = symptoms_data[['Symptom_1', 'Symptom_2', 'Symptom_3', 'Symptom_4',
                                                'Symptom_5', 'Symptom_6', 'Symptom_7', 'Symptom_8',
                                                'Symptom_9', 'Symptom_10', 'Symptom_11', 'Symptom_12',
                                                'Symptom_13', 'Symptom_14', 'Symptom_15', 'Symptom_16', 
                                                'Symptom_17']].apply(lambda x: [str(symptom) for symptom in x if pd.notnull(symptom)], axis=1)

# Remove rows with empty symptom lists
symptoms_data = symptoms_data[symptoms_data['Symptom_List'].map(lambda x: len(x) > 0)]

# Use MultiLabelBinarizer to transform symptoms into a binary format
mlb = MultiLabelBinarizer()
X = mlb.fit_transform(symptoms_data['Symptom_List'])
y = symptoms_data['Disease']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Make predictions and calculate accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Model accuracy: {accuracy * 100:.2f}%')

# Save the model and label binarizer
joblib.dump(model, 'disease_prediction_model.pkl')
joblib.dump(mlb, 'mlb.pkl')
