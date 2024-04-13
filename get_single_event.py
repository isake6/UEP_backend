import psycopg2.extras
from flask import jsonify
from database import get_db

def get_single_event_handler(data):
    # Get the input from the request
    try:
        event_id = data['event_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400
    
    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    print('Received get event request:', data)

    # Input validation for empty fields
    if event_id is None or event_id == '':
        return jsonify({'message': 'Event ID is missing'}), 400
    
    # Get events from database
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

    return jsonify({'event': event}), 200
