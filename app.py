from flask import Flask, request
from flask_cors import CORS
import login
import json

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login_route():
	data = request.get_json()
	event = {
		'body': json.dumps(data)
	}
	return login.lambda_handler(event, None)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=3000)


