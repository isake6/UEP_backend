import boto3
import psycopg2.extras
from json import dumps, loads
import os
from flask import Response, jsonify
from database import get_db

def add_comment_handler(data):
    # Get the input from the request
    author_id = data['author_id']
    event_id = data['event_id']
    comment = data['comment']

    print('Received add comment request:', data)

    # Database connection
    db_connection = get_db()

    # Input validation for empty fields
    if author_id is None:
        return jsonify({'message': 'Author ID is missing'}), 400
    
    if event_id is None:
        return jsonify({'message': 'Event ID is missing'}), 400
    
    if comment is None:
        return jsonify({'message': 'Comment is missing'}), 400

    # Validate author id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (author_id,))
        user = cursor.fetchone()
    except psycopg2.Error as e:
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        cursor.close()

    if user is None:
        return jsonify({'message': 'Author ID is not in the database'}), 401
    
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

    # Insert the comment into the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('INSERT INTO comments (author_id, event_id, comment, created_time) VALUES (%s, %s, %s, NOW())', (author_id, event_id, comment))
        db_connection.commit()
    except Exception as e:
        return jsonify({'message': 'Error while trying to insert into comments table.'}), 500
    finally:
        cursor.close()

    return jsonify({'message': 'Comment added successfully'}), 200