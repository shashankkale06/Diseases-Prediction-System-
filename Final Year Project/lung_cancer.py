from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler
import mysql.connector

app = Flask(__name__)

# Load your lung survey dataset
df = pd.read_csv("dataset/survey lung cancer.csv")
pd.set_option('display.max_columns', None)

# Check if the 'FATIGUE' column is present in the DataFrame
if 'FATIGUE' not in df.columns:
    raise ValueError("The 'FATIGUE' column is not present in the dataset.")

# Encode categorical columns
encoder = LabelEncoder()
categorical_columns = ['GENDER', 'SMOKING', 'YELLOW_FINGERS', 'ANXIETY', 'PEER_PRESSURE', 'CHRONIC DISEASE', 'FATIGUE',
                       'ALLERGY', 'WHEEZING', 'ALCOHOL CONSUMING', 'COUGHING', 'SHORTNESS OF BREATH',
                       'SWALLOWING DIFFICULTY', 'CHEST PAIN', 'LUNG_CANCER']

for col in categorical_columns:
    df[col] = encoder.fit_transform(df[col])

# Separate features (X) and target variable (y)
X = df.drop(['LUNG_CANCER'], axis=1)
y = df['LUNG_CANCER']

# Apply oversampling
X_over, y_over = RandomOverSampler().fit_resample(X, y)

# Create and train the random forest classifier
model3 = RandomForestClassifier(n_estimators=90, random_state=42, max_depth=12, max_features='sqrt', min_samples_split=15)
model3.fit(X_over, y_over)

# MySQL configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin123',
    'database': 'medical',  # Updated database name
    'auth_plugin': 'mysql_native_password',
}

# Connect to MySQL database
db = mysql.connector.connect(**mysql_config)
cursor = db.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS lung_cancer_predictions (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  age FLOAT,
                  gender VARCHAR(10),
                  smoking INT,
                  yellow_fingers INT,
                  anxiety INT,
                  peer_pressure INT,
                  chronic_disease INT,
                  fatigue INT,
                  allergy INT,
                  wheezing INT,
                  alcohol_consuming INT,
                  coughing INT,
                  shortness_of_breath INT,
                  swallowing_difficulty INT,
                  chest_pain INT,
                  predicted_value INT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                  )''')
db.commit()

@app.route('/')
def index():
    return render_template('lung_cancer_ui.html', columns=X.columns.tolist())

@app.route('/home')
def home():
    return redirect("http://localhost:5000/home_2")

@app.route('/predict', methods=['POST'])
def predict():
    user_input = {}
    for feature in X.columns:
        if feature == 'AGE':
            value = float(request.form.get(feature))
        elif feature == 'GENDER':
            value = request.form.get(feature).capitalize()
            value = 1 if value == 'Male' else 0
        elif feature in categorical_columns:
            value = request.form.get(feature)
            value = 1 if value == '1' else 0  # Convert to numerical representation
        else:
            value = float(request.form.get(feature))
        user_input[feature] = value

    # Create a DataFrame with the user input
    user_df = pd.DataFrame([user_input])

    # Make predictions
    user_prediction = model3.predict(user_df)

    # Map the predicted outcome to text
    prediction_text = 'Patient is not diagnosed with Lung Cancer' if user_prediction[0] == 0 else 'Patient is diagnosed with Lung Cancer'

    # Convert floating-point values to Python float objects
    for feature in user_df.columns:
        if isinstance(user_df[feature].iloc[0], np.float64):
            user_df[feature] = float(user_df[feature].iloc[0])

    # Store user input and prediction in MySQL database
    sql = '''INSERT INTO lung_cancer_predictions 
             (age, gender, smoking, yellow_fingers, anxiety, peer_pressure, chronic_disease, fatigue,
             allergy, wheezing, alcohol_consuming, coughing, shortness_of_breath, swallowing_difficulty, chest_pain,
             predicted_value) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

    # Convert float values to compatible MySQL data types
    values = tuple(map(lambda x: str(x) if isinstance(x, np.float64) else x, user_df.values[0])) + (int(user_prediction[0]),)
    cursor.execute(sql, values)
    db.commit()

    pred_score = model3.predict_proba(user_df)
    score_pred = str(round(max(pred_score[0]) * 100, 2)) + "%"
    return render_template('lung_cancer_result.html', prediction_text=prediction_text, pred_score = score_pred)

if __name__ == '__main__':
    app.run(debug=True, port=5004, use_reloader=False)

