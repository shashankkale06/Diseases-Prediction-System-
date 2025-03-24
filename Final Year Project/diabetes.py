from flask import Flask, render_template, request, redirect
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
import mysql.connector

app = Flask(__name__)

# MySQL configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin123',
    'database': 'medical',
    'auth_plugin': 'mysql_native_password',
}

# Establish MySQL database connection
db_connection = mysql.connector.connect(**mysql_config)
cursor = db_connection.cursor()

# Load your dataset
df = pd.read_csv("dataset/diabetes.csv")

# Define features (X) and target variable (y)
X = df.drop('diabetes', axis=1)
y = df['diabetes']

# Define mappings for categorical variables
hypertension_mapping = {'No': 0, 'Yes': 1}
heart_disease_mapping = {'No': 0, 'Yes': 1}
gender_mapping = {'Female': 0, 'Male': 1}
smoking_history_mapping = {'Current': 0,  'Former': 1, 'Never': 2}

# Encode categorical variables
encoder = OneHotEncoder()
X_encoded = encoder.fit_transform(X[['gender', 'smoking_history']])
X_categorical = pd.DataFrame(X_encoded.toarray(), columns=encoder.get_feature_names_out(['gender', 'smoking_history']))

# Concatenate encoded categorical variables with numerical variables
X_numeric = X.drop(columns=['gender', 'smoking_history'])
X = pd.concat([X_numeric, X_categorical], axis=1)

# Define preprocessing pipeline
preprocessing_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='mean'))
])

# Fit preprocessing pipeline and transform data
X = preprocessing_pipeline.fit_transform(X)
X = pd.DataFrame(X, columns=X_numeric.columns.tolist() + X_categorical.columns.tolist())  # Convert back to DataFrame

# Create a random forest classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
rf_classifier.fit(X, y)

@app.route('/')
def index():
    return render_template('diabetes_ui.html')

@app.route('/home')
def home():
    return redirect("http://localhost:5000/home_2")

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        user_input = {}
        for feature in X.columns:
            value = request.form.get(feature)
            user_input[feature] = float(value) if value is not None else None  # Handle missing values

        # Convert user input to a DataFrame
        user_df = pd.DataFrame([user_input])

        # Impute missing values in user input
        user_df = pd.DataFrame(preprocessing_pipeline.transform(user_df), columns=user_df.columns)

        # Make predictions
        user_prediction = rf_classifier.predict(user_df)

        # Map the predicted outcome to text
        prediction_text = 'Patient is diagnosed with Diabetes.' if user_prediction[0] == 1 else 'Patient is not diagnosed with Diabetes.'

        # Insert user input and prediction into the database
        insert_query = "INSERT INTO diabetes2 (Age, Gender, Hypertension, Heart_Disease, BMI, HbA1c_Level, Blood_Glucose_Level, Smoking_History, Prediction) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (int(request.form['age']), request.form['gender'], request.form['hypertension'], request.form['heart_disease'], float(request.form['bmi']), float(request.form['HbA1c_level']), float(request.form['blood_glucose_level']), request.form['smoking_history'], prediction_text))
        db_connection.commit()

        pred_score = rf_classifier.predict_proba(user_df)
        score_pred = str(round(max(pred_score[0]) * 100, 2)) + "%"
        return render_template('diabites.html', prediction=prediction_text, pred_score = score_pred)

if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False)
