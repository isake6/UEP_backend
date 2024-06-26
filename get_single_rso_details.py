import psycopg2.extras
from flask import jsonify, request
from database import get_db

def get_single_rso_details_handler(data):
    # Get the input from the request
    try:
        rso_id = data['rso_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400
    

    print('Received get single RSO details request:')

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if rso_id is None or rso_id == '':
        return jsonify({'message': 'RSO ID is missing'}), 400
    
    # Validate rso id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM rso WHERE id = %s', (rso_id,))
        rso = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if rso is None:
        return jsonify({'message': 'RSO ID is not in the database'}), 401
    
    # Get rso admin email
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT email FROM users WHERE id = %s', (rso['admin'],))
        admin_email = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if admin_email is None:
        return jsonify({'message': 'Admin email not found'}), 401

    rso['admin_email'] = admin_email['email']
    
    return jsonify({'rso_details': rso}), 200