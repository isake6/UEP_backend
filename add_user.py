import psycopg2.extras
from flask import jsonify
from database import get_db

def signup_handler(data):
    # Get the input from the request
    try:
        email = data['email']
        password = data['password']
        first_name = data['firstName']
        last_name = data['lastName']
        role = data['role']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400
    
    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection

    cursor = None

    print('Received signup request:', data)

    # Input validation
    if email is None or email == '':
        return jsonify({'message': 'email is missing'}), 400
    
    if password is None or password == '':
        return jsonify({'message': 'Password is missing'}), 400
    
    if first_name is None or first_name == '':
        return jsonify({'message': 'First name is missing'}), 400
    
    if last_name is None or last_name == '':
        return jsonify({'message': 'Last name is missing'}), 400
    
    if role is None or role == '':
        return jsonify({'message': 'Role is missing'}), 400
    
    # Check if the email domain is valid
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

    if university is None:
        return jsonify({'message': 'Invalid email domain. There are no existing universities with this email domain.'}), 401
    
    university_id = university['id']

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

    # If user already exists, return an error
    if user is not None:
        return jsonify({'message': 'Email taken. User already exists.'}), 401
    
    # Add the user to the database
    try:
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO users (email, password, first_name, last_name, role, university_id) VALUES (%s, %s, %s, %s, %s, %s)", (email, password, first_name, last_name, role, university_id))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error adding user to database. SQL query could not be completed.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    # If the signup is successful, return 200 status code
    return jsonify({'message': 'Signup successful.'}), 200