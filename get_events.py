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
    
    # Check if user exists in the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        results = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if results is None:
        return jsonify({'message': 'User ID is not in the database'}), 401
    
    # Check if the university exists in the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM universities WHERE id = %s", (university_id,))
        results = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from universities table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if results is None:
        return jsonify({'message': 'University ID is not in the database'}), 401
    
    # Get events from database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('''(SELECT *, coordinates::text FROM events E WHERE E.category = 'private' AND E.university = %s) \
            UNION \
            (SELECT *, coordinates::text FROM events E WHERE E.category = 'public') \
            UNION \
            (SELECT E.*, coordinates::text FROM events E, rso_members M WHERE E.category = 'RSO' AND E.rso = M.rso_id AND M.id = %s)''' \
            , (university_id, user_id))
        events = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'events': events}), 200
