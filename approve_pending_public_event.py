import psycopg2.extras
from flask import jsonify
from database import get_db

def approve_pending_public_event_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        university_id = data['university_id']
        event_id = data['event_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received approve pending public event request:', data)

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
    
    # Retrieve event details
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM pending_events WHERE id = %s', (event_id,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from pending events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()
    
    if result is None:
        return jsonify({'message': 'Event ID is not in the database'}), 401
    
    event = result

    # Check if there is an overlap with existing events
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM events WHERE location = %s AND time = %s', (event['location'], event['time']))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is not None:
        return jsonify({'message': 'Event overlaps with an existing event'}), 401

    # Remove from pending events table
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('DELETE FROM pending_events WHERE id = %s', (event_id,))
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to delete from pending events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    # Add event to events table
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('INSERT INTO events (name, author_id, phone, email, approved, description, location, time, university, category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id', (event['name'], event['author_id'], event['phone'], event['email'], True, event['description'], event['location'], event['time'], event['university'], event['category']))
        event_id = cursor.fetchone()['id']
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to insert into events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()
    
    return jsonify({'message': 'Event approved successfully', 'event_id': event_id}), 200