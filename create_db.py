import psycopg2
import os


print(os.getenv('WOBOT_DB_HOST'))

conn = psycopg2.connect(
    host=os.getenv('WOBOT_DB_HOST'),
    database=os.getenv('WOBOT_DEFAULT_DB'),
    user=os.getenv('WOBOT_DB_USER'),
    password=os.getenv('WOBOT_DB_PWD'),
    port=os.getenv('WOBOT_DB_PORT')
)

# Create a cursor object to execute SQL queries
cur = conn.cursor()

conn.autocommit = True

# Create a cursor object to execute SQL queries
cur = conn.cursor()

# Create a new database if it doesn't already exist
cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (os.getenv('WOBOT_DB_NAME'),))
db_exists = cur.fetchone()

if not db_exists:
    cur.execute("CREATE DATABASE " + os.getenv('WOBOT_DB_NAME'))
    print("Database created successfully.")
else:
    print("Database already exists.")
    cur.execute("DROP DATABASE " + os.getenv('WOBOT_DB_NAME'))
    cur.execute("CREATE DATABASE " + os.getenv('WOBOT_DB_NAME'))

# Close the cursor and the default database connection
cur.close()
conn.close()

# Establish a connection to the newly created database
conn = psycopg2.connect(
    host=os.getenv('WOBOT_DB_HOST'),
    database=os.getenv('WOBOT_DB_NAME'),
    user=os.getenv('WOBOT_DB_USER'),
    password=os.getenv('WOBOT_DB_PWD'),
    port=os.getenv('WOBOT_DB_PORT')

)
# Create a new cursor
cur = conn.cursor()

# SQL query to create the "user" table
user_table = '''
    CREATE TABLE IF NOT EXISTS "users" (
        id SERIAL PRIMARY KEY,
        user_name VARCHAR(255),
        mail_id VARCHAR(255),
        password VARCHAR(255),
        details JSONB,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
'''

todo_table = '''CREATE TABLE IF NOT EXISTS "todo" (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        title VARCHAR(255),
        my_list CHARACTER(255)[],
        details JSONB,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )'''
# Execute the create table query
cur.execute(user_table)
cur.execute(todo_table)
# Commit the changes to the database
conn.commit()

# Close the cursor and the database connection
cur.close()
conn.close()
