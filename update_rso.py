import psycopg2.extras
from flask import jsonify
from database import get_db

def update_rso_handler(data):
    # Get the input from the request
    try:
        user_id = data['user_id']
        rso_id = data['rso_id']
        name = data['name']
        admin_email = data['admin_email']
        description = data['description']
        university_id = data['university_id']
    except KeyError as e:
        print(f"Error: Missing field {e} in request data")
        return jsonify({'message': f'Missing field {e} in request data'}), 400

    print('Received update RSO request:', data)

    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    # Input validation for empty fields
    if user_id is None or user_id == '':
        return jsonify({'message': 'User ID is missing'}), 400
    
    if rso_id is None or rso_id == '':
        return jsonify({'message': 'RSO ID is missing'}), 400
    
    if name is None or name == '':
        return jsonify({'message': 'RSO name is missing'}), 400
    
    if admin_email is None or admin_email == '':
        return jsonify({'message': 'RSO admin is missing'}), 400
    
    if description is None or description == '':
        return jsonify({'message': 'RSO description is missing'}), 400
    
    if university_id is None or university_id == '':
        return jsonify({'message': 'University ID is missing'}), 400
    
    # Check that the user exists
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result is None:
        return jsonify({'message': 'User ID is not in the database'}), 401
    
    # Check that the RSO exists
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM rso WHERE id = %s', (rso_id,))
        result1 = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rsos table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result1 is None:
        return jsonify({'message': 'RSO ID is not in the database'}), 401
    
    # Check that the RSO belongs to the university
    if result1['university'] != university_id:
        return jsonify({'message': 'RSO does not belong to this university'}), 401
    
    # Check that the user is the admin of the RSO
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM rso WHERE id = %s AND admin = %s', (rso_id, user_id))
        result2 = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result2 is None:
        return jsonify({'message': 'User is not the admin of this RSO'}), 401
    
    # Check that the new name does not overlap with another RSO
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM rso WHERE name = %s AND university = %s AND id != %s', (name, university_id, rso_id))
        result3 = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result3 is not None:
        return jsonify({'message': 'RSO name already exists in this university'}), 401
    
    # Convert the admin email to user ID
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT id FROM users WHERE email = %s', (admin_email,))
        admin = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if admin is None:
        return jsonify({'message': 'Admin email is not in the database'}), 401
    
    admin = admin['id']
    
    # Check that the new admin is another member of the RSO
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM rso_members WHERE id = %s AND rso_id = %s', (admin, rso_id))
        result4 = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso_members table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result4 is None:
        return jsonify({'message': 'New admin is not a member of this RSO'}), 401
    
    # If the new admin has student role, update role to admin
    try:
        cursor = db_connection.cursor()
        cursor.execute("UPDATE users SET role = %s WHERE id = %s and role = 'student'", ('admin', admin))
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to update users table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    # Check if the old admin is an admin of any other RSO
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM rso WHERE admin = %s and id != %s', (user_id, rso_id))
        result5 = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from rso table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    if result5 is None:
        # If the old admin is not an admin of any other RSO, update role to student
        try:
            cursor = db_connection.cursor()
            cursor.execute("UPDATE users SET role = %s WHERE id = %s and role = 'admin'", ('student', user_id))
        except psycopg2.Error as e:
            print(f"Error: {e}")
            return jsonify({'message': 'Error while trying to update users table.'}), 500
        finally:
            if cursor is not None:
                cursor.close()
    
    # Update the RSO
    try:
        cursor = db_connection.cursor()
        cursor.execute('UPDATE rso SET name = %s, admin = %s, description = %s WHERE id = %s', (name, admin, description, rso_id))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to update rso table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    # Return results
    return jsonify({'message': 'RSO updated successfully'}), 200