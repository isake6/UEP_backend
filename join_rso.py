import psycopg2.extras
from flask import jsonify
from database import get_db

def join_rso_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        rso_id = data['rso_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received join RSO request:', data)

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if user_id is None or user_id == '':
        return jsonify({'message': 'User ID is missing'}), 400
    
    if rso_id is None or rso_id == '':
        return jsonify({'message': 'RSO ID is missing'}), 400
    
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
    
    # Check that the RSO exists
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM rso WHERE id = %s', (rso_id,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rsos table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is None:
        return jsonify({'message': 'RSO ID is not in the database'}), 401
    
    # Check that the user is not already in the RSO
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM rso_members WHERE user_id = %s AND rso_id = %s', (user_id, rso_id))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso_members table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is not None:
        return jsonify({'message': 'User is already in this RSO'}), 401
    
    # Add the user to the RSO
    try:
        cursor = db_connection.cursor()
        cursor.execute('INSERT INTO rso_members (user_id, rso_id) VALUES (%s, %s)', (user_id, rso_id))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to insert into rso_members table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'message': 'User joined RSO successfully'}), 200