import boto3
import psycopg2
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

def login_handler(data):
    # Get the username and password from the request
    username = data['username']
    password = data['password']

    print('Received login request:', data)

    # Input validation
    # If input is missing, return an error
    if username is None:
        return jsonify({'message': 'Username is missing'}), 400
    
    if password is None:
        return jsonify({'message': 'Password is missing'}), 400
    
    # Check if the user exists in the database
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    # If user does not exist, return an error
    if user is None:
        return jsonify({'message': 'User does not exist'}), 401
    
    # Check if the password is correct
    if user['password'] != password:
        return jsonify({'message': 'Incorrect password'}), 401
    
    # If the login is successful, return the user's information
    return jsonify({'username': user['username'], 'email': user['email'], 'role': user['role']}), 200
