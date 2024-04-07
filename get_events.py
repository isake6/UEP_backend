import psycopg2.extras
from flask import jsonify
from database import get_db

def get_events_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        university_id = data['university_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400
    
    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    print('Received get events request:', data)

    # Input validation for empty fields
    if user_id is None or user_id == '':
        return jsonify({'message': 'User ID is missing'}), 400
    
    if university_id is None or university_id == '':
        return jsonify({'message': 'University ID is missing'}), 400
    
    # Get events from database
    try:
        cursor = db_connection.cursor()
        cursor.execute('''SELECT * FROM events E, rso_members M \
                       WHERE E.category = 'private' AND university_id = %s \
                       OR E.category = 'public' \
                       OR E.category = 'RSO' AND E.rso = M.rso_id AND M.id = %s''', (university_id, user_id))
        events = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'events': events}), 200
