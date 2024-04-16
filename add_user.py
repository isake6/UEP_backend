import psycopg2.extras
from flask import jsonify
from database import get_db
import re

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
    
    if not re.match(r'\S+@\S+.(com|net|org|edu)$', email):
       return jsonify({'message': 'Invalid email address.'}), 400
    
    if password is None or password == '':
        return jsonify({'message': 'Password is missing'}), 400
    
    if first_name is None or first_name == '':
        return jsonify({'message': 'First name is missing'}), 400
    
    if last_name is None or last_name == '':
        return jsonify({'message': 'Last name is missing'}), 400
    
    if role is None or role == '':
        return jsonify({'message': 'Role is missing'}), 400
    
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
    
    # Check if the email domain is valid
    if role != 'super admin':
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
    
    else:
        try:
            cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("SELECT id FROM universities WHERE email_domain = %s", (email.split('@')[1],))
            university_check = cursor.fetchone()
            if university_check is not None:
                return jsonify({'message': 'Invalid email domain. A university with this email domain already exists.'}), 401
            cursor.execute("INSERT INTO universities (name, email_domain) VALUES (%s, %s) RETURNING id", ((email + ' University'), email.split('@')[1]))
            new_university = cursor.fetchone()
        except psycopg2.Error as e:
            print(f"Error: {e}")
            return jsonify({'message': 'Error adding university to database. SQL query could not be completed.'}), 500
        finally:
            if cursor is not None:
                cursor.close()

        university_id = new_university['id']
    
    # Add the user to the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("INSERT INTO users (email, password, first_name, last_name, role, university_id) VALUES (%s, %s, %s, %s, %s, %s)", (email, password, first_name, last_name, role, university_id))
        # Update the admin of the new university
        if role == 'super admin':
            try:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                admin = cursor.fetchone()
                if admin is None:
                    return jsonify({'message': 'Error updating university admin. User not found.'}), 500
                admin = admin['id']
                cursor.execute("UPDATE universities SET super_admin = %s WHERE id = %s", (admin, university_id))
            except psycopg2.Error as e:
                print(f"Error: {e}")
                return jsonify({'message': 'Error updating university admin. SQL query could not be completed.'}), 500
            finally:
                if cursor is not None:
                    cursor.close()
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error adding user to database. SQL query could not be completed.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    # If the signup is successful, return 200 status code
    return jsonify({'message': 'Signup successful.'}), 200