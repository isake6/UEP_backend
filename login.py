import boto3
import psycopg2
from json import dumps, loads
import os

# Database connection
db_connection = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

def lambda_handler(event, context):
    event = event.get('body')
    event = loads(event)

    # Get the username and password from the request
    username = event['username']
    password = event['password']
    
    # Check if the user exists in the database
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    # If user does not exist, return an error
    if user is None:
        return {
            'statusCode': 400,
            'body': dumps({'message': 'User does not exist'})
        }
    
    # Check if the password is correct
    if user[2] != password:
        return {
            'statusCode': 400,
            'body': dumps({'message': 'Incorrect password'})
        }
    
    # If the login is successful, return the user's information
    return {
        'statusCode': 200,
        'body': dumps({'username': user[0], 'email': user[1]})
    }
