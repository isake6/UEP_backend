import psycopg2.extras
from flask import jsonify
from database import get_db

def add_rso_handler(data):
    # Get the input from the request
    try:
        user1_email = data['user1_email']
        user2_email = data['user2_email']
        user3_email = data['user3_email']
        user4_email = data['user4_email']
        user5_email = data['user5_email']
        admin_email = data['admin_email']
        name = data['name']
        university_id = data['university_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400
    
    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection

    cursor = None

    print('Received RSO signup request:', data)

    # Input validation
    if user1_email is None or user1_email == '':
        return jsonify({'message': 'User 1 email is missing'}), 400
    
    if user2_email is None or user2_email == '':
        return jsonify({'message': 'User 2 email is missing'}), 400
    
    if user3_email is None or user3_email == '':
        return jsonify({'message': 'User 3 email is missing'}), 400
    
    if user4_email is None or user4_email == '':
        return jsonify({'message': 'User 4 email is missing'}), 400
    
    if user5_email is None or user5_email == '':
        return jsonify({'message': 'User 5 email is missing'}), 400
    
    if admin_email is None or admin_email == '':
        return jsonify({'message': 'Admin email is missing'}), 400
    
    if admin_email not in [user1_email, user2_email, user3_email, user4_email, user5_email]:
        return jsonify({'message': 'Admin email does not match any email in the list of applicants'}), 400

    if name is None or name == '':
        return jsonify({'message': 'RSO name is missing'}), 400
    
    if university_id is None or university_id == '':
        return jsonify({'message': 'University ID is missing'}), 400
    
    # Check if the university exists in the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM universities WHERE id = %s", (university_id,))
        results = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from universities table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if results is None:
        return jsonify({'message': 'University ID is not in the database'}), 401
    
    # Check if the users exist in the database and are from the same university
    emails_to_check = [user1_email, user2_email, user3_email, user4_email, user5_email]
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        placeholders = ', '.join(['%s'] * len(emails_to_check))
        query = f"SELECT DISTINCT id FROM users WHERE email IN ({placeholders}) AND university_id = %s"
        cursor.execute(query, (*emails_to_check, university_id))
        results = cursor.fetchall()
        if len(results) == len(emails_to_check):
            print("All users exist and are from the same university.")
            cursor.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
            admin_id = cursor.fetchone()[0]
        else:
            print("Not all users exist or are from different universities.")
            return jsonify({'message': 'Not all users exist or are from different universities'}), 401
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to validate users.', 'query': query}), 500
    finally:
        if cursor is not None:
            cursor.close()

    user1_id = results[0]['id']
    user2_id = results[1]['id']
    user3_id = results[2]['id']
    user4_id = results[3]['id']
    user5_id = results[4]['id']
    
    # Check if the RSO already exists
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM rso WHERE name = %s AND university = %s", (name, university_id))
        results = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rsos table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if results is not None:
        return jsonify({'message': 'RSO already exists'}), 401
    
    # Add the RSO to the database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("INSERT INTO rso (name, university) VALUES (%s, %s) RETURNING id", (name, university_id))
        results = cursor.fetchone()[0]
        cursor.execute("INSERT INTO rso_members (id, rso_id) VALUES (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s)", (user1_id, results, user2_id, results, user3_id, results, user4_id, results, user5_id, results))
        cursor.execute("UPDATE rso SET admin = %s WHERE id = %s", (admin_id, results))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to insert into rso table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'message': 'RSO added successfully.', 'id':results}), 200