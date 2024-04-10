import psycopg2.extras
from flask import jsonify
from database import get_db

def add_event_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        user_email = data['user_email']
        rso = data['rso']
        name = data['name']
        category = data['category']
        time = data['time']
        description = data['description']
        location = data['location']
        phone = data['phone']
        contact_email = data['contact_email']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received add event request:', data)

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if user_id is None or user_id == '':
        return jsonify({'message': 'user ID is missing'}), 400
    
    if user_email is None or user_email == '':
        return jsonify({'message': 'user email is missing'}), 400
    
    if category is None or category == '':
        return jsonify({'message': 'Event category is missing'}), 400
    
    if rso is None and category != 'public' or rso == '':
        return jsonify({'message': 'RSO is missing, public events must have an RSO'}), 400

    if name is None or name == '':
        return jsonify({'message': 'Event name is missing'}), 400
    
    if time is None or time == '':
        return jsonify({'message': 'Event time is missing'}), 400
    
    if description is None or description == '':
        return jsonify({'message': 'Event description is missing'}), 400

    if location is None or location == '':
        return jsonify({'message': 'Event location is missing'}), 400
    
    if phone is None or phone == '':
        return jsonify({'message': 'Event phone is missing'}), 400
    
    if contact_email is None or contact_email == '':
        return jsonify({'message': 'Event email is missing'}), 400
    
    # Validate user id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if user is None:
        return jsonify({'message': 'Invalid user ID. User does not exist.'}), 401
    
    # Get the university of the user
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM universities WHERE email_domain = %s", (user_email.split('@')[1],))
        university = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from universities table based on email domain.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    # If the university doesn't exist, return an error
    if university is None:
        return jsonify({'message': 'Invalid user email domain. There are no existing universities with this email domain.'}), 401
    
    university = university['id']
    
    # If the event is public, add it to the pending events table
    if category == 'public':
        try:
            cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("INSERT INTO pending_events (university, author_id, approved, category, name, time, description, location, phone, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (university, user_id, False, category, name, time, description, location, phone, contact_email))
            db_connection.commit()
            return jsonify({'message': 'Public event submitted for approval'}), 200
        except psycopg2.Error as e:
            print(f"Error: {e}")
            return jsonify({'message': 'Error submitting public event for approval. SQL query failed.'}), 500
        finally:
            if cursor is not None:
                cursor.close()
    
    # If the event isn't public, insert the event into the database
    # Validate RSO ID
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM rso WHERE id = %s", (rso,))
        rso = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if rso is None:
        return jsonify({'message': 'Invalid RSO ID. RSO does not exist.'}), 401
    
    rso = rso['id']

    # Validate that the user is the admin of the RSO
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM rso WHERE id = %s AND admin = %s", (rso, user_id))
        results = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if results is None:
        return jsonify({'message': 'Invalid user authorization. User is not the admin of this RSO.'}), 401
    
    # Check that there is no overlapping event
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM events WHERE time = %s AND location = %s", (time, location))
        results = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if results is not None:
        return jsonify({'message': 'Error: Event Overlap. An event already exists at this time and location'}), 401

    # Add the event to the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("INSERT INTO events (university, author_id, approved, category, name, time, description, location, phone, email, rso) VALUES \
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (university, user_id, True, category, name, time, description, location, phone, contact_email, rso))
        db_connection.commit()
        return jsonify({'message': 'Event added successfully'}), 200
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error adding event to database. SQL query failed.'}), 500
    finally:
        if cursor is not None:
            cursor.close()