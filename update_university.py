import psycopg2.extras
from flask import jsonify
from database import get_db

def update_university_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        university_id = data['university_id']
        new_name = data['new_name']
        new_location = data['new_location']
        new_description = data['new_description']
        new_population = data['new_population']
        new_lat = data['new_lat']
        new_long = data['new_long']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received update university request:', data)

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if user_id is None or user_id == '':
        return jsonify({'message': 'User ID is missing'}), 400
    
    if university_id is None or university_id == '':
        return jsonify({'message': 'University ID is missing'}), 400
    
    if new_name is None or new_name == '':
        return jsonify({'message': 'New name is missing'}), 400
    
    if new_location is None or new_location == '':
        return jsonify({'message': 'New location is missing'}), 400
    
    if new_description is None or new_description == '':
        return jsonify({'message': 'New description is missing'}), 400
    
    if new_population is None or new_population == '':
        return jsonify({'message': 'New population is missing'}), 400
    
    if new_lat is None or new_lat == '':
        return jsonify({'message': 'New latitude is missing'}), 400
    
    if new_long is None or new_long == '':
        return jsonify({'message': 'New longitude is missing'}), 400
    
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

    # Check that the university exists
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM universities WHERE id = %s', (university_id,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from universities table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is None:
        return jsonify({'message': 'University ID is not in the database'}), 401
    
    # Check if the user is the super_admin of this university
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM universities WHERE id = %s AND super_admin = %s', (university_id, user_id))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from universities table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is None:
        return jsonify({'message': 'User is not the super admin of this university'}), 401
    
    # Update university
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('UPDATE universities SET name = %s, location = %s, description = %s, student_population = %s, lat = %s, long = %s WHERE id = %s', (new_name, new_location, new_description, new_population, new_lat, new_long, university_id))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to update university.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'message': 'University updated successfully'}), 200