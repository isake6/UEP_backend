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

def add_comment_handler(data):
    # Get the input from the request
    author_id = data['author_id']
    event_id = data['event_id']
    comment = data['comment']

    print('Received add comment request:', data)

    # Input validation for empty fields
    
    if author_id is None:
        return jsonify({'message': 'Author ID is missing'}), 400
    
    if event_id is None:
        return jsonify({'message': 'Event ID is missing'}), 400
    
    if comment is None:
        return jsonify({'message': 'Comment is missing'}), 400

    # Validate author id
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (author_id,))
    user = cursor.fetchone()
    cursor.close()

    if user is None:
        return jsonify({'message': 'Author ID is not in the database'}), 401
    
    # Validate event id
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM events WHERE id = %s', (event_id,))
    event = cursor.fetchone()
    cursor.close()

    if event is None:
        return jsonify({'message': 'Event ID is not in the database'}), 401

    # Insert the comment into the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('INSERT INTO comments (author_id, event_id, comment, created_time) VALUES (%s, %s, %s, NOW())', (author_id, event_id, comment))
        db_connection.commit()
        cursor.close()
    except Exception as e:
        return jsonify({'message': 'Error while trying to insert into comments table.'}), 500

    return jsonify({'message': 'Comment added successfully'}), 200