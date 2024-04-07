from flask import Flask, request, make_response, jsonify, g
from flask_cors import CORS
from psycopg2 import pool
import psycopg2.extras
import login, add_user, add_event, add_comment
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://lobster-app-g8oyg.ondigitalocean.app", "http://159.203.80.189", "http://localhost:3000", "https://somethingorother.xyz"]}}, supports_credentials=True)

# Create a connection pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

def get_db():
	if 'db' not in g or g.db.closed:
		try:
			# Get a connection from the pool
			g.db = db_pool.getconn()
		except psycopg2.pool.PoolError:
			return jsonify({'message': 'Error getting connection from the pool'}), 500

	return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        # Put the connection back in the pool
        db_pool.putconn(db)

@app.route('/login', methods=['POST'])
def login_route():
	data = request.get_json()
	result = login.login_handler(data)
	return result

@app.route('/create', methods=['POST'])
def create_route():
	data = request.get_json()
	result = add_user.signup_handler(data)
	return result

@app.route('/add_event', methods=['POST'])
def add_event_route():
	data = request.get_json()
	result = add_event.add_event_handler(data)
	return result

@app.route('/add_comment', methods=['POST'])
def add_comment_route():
	data = request.get_json()
	result = add_comment.add_comment_handler(data)
	return result

@app.errorhandler(500)
def handle_500(e):
	response = make_response(str(e), 500)
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)


