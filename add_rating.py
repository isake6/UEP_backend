import boto3
import psycopg2.extras
from json import dumps, loads
import os
from flask import Response, jsonify
from database import get_db

def add_rating_handler(data):
    # Get the input from the request
    user_id = data['user_id']
    event_id = data['event_id']
    rating = data['rating']

    print('Received add rating request:', data)

    # Database connection
    db_connection = get_db()

    # Input validation for empty fields
    if user_id is None:
        return jsonify({'message': 'User ID is missing'}), 400
    
    if event_id is None:
        return jsonify({'message': 'Event ID is missing'}), 400
    
    if rating is None:
        return jsonify({'message': 'Rating is missing'}), 400

    # Validate User id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
    except psycopg2.Error as e:
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        cursor.close()

    if user is None:
        return jsonify({'message': 'User ID is not in the database'}), 401
    
    # Validate event id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM events WHERE id = %s', (event_id,))
        event = cursor.fetchone()
    except psycopg2.Error as e:
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        cursor.close()

    if event is None:
        return jsonify({'message': 'Event ID is not in the database'}), 401
    
    # Prevent users from rating the same event twice
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM ratings WHERE author_id = %s AND event_id = %s', (user_id, event_id))
        duplicate_ratings = cursor.fetchone()
    except psycopg2.Error as e:
        return jsonify({'message': 'Error while trying to select from ratings table.'}), 500
    finally:
        cursor.close()

    if duplicate_ratings is not None:
        return jsonify({'message': 'User has already rated this event'}), 401

    # Insert the rating into the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('INSERT INTO ratings (author_id, event_id, rating) VALUES (%s, %s, %s)', (user_id, event_id, rating))
        db_connection.commit()
    except Exception as e:
        return jsonify({'message': 'Error while trying to insert into ratings table.'}), 500
    finally:
        cursor.close()

    return jsonify({'message': 'Rating added successfully'}), 200