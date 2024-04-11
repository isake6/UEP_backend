from flask import g, jsonify
from psycopg2 import pool
import psycopg2.extras
from setup_local_db import mypassword

# Create a connection pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='localhost',
    port='5432',
    user='postgres',
    password=mypassword,
    database='uep_db'
)

def get_db():
    if 'db' not in g or g.db.closed:
        try:
            # Get a connection from the pool
            g.db = db_pool.getconn()
        except psycopg2.pool.PoolError:
            return jsonify({'message': 'Error getting connection from the pool'}), 500

    return g.db