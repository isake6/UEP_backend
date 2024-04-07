import psycopg2.extras
from flask import jsonify
from database import get_db

def login_handler(data):
    # Get the username and password from the request
    try:
        email = data['email']
        password = data['password']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection

    cursor = None

    print('Received login request:', data)

    # Input validation
    # If input is missing, return an error
    if email is None or email == '':
        return jsonify({'message': 'email is missing'}), 400
    
    if password is None or password == '':
        return jsonify({'message': 'Password is missing'}), 400
    
    # Check if the user exists in the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    # If user does not exist, return an error
    if user is None:
        return jsonify({'message': 'User does not exist'}), 401
    
    # Check if the password is correct
    if user['password'] != password:
        return jsonify({'message': 'Incorrect password'}), 401
    
    # Get the university of the user
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM universities WHERE email_domain = %s", (email.split('@')[1],))
        university = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from universities table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    university_id = university['id']
    
    # If the login is successful, return the user's information
    return jsonify({'id': user['id'], 'first_name': user['first_name'], 'last_name': user['last_name'], 'email': user['email'], 'role': user['role'], 'university_id': university_id}), 200
