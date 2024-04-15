import psycopg2.extras
from flask import jsonify
from database import get_db

def get_events_for_guest_handler(data):    
    # Database connection
    db_connection = get_db()
    if isinstance(db_connection, tuple):
        # get_db returned an error response
        return db_connection
    
    cursor = None

    print('Received get events for guest request:', data)
    
    # Get events from database
    try:
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM events WHERE category='public'")
        events = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error while trying to select from events table.'}), 500
    finally:
        if cursor is not None:
            cursor.close()

    return jsonify({'events': events}), 200
