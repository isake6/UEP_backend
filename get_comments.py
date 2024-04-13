import psycopg2.extras
from flask import jsonify, request
from database import get_db

def get_comments_handler(data):
    # Get the input from the request
    try:
        event_id = data['event_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400
    

    print('Received get comments request:')

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if event_id is None or event_id == '':
        return jsonify({'message': 'Event ID is missing'}), 400
    
    # Validate event id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM events WHERE id = %s', (event_id,))
        event = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if event is None:
        return jsonify({'message': 'Event ID is not in the database'}), 401
    
    # Get comments for the event
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM comments WHERE event_id = %s', (event_id,))
        comments = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from comments table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'comments': comments}), 200