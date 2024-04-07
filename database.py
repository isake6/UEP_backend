from flask import g, jsonify
from psycopg2 import pool
import psycopg2.extras
import os

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