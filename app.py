from flask import Flask, request, make_response, g
from flask_cors import CORS
import login
import update_university
import add_user
import add_event, get_events, get_pending_public_events, approve_pending_public_event, deny_pending_public_event
import add_comment, update_comment, get_comments, delete_comment
import add_rating, get_user_rating, update_rating
import add_rso, get_managed_rsos, get_university_rsos
from database import db_pool

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://lobster-app-g8oyg.ondigitalocean.app", "http://66.158.232.124", "http://159.203.80.189", "http://localhost:3000", "https://somethingorother.xyz"]}}, supports_credentials=True)


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        # Put the connection back in the pool
        db_pool.putconn(db)

# Summary: This route is used to login a user and returns user info.
# Method: POST
# Input: email, password
# Output: user_id, first_name, last_name, role, email, university_id
@app.route('/login', methods=['POST'])
def login_route():
	data = request.get_json()
	result = login.login_handler(data)
	return result

# Summary: This route is used to update a university in the database.
# Method: POST
# Input: user_id, university_id, new_name, new_location, new_description
# Output: updates university in database
@app.route('/update_university', methods=['POST'])
def update_university_route():
	data = request.get_json()
	result = update_university.update_university_handler(data)
	return result

# Summary: This route is used to create a new user.
# Method: POST
# Input: email, password, firstName, lastName, role
# Output: adds user to database
@app.route('/create', methods=['POST'])
def create_route():
	data = request.get_json()
	result = add_user.signup_handler(data)
	return result

# Summary: This route is used to get all RSOs for a university.
# Method: POST
# Input: university_id
# Output: returns all RSOs for this university as a JSON object
@app.route('/get_university_rsos', methods=['POST'])
def get_university_rsos_route():
	data = request.get_json()
	result = get_university_rsos.get_university_rsos_handler(data)
	return result

# Summary: This route is used to get all RSOs managed by a user.
# Method: POST
# Input: user_id
# Output: returns all RSOs managed by this user as a JSON object
@app.route('/get_managed_rsos', methods=['POST'])
def get_managed_rsos_route():
	data = request.get_json()
	result = get_managed_rsos.get_managed_rsos_handler(data)
	return result

# Summary: This route is used to add an RSO to the database.
# Method: POST
# Input: user1_email, user2_email, user3_email, user4_email, user5_email, admin_email, name, university_id
# Output: adds RSO to database
@app.route('/add_rso', methods=['POST'])
def add_rso_route():
	data = request.get_json()
	result = add_rso.add_rso_handler(data)
	return result

# Summary: This route is used to add an event to the database.
# Method: POST
# Input: user_id, user_email, rso, name, category, time, description, location, phone, contact_email
# Output: adds event to database
@app.route('/add_event', methods=['POST'])
def add_event_route():
	data = request.get_json()
	result = add_event.add_event_handler(data)
	return result

# Summary: This route is used to get events from the database.
# Method: POST
# Input: user_id, university_id
# Output: returns all viewable events for this user as a JSON object
@app.route('/get_events', methods=['POST'])
def get_events_route():
	data = request.get_json()
	result = get_events.get_events_handler(data)
	return result

# Summary: This route is used to get pending public events from the database.
# Method: POST
# Input: user_id, university_id
# Output: returns all pending public events for this user as a JSON object
@app.route('/get_pending_public_events', methods=['POST'])
def get_pending_public_events_route():
	data = request.get_json()
	result = get_pending_public_events.get_pending_public_events_handler(data)
	return result

# Summary: This route is used to approve a pending public event in the database.
# Method: POST
# Input: user_id, university_id, event_id
# Output: approves pending public event in database
@app.route('/approve_pending_public_event', methods=['POST'])
def approve_pending_public_event_route():
	data = request.get_json()
	result = approve_pending_public_event.approve_pending_public_event_handler(data)
	return result

# Summary: This route is used to deny a pending public event in the database.
# Method: POST
# Input: user_id, university_id, event_id
# Output: denies pending public event in database and removes it from the pending events table
@app.route('/deny_pending_public_event', methods=['POST'])
def deny_pending_public_event_route():
	data = request.get_json()
	result = deny_pending_public_event.deny_pending_public_event_handler(data)
	return result

# Summary: This route is used to get comments for an event from the database.
# Method: GET
# Input: event_id included in URL as ?event_id=<event_id>
# Output: returns all comments for this event as a JSON object
@app.route('/get_comments', methods=['GET'])
def get_comments_route():
	result = get_comments.get_comments_handler()
	return result

# Summary: This route is used to add a comment to an event in the database.
# Method: POST
# Input: user_id, event_id, comment
# Output: adds comment to database
@app.route('/add_comment', methods=['POST'])
def add_comment_route():
	data = request.get_json()
	result = add_comment.add_comment_handler(data)
	return result

# Summary: This route is used to update a comment in the database.
# Method: POST
# Input: user_id, comment_id, new_comment
# Output: updates comment in database with new edit timestamp
@app.route('/update_comment', methods=['POST'])
def update_comment_route():
	data = request.get_json()
	result = update_comment.update_comment_handler(data)
	return result

@app.route('/delete_comment', methods=['POST'])
def delete_comment_route():
	data = request.get_json()
	result = delete_comment.delete_comment_handler(data)
	return result

# Summary: This route is used to get a user's rating for an event from the database.
# Method: POST
# Input: user_id, event_id
# Output: returns user's rating for this event as a JSON object
@app.route('/get_user_rating', methods=['POST'])
def get_user_rating_route():
	data = request.get_json()
	result = get_user_rating.get_user_rating_handler(data)
	return result

# Summary: This route is used to add a rating to an event in the database.
# Method: POST
# Input: user_id, event_id, rating
# Output: adds rating to database for this event
@app.route('/add_rating', methods=['POST'])
def add_rating_route():
	data = request.get_json()
	result = add_rating.add_rating_handler(data)
	return result

# Summary: This route is used to update a rating in the database.
# Method: POST
# Input: rating_id, new_rating
# Output: updates rating in database with new rating
@app.route('/update_rating', methods=['POST'])
def update_rating_route():
	data = request.get_json()
	result = update_rating.update_rating_handler(data)
	return result

@app.errorhandler(500)
def handle_500(e):
	response = make_response(str(e), 500)
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)


