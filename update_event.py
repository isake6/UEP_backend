import psycopg2.extras
from flask import jsonify
from database import get_db

def update_event_handler(data):
    # Get the input from the request
    try:
        event_id = data['event_id']
        name = data['name']
        category = data['category']
        time = data['time']
        description = data['description']
        location = data['location']
        phone = data['phone']
        contact_email = data['contact_email']
        lat = data['lat']
        long = data['long']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400
    
    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    print('Received update event request:', data)

    # Input validation for empty fields
    if event_id is None or event_id == '':
        return jsonify({'message': 'Event ID is missing'}), 400
    
    if name is None or name == '':
        return jsonify({'message': 'Event name is missing'}), 400
    
    if category is None or category == '':
        return jsonify({'message': 'Event category is missing'}), 400
    
    if time is None or time == '':
        return jsonify({'message': 'Event time is missing'}), 400
    
    if description is None or description == '':
        return jsonify({'message': 'Event description is missing'}), 400
    
    if location is None or location == '':
        return jsonify({'message': 'Event location is missing'}), 400
    
    if phone is None or phone == '':
        return jsonify({'message': 'Event phone is missing'}), 400
    
    if contact_email is None or contact_email == '':
        return jsonify({'message': 'Event contact email is missing'}), 400
    
    if lat is None or lat == '':
        return jsonify({'message': 'Event latitude is missing'}), 400
    
    if long is None or long == '':
        return jsonify({'message': 'Event longitude is missing'}), 400
    
    # Check that event exists in the database
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
        return jsonify({'message': 'Event does not exist'}), 400
    
    # Check that the new time and location are not already taken
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM events WHERE time = %s AND location = %s', (time, location))
        event = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if event is not None:
        if len(event) > 1 or (len(event) == 1 and event[0]['id'] != event_id):
            print('Event with the same time and location already exists')
            return jsonify({'message': 'Event with the same time and location already exists'}), 400
        
    # Do a similar overlap check but with lat and long
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM events WHERE time = %s AND lat = %s AND long = %s', (time, lat, long))
        event = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if event is not None:
        if len(event) > 1 or (len(event) == 1 and event[0]['id'] != event_id):
            print('Event with the same time and location already exists')
            return jsonify({'message': 'Event with the same time and coordinates already exists'}), 400
    
    
    # Update event in database
    try:
        cursor = db_connection.cursor()
        cursor.execute('UPDATE events SET name = %s, category = %s, time = %s, description = %s, location = %s, phone = %s, email = %s, lat = %s, long = %s WHERE id = %s', (name, category, time, description, location, phone, contact_email, lat, long, event_id))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to update event in events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'message': 'Event updated successfully'}), 200