import boto3
import psycopg2.extras
from json import dumps, loads
import os
from flask import Response, jsonify

# Database connection
db_connection = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

def signup_handler(data):
    # Get the input from the request
    email = data['email']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    role = data['role']

    print('Received signup request:', data)

    # Input validation
    # If input is missing, return an error
    if email is None:
        return jsonify({'message': 'email is missing'}), 400
    
    if password is None:
        return jsonify({'message': 'Password is missing'}), 400
    
    if first_name is None:
        return jsonify({'message': 'First name is missing'}), 400
    
    if last_name is None:
        return jsonify({'message': 'Last name is missing'}), 400
    
    if role is None:
        return jsonify({'message': 'Role is missing'}), 400
    
    # Check if the user exists in the database
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    # If user already exists, return an error
    if user is not None:
        return jsonify({'message': 'Email taken. User already exists.'}), 401
    
    # Add the user to the database
    try:
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO users (email, password, first_name, last_name, role) VALUES (%s, %s, %s, %s, %s)", (email, password, first_name, last_name, role))
        db_connection.commit()
        cursor.close()
    except Exception as e:
        return jsonify({'message': 'Error adding user to database. SQL query could not be completed.'}), 500

    # If the signup is successful, return 200 status code
    return jsonify({'message': 'Signup successful.'}), 200