from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import mysql.connector

app = Flask(__name__)

# Load the dataset
df = pd.read_csv("dataset/kidney_disease_renamed.csv")

# Preprocess the data
df['packed_cell_volume'] = pd.to_numeric(df['packed_cell_volume'], errors='coerce')
df['white_blood_cell_count'] = pd.to_numeric(df['white_blood_cell_count'], errors='coerce')
df['red_blood_cell_count'] = pd.to_numeric(df['red_blood_cell_count'], errors='coerce')

cat_cols = [col for col in df.columns if df[col].dtype == 'object']
num_cols = [col for col in df.columns if df[col].dtype != 'object']

# Replace special characters in categorical columns
df['diabetes_mellitus'].replace(to_replace={'\tno': 'no', '\tyes': 'yes', ' yes': 'yes'}, inplace=True)
df['coronary_artery_disease'] = df['coronary_artery_disease'].replace(to_replace='\tno', value='no')
df['class'] = df['class'].replace(to_replace={'ckd\t': 'ckd', 'notckd': 'not ckd'})

# Map class labels to numeric values
df['class'] = df['class'].map({'ckd': 0, 'not ckd': 1})
df['class'] = pd.to_numeric(df['class'], errors='coerce')

# Impute missing values
def random_value_imputation(feature):
    random_sample = df[feature].dropna().sample(df[feature].isna().sum())
    random_sample.index = df[df[feature].isnull()].index
    df.loc[df[feature].isnull(), feature] = random_sample

def impute_mode(feature):
    mode = df[feature].mode()[0]
    df[feature] = df[feature].fillna(mode)

for col in num_cols:
    random_value_imputation(col)
random_value_imputation('red_blood_cells')
random_value_imputation('pus_cell')

for col in cat_cols:
    impute_mode(col)

# Encode categorical variables
le = LabelEncoder()
for col in cat_cols:
    df[col] = le.fit_transform(df[col])

# Define features (X) and target variable (y)
X = df.drop('class', axis=1)
y = df['class']

# Define preprocessing pipeline
preprocessing_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='mean'))
])

# Fit preprocessing pipeline and transform data
X = preprocessing_pipeline.fit_transform(X)
X = pd.DataFrame(X, columns=df.drop('class', axis=1).columns)  # Convert numpy array back to DataFrame

# Ensure all labels are present in y
unique_labels = y.unique()
if 0 not in unique_labels:
    y = y.replace({1: 0, 2: 1})  # Assuming 1 and 2 are the existing labels

# Create a random forest classifier
rd_clf = RandomForestClassifier(criterion='entropy', max_depth=11, max_features='auto', min_samples_leaf=2, min_samples_split=3, n_estimators=130)
rd_clf.fit(X, y)

# MySQL database configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin123',
    'database': 'medical',
    'auth_plugin': 'mysql_native_password',
}

# Establish connection to MySQL database
db = mysql.connector.connect(**mysql_config)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('kidney_disease_ui.html')

@app.route('/home')
def home():
    return redirect("http://localhost:5000/home_2")

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        user_input = {}
        for feature in X.columns:
            value = request.form.get(feature)
            if value is not None:
                try:
                    user_input[feature] = float(value)
                except ValueError:
                    user_input[feature] = None  # or handle the error differently
            else:
                user_input[feature] = None  # Handle missing values

        # Convert user input to a DataFrame
        user_df = pd.DataFrame([user_input])

        # Impute missing values in user input
        user_df = pd.DataFrame(preprocessing_pipeline.transform(user_df), columns=user_df.columns)

        # Make predictions
        user_prediction = rd_clf.predict(user_df)

        # Map the predicted outcome to text
        prediction_text = 'Patient is diagnosed with Chronic Kidney Disease' if user_prediction[0] == 0 else 'Patient is not diagnosed with Chronic Kidney Disease'

        # Insert user data and prediction into the kidney table
        sql = """INSERT INTO kidney 
                         (age, blood_pressure, specific_gravity, albumin, sugar, red_blood_cells, pus_cell, 
                         pus_cell_clumps, bacteria, blood_glucose_random, blood_urea, serum_creatinine, sodium, 
                         potassium, haemoglobin, packed_cell_volume, white_blood_cell_count, red_blood_cell_count, 
                         hypertension, diabetes_mellitus, coronary_artery_disease, appetite, peda_edema, aanemia, 
                         predicted_value, Timestamp) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                         %s, %s, %s, %s, CURRENT_TIMESTAMP)"""

        # Get the predicted value (0 or 1)
        predicted_value = int(user_prediction[0])  # Ensure predicted value is converted to int

        # Convert values to native Python types for MySQL
        values = tuple(map(lambda x: float(x) if isinstance(x, np.floating) else x, user_df.values[0])) + (predicted_value,)

        # Execute SQL query to insert data into the kidney table
        cursor.execute(sql, values)

        # Commit the transaction
        db.commit()

        pred_score = rd_clf.predict_proba(user_df)
        score_pred = str(round(max(pred_score[0]) * 100, 2)) + "%"

        return render_template('kidney_disease_result.html', prediction=prediction_text, pred_score = score_pred)


if __name__ == '__main__':
    app.run(debug=True, port=5003, use_reloader=False)