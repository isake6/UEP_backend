import psycopg2.extras
from flask import jsonify
from database import get_db

def get_user_rso_list_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received get user RSO list request:', data)

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if user_id is None or user_id == '':
        return jsonify({'message': 'User ID is missing'}), 400
    
    # Check that the user exists
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is None:
        return jsonify({'message': 'User ID is not in the database'}), 401
    
    # Get the RSOs that the user is a member of
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT rso_id FROM rso_members WHERE id = %s', (user_id,))
        rso_ids = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso_members table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    # Return results
    return jsonify({'rso_ids': rso_ids}), 200