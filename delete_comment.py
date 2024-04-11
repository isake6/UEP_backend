import psycopg2.extras
from flask import jsonify
from database import get_db

def delete_comment_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        comment_id = data['comment_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received delete comment request:', data)

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
    
    # Validate that author is the author of the comment
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM comments WHERE id = %s AND author_id = %s', (comment_id, user_id))
        comment = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from comments table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if comment is None:
        return jsonify({'message': 'User is not the author of this comment'}), 401
    
    # Delete comment
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('DELETE FROM comments WHERE id = %s', (comment_id,))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to delete from comments table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'message': 'Comment deleted successfully'}), 200