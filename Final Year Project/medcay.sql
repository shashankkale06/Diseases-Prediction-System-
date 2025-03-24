create database medical;
use medical;
CREATE TABLE registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    dob DATE NOT NULL,
    password VARCHAR(255)
);
DELETE FROM login;

registrationselect * from login;
CREATE TABLE login (
username VARCHAR(255) NOT NULL,
password VARCHAR(255)
);

select * from registration;
delete from login where username = 'shashankkale2003@gmail.com';
DELETE FROM login;
SET sql_safe_updates = 0;


CREATE TABLE heart2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    age FLOAT,
    sex FLOAT,
    cp FLOAT,
    trestbps FLOAT,
    chol FLOAT,
    fbs FLOAT,
    restecg FLOAT,
    thalach FLOAT,
    exang FLOAT,
    oldpeak FLOAT,
    slope FLOAT,
    ca FLOAT,
    thal FLOAT,
    predicted_value VARCHAR(225),
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from lung_cancer_predictions;
select * from heart2;
select * from diabetes2;
select * from kidney;

CREATE TABLE diabetes2 (
    id INT AUTO_INCREMENT PRIMARY KEY,

    Age INT NOT NULL,
    Gender VARCHAR(10) NOT NULL,
    Hypertension VARCHAR(100) NOT NULL,
    Heart_Disease VARCHAR(100) NOT NULL,
    BMI FLOAT NOT NULL,
    HbA1c_Level FLOAT NOT NULL,
    Blood_Glucose_Level FLOAT NOT NULL,
    Smoking_History VARCHAR(100) NOT NULL,
    Prediction VARCHAR(50) NOT NULL,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE kidney (
	id INT AUTO_INCREMENT PRIMARY KEY,
    age INT,
    blood_pressure VARCHAR(255),
    specific_gravity FLOAT,
    albumin INT,
    sugar INT,
    red_blood_cells INT,
    pus_cell INT,
    pus_cell_clumps INT,
    bacteria INT,
    blood_glucose_random VARCHAR(255),
    blood_urea VARCHAR(255),
    serum_creatinine VARCHAR(255),
    sodium VARCHAR(255),
    potassium VARCHAR(255),
    haemoglobin VARCHAR(255),
    packed_cell_volume VARCHAR(255),
    white_blood_cell_count VARCHAR(255),
    red_blood_cell_count VARCHAR(255),
    hypertension INT,
    diabetes_mellitus INT,
    coronary_artery_disease INT,
    appetite VARCHAR(255),
    peda_edema VARCHAR(255),
    aanemia VARCHAR(255),
    predicted_value INT,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from heart2;

CREATE TABLE lung_cancer_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    age FLOAT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    smoking INT NOT NULL,
    yellow_fingers INT NOT NULL,
    anxiety INT NOT NULL,
    peer_pressure INT NOT NULL,
    chronic_disease INT NOT NULL,
    fatigue INT NOT NULL,
    allergy INT NOT NULL,
    wheezing INT NOT NULL,
    alcohol_consuming INT NOT NULL,
    coughing INT NOT NULL,
    shortness_of_breath INT NOT NULL,
    swallowing_difficulty INT NOT NULL,
    chest_pain INT NOT NULL,
    predicted_lung_cancer INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE heart MODIFY predicted_value VARCHAR(255);
select * from registration;
CREATE TABLE registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone int,
    dob DATE NOT NULL,
    password VARCHAR(255)
);

select *from registration;
