import psycopg2.extras
from flask import jsonify
from database import get_db

def update_comment_handler(data):
    # Get the input from the request
    user_id = data['user_id']
    comment_id = data['comment_id']
    new_comment = data['new_comment']

    print('Received update comment request:', data)

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if user_id is None or user_id == '':
        return jsonify({'message': 'User ID is missing'}), 400
    
    if comment_id is None or comment_id == '':
        return jsonify({'message': 'Comment ID is missing'}), 400
    
    if new_comment is None or new_comment == '':
        return jsonify({'message': 'New comment is missing'}), 400
    
    # Validate comment id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM comments WHERE id = %s', (comment_id,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from comments table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is None:
        return jsonify({'message': 'Comment ID is not in the database'}), 401
    
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
    
    # Validate that the user is the author of the comment
    if result['author_id'] != user_id:
        return jsonify({'message': 'User is not the author of the comment'}), 401
    
    # Update the comment in the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('UPDATE comments SET comment = %s, edit_time = NOW() WHERE id = %s', (new_comment, comment_id))
        db_connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to update the comment.'}), 500
    finally:
        if cursor is not None:
            cursor.close()
        
    return jsonify({'message': 'Comment updated successfully'}), 200