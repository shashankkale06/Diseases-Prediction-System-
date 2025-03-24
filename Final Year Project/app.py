from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from email_validator import validate_email, EmailNotValidError
import re

app = Flask(__name__)
# app.run(host='127.0.0.1', port=5001)
app.secret_key = 'your_secret_key'

# MySQL configurations (assuming the credentials are correct)
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin123',
    'database': 'medical',
    'auth_plugin': 'mysql_native_password',
}

# Function to execute MySQL queries
def execute_query(query, data=None, fetch_one=False):
    try:
        # Establish a connection
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        # Execute the query with parameterized data
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

        # Fetch and process results
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()

        # Commit the changes
        conn.commit()

        return result

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        # Optionally log the error or handle it in a way that fits your application

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = "SELECT username, password FROM login WHERE username = %s"
        data = (username,)
        result = execute_query(query, data, fetch_one=True)

        # If the username doesn't exist or password doesn't match, flash an error
        if not result or result[1] != password:
            flash('Invalid credentials. Please try again.', 'error')

        # If the username and password match, redirect to 'home_2'
        elif result and result[1] == password:
            return redirect(url_for('home_2'))

    # Always render login.html for GET or failed POST requests
    return render_template('login.html')


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        date_of_birth = request.form['dob']
        password = request.form['password']

        try:
            # Validate full name (no numbers or special characters)
            if not re.match("^[A-Za-z ]+$", full_name):
                raise ValueError('Invalid full name. Please use only letters and spaces.')

            # Validate email format
            v = validate_email(email)
            email = v.email

            # Validate password (allow everything, customize as needed)
            if not password:
                raise ValueError('Password cannot be empty.')

            # Validate phone number (10 digits, no letters or special characters)
            if not re.match("^[0-9]{10}$", phone_number):
                raise ValueError('Invalid phone number. Please enter 10 digits without spaces or special characters.')

            # Check if the email is already registered for regular users
            existing_user_query = "SELECT email FROM registration WHERE email = %s"
            existing_user_data = (email,)
            existing_user_result = execute_query(existing_user_query, existing_user_data, fetch_one=True)

            if existing_user_result:
                flash('Email is already registered. Please use a different email address.', 'error')
                return render_template('registration.html')

            # Insert data into the registration table with parameterized query
            registration_query = "INSERT INTO registration (full_name, email, phone, dob, password) VALUES (%s, %s, %s, %s, %s)"
            registration_data = (full_name, email, phone_number, date_of_birth, password)
            execute_query(registration_query, registration_data)

            # Insert data into the login table with parameterized query
            login_query = "INSERT INTO login (username, password) VALUES (%s, %s)"
            login_data = (email, password)
            execute_query(login_query, login_data)

            # Flash message for successful registration
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        except (EmailNotValidError, ValueError) as e:
            flash(str(e), 'error')
            return render_template('registration.html')

    return render_template('registration.html')

# Remove or comment out this route definition to avoid conflict
@app.route('/home_2')
def home_2():
    return render_template('dashboard.html')

@app.route('/diagnosis')
def diagnosis():
    return render_template('diagnosis.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/diabetes')
def diabetes():
    return redirect('http://localhost:5001/')

@app.route('/heart')
def heart():
    return redirect('http://localhost:5002/')

@app.route('/kidney')
def kidney():
    return redirect('http://localhost:5003/')

@app.route('/lung')
def lung():
    return redirect('http://localhost:5004/')

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
# app.run(host='127.0.0.1', port=5001)