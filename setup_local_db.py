import subprocess
import psycopg2
import time

# Your password string
mypassword = "dd1805852fa043af98823e6e4479b6c0"

# Start the PostgreSQL server
subprocess.run(["C:\\Program Files\\PostgreSQL\\16\\bin\\pg_ctl", "-D", "C:\\Program Files\\PostgreSQL\\16\\data", "start"])

# Wait for the server to start up
print("Starting server...")
time.sleep(5)

# Connect to the server using the postgres database
conn = psycopg2.connect(database="postgres", user="postgres", password=mypassword, host="localhost", port="5432")

# Set autocommit mode
conn.autocommit = True

# Create a cursor
cur = conn.cursor()

# Drop the UEP_DB database if it exists
cur.execute("DROP DATABASE IF EXISTS UEP_DB")
print("Creating database...")
time.sleep(3)

# Create the UEP_DB database
cur.execute("CREATE DATABASE UEP_DB")

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()
time.sleep(3)

# Connect to the new database
conn = psycopg2.connect(database="uep_db", user="postgres", password=mypassword, host="localhost", port="5432")

# Create a cursor
cur = conn.cursor()

# Drop the 'public' schema
cur.execute("DROP SCHEMA public CASCADE")

# Commit the changes
conn.commit()
print("Creating schema...")
time.sleep(3)

# Open the schema file and read its contents
with open('schema.sql', 'r', encoding='utf-8') as f:
    schema = f.read()

# Execute the SQL commands
cur.execute(schema)

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()