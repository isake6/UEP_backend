import psycopg2.extras
from flask import jsonify
from database import get_db

def get_university_details_handler(data):
    # Get the input from the request
    try:
        university_id = data['university_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received get university details request:', data)

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Get the university details
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM universities WHERE id = %s", (university_id,))
        university = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from universities table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if university is None:
        return jsonify({'message': 'University not found'}), 404
    
    return jsonify(university), 200

    