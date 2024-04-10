import psycopg2.extras
from flask import jsonify
from database import get_db

def update_rating_handler(data):
    # Get the input from the request
    try:
        rating_id = data['rating_id']
        new_rating = data['new_rating']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received update rating request:', data)

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if rating_id is None or rating_id == '':
        return jsonify({'message': 'Rating ID is missing'}), 400
    
    if new_rating is None or new_rating == '':
        return jsonify({'message': 'New rating is missing'}), 400
    
    # Validate rating id
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM ratings WHERE id = %s', (rating_id,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from ratings table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is None:
        return jsonify({'message': 'Rating ID is not in the database'}), 401
    
    # Update rating
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('UPDATE ratings SET rating = %s WHERE id = %s', (new_rating, rating_id))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to update rating.'}), 500
    finally:
        if cursor is not None:
            cursor.close()
    
    return jsonify({'message': 'Rating updated successfully'}), 200