import boto3
import psycopg2.extras
from json import dumps, loads
import os
from flask import Response, jsonify

# Database connection
db_connection = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

def add_event_handler(data):
    # Get the input from the request
    author_id = data['author_id']
    author_email = data['author_email']
    rso = data['rso']
    name = data['name']
    category = data['category']
    time = data['time']
    description = data['description']
    location = data['location']
    phone = data['phone']
    email = data['email']

    print('Received add event request:', data)

    # Input validation for empty fields
    
    if author_id is None:
        return jsonify({'message': 'Author ID is missing'}), 400
    
    if author_email is None:
        return jsonify({'message': 'Author email is missing'}), 400
    
    if category is None:
        return jsonify({'message': 'Event category is missing'}), 400
    
    if rso is None and category != 'public':
        return jsonify({'message': 'RSO is missing, public events must have an RSO'}), 400

    if name is None:
        return jsonify({'message': 'Event name is missing'}), 400
    
    if time is None:
        return jsonify({'message': 'Event time is missing'}), 400
    
    if description is None:
        return jsonify({'message': 'Event description is missing'}), 400

    if location is None:
        return jsonify({'message': 'Event location is missing'}), 400
    
    if phone is None:
        return jsonify({'message': 'Event phone is missing'}), 400
    
    if email is None:
        return jsonify({'message': 'Event email is missing'}), 400
    
    # Validate author id
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (author_id,))
    author = cursor.fetchone()
    cursor.close()

    if author is None:
        return jsonify({'message': 'Invalid author ID. User does not exist.'}), 401
    
    # Get the university of the author
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM universities WHERE email_domain = %s", (author_email.split('@')[1],))
    university = cursor.fetchone()
    cursor.close()

    # If the university doesn't exist, return an error
    if university is None:
        return jsonify({'message': 'Invalid author email domain. There are no existing universities with this email domain.'}), 401
    
    university = university['id']
    
    # If the event is public, add it to the pending events table
    if category == 'public':
        try:
            cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("INSERT INTO pending_events (university, author_id, approved, category, name, time, description, location, phone, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (university, author_id, False, category, name, time, description, location, phone, email))
            db_connection.commit()
            cursor.close()

            return jsonify({'message': 'Public event submitted for approval'}), 200
        
        except Exception as e:
            return jsonify({'message': 'Error submitting public event for approval. SQL query failed.'}), 500
    
    # If the event isn't public, insert the event into the database
    # Validate RSO ID
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM rso WHERE id = %s", (rso,))
    rso = cursor.fetchone()
    cursor.close()

    if rso is None:
        return jsonify({'message': 'Invalid RSO ID. RSO does not exist.'}), 401
    
    rso = rso['id']

    # Validate that the author is the admin of the RSO
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM rso WHERE id = %s AND admin = %s", (rso, author_id))
    results = cursor.fetchone()
    cursor.close()

    if results is None:
        return jsonify({'message': 'Invalid user authorization. User is not the admin of this RSO.'}), 401

    # Add the event to the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("INSERT INTO events (university, author_id, approved, category, name, date, time, description, location, phone, email, rso) VALUES \
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (university, author_id, True, category, name, time, description, location, phone, email, rso))
        db_connection.commit()
        cursor.close()

        return jsonify({'message': 'Event added successfully'}), 200
    
    except Exception as e:
        return jsonify({'message': 'Error adding event to database. SQL query failed.'}), 500