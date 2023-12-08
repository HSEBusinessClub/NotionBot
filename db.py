import os
import psycopg2


CREATE_USER_TABLE_QUERY = """
CREATE TABLE IF NOT EXIST users(
id INT PRIMARY KEY,
email VARCHAR
)"""

CREATE_TASKS_TABLE_QUERY = """
CREATE TABLE IN NOT EXISTS tasks(
id INT PRIMARY KEY,
owner_id = INT
)
"""


def init_db() -> tuple[psycopg2.connect, psycopg2.cursor]:
    user_name = os.environ["POSTGRES_USER"]
    db_password = os.environ["POSTGRES_PASSWORD"]
    db_name = os.environ["POSTGRES_DB_NAME"]
    connection = psycopg2.connect(host='localhost', user=user_name,
                                  password=db_password, database=db_name)
    cursor = connection.cursor()

    cursor.execute(CREATE_USER_TABLE_QUERY)
    cursor.execute(CREATE_TASKS_TABLE_QUERY)
    connection.commit()
    return connection, cursor
