import psycopg2.extras
from flask import jsonify
from database import get_db

def delete_event_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        event_id = data['event_id']
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
    
    if event_id is None or event_id == '':
        return jsonify({'message': 'Event ID is missing'}), 400
    
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
    
    # Check that the event exists
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM events WHERE id = %s', (event_id,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is None:
        return jsonify({'message': 'Event ID is not in the database'}), 401
    
    # Check that the user_id matches the author_id of the event
    if result['author_id'] != user_id:
        return jsonify({'message': 'You are not the author of the event'}), 401
    
    # Delete the event
    try:
        cursor = db_connection.cursor()
        cursor.execute('DELETE FROM events WHERE id = %s', (event_id,))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to delete from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()
    
    return jsonify({'message': 'Event deleted successfully'}), 200