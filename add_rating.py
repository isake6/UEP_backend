import psycopg2.extras
from flask import jsonify
from database import get_db

def add_rating_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        event_id = data['event_id']
        rating = data['rating']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received add rating request:', data)

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
    
    if rating is None or rating == '':
        return jsonify({'message': 'Rating is missing'}), 400

    # Validate User id
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
    
    # Prevent users from rating the same event twice
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM ratings WHERE author_id = %s AND event_id = %s', (user_id, event_id))
        duplicate_ratings = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from ratings table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if duplicate_ratings is not None:
        return jsonify({'message': 'User has already rated this event'}), 401
    
    # Validate rating range
    if rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400

    # Insert the rating into the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('INSERT INTO ratings (author_id, event_id, rating) VALUES (%s, %s, %s)', (user_id, event_id, rating))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to insert into ratings table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'message': 'Rating added successfully'}), 200