import psycopg2.extras
from flask import jsonify
from database import get_db

def add_comment_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        event_id = data['event_id']
        comment = data['comment']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received add comment request:', data)

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
    
    if comment is None or comment == '':
        return jsonify({'message': 'Comment is missing'}), 400

    # Validate author id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if user is None:
        return jsonify({'message': 'User ID is not in the database'}), 401
    
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

    # Insert the comment into the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('INSERT INTO comments (author_id, event_id, comment, created_time) VALUES (%s, %s, %s, NOW())', (user_id, event_id, comment))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to insert into comments table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'message': 'Comment added successfully'}), 200