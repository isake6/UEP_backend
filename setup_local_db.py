import subprocess
import psycopg2
import time

# Start the PostgreSQL server
subprocess.run(["C:\\Program Files\\PostgreSQL\\16\\bin\\pg_ctl", "-D", "C:\\Program Files\\PostgreSQL\\16\\data", "start"])

# Wait for the server to start up
time.sleep(5)

# Connect to the server using the postgres database
conn = psycopg2.connect(database="postgres", user="postgres", password="dd1805852fa043af98823e6e4479b6c0", host="localhost", port="5432")

# Create a cursor
cur = conn.cursor()

# Create a new database
cur.execute("CREATE DATABASE UEP_DB")

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()

# Connect to the new database
conn = psycopg2.connect(database="UEP_DB", user="postgres", password="password", host="localhost", port="5432")

# Open the schema file and read its contents
with open('schema.sql', 'r') as f:
    schema = f.read()

# Create a cursor
cur = conn.cursor()

# Execute the SQL commands
cur.execute(schema)

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()