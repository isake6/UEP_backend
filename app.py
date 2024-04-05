from flask import Flask, request, make_response
from flask_cors import CORS
import login
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://lobster-app-g8oyg.ondigitalocean.app", "http://159.203.80.189", "http://localhost:3000", "https://somethingorother.xyz"]}}, supports_credentials=True)

@app.route('/login', methods=['POST'])
def login_route():
	data = request.get_json()
	result = login.login_handler(data)
	return result

@app.errorhandler(500)
def handle_500(e):
	response = make_response(str(e), 500)
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)


