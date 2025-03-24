from flask import Flask, render_template, request, redirect
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
import mysql.connector

app = Flask(__name__)

# Connect to your MySQL database
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin123',
    'database': 'medical',
    'auth_plugin': 'mysql_native_password',
}
conn = mysql.connector.connect(**mysql_config)
cursor = conn.cursor()

# Load your dataset
df = pd.read_csv("dataset/heart.csv")

# Define features (X) and target variable (y)
X = df.drop('target', axis=1)
y = df['target']

# Mapping for chest pain, sex, exercise-induced angina, and slope
chest_pain_mapping = {0: 'Typical Angina', 1: 'Atypical Angina', 2: 'Non-Anginal Pain', 3: 'Asymptomatic'}
sex_mapping = {'male': 1, 'female': 0}
exang_mapping = {'No': 0, 'Yes': 1}
slope_mapping = {0: 'Upsloping', 1: 'Flat', 2: 'Downsloping'}
fbs_mapping = {0: 'False', 1: 'True'}
restecg_mapping = {0: 'Normal', 1: 'Abnormality', 2: 'Probable or Definite Left Ventricular Hypertrophy'}
thal_mapping = {0: 'Normal', 1: 'Mild Defect', 2: 'Fixed Defect', 3: 'Reversible Defect'}
ca_mapping = {0: 'No major vessels colored by fluoroscopy',
              1: 'One major vessel colored by fluoroscopy.',
              2: 'Two major vessels colored by fluoroscopy.',
              3: ' Three major vessels colored by fluoroscopy. ',
              4: 'Unusual'}

# Impute missing values
imputer = SimpleImputer(strategy='mean')
X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

# Create a random forest classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
rf_classifier.fit(X, y)

@app.route('/')
def index():
    return render_template('index.html', columns=X.columns,
                           chest_pain_mapping=chest_pain_mapping,
                           sex_mapping=sex_mapping,
                           exang_mapping=exang_mapping,
                           slope_mapping=slope_mapping,
                           fbs_mapping=fbs_mapping,
                           restecg_mapping=restecg_mapping,
                           thal_mapping=thal_mapping,
                           ca_mapping=ca_mapping)


@app.route('/home')
def home():
    return redirect("http://localhost:5000/home_2")


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        user_input = {}
        for feature in X.columns:
            value = request.form.get(feature)
            if feature == 'sex':
                user_input[feature] = sex_mapping.get(value.lower(), float('nan'))
            elif feature == 'exang':
                user_input[feature] = exang_mapping.get(value, float('nan'))
            elif feature == 'slope':
                user_input[feature] = slope_mapping.get(value, float('nan'))
            else:
                user_input[feature] = float(value)

        # Convert user input to a DataFrame
        user_df = pd.DataFrame([user_input])

        # Impute missing values in user input
        user_df = pd.DataFrame(imputer.transform(user_df), columns=user_df.columns)

        # Make predictions
        user_prediction = rf_classifier.predict(user_df)

        # Map the predicted outcome to text
        prediction_text = 'Patient is diagnosed with Heart Disease.' if user_prediction[0] == 1 else 'Patient is not diagnosed with Heart Disease.'

        # Store user input and predicted value into the database
        cursor.execute("INSERT INTO heart2 (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, predicted_value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (user_input['age'], user_input['sex'], user_input['cp'], user_input['trestbps'], user_input['chol'],
                        user_input['fbs'], user_input['restecg'], user_input['thalach'], user_input['exang'],
                        user_input['oldpeak'], user_input['slope'], user_input['ca'], user_input['thal'], prediction_text))
        conn.commit()
        pred_score = rf_classifier.predict_proba(user_df)
        score_pred = str(round(max(pred_score[0])*100, 2)) + "%"
        return render_template('result.html', prediction=prediction_text, pred_score = score_pred)

if __name__ == '__main__':
    app.run(debug=True, port=5002, use_reloader=False)
