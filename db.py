import os
import psycopg2
from psycopg2.extensions import cursor, connection


CREATE_USER_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS users(
id SERIAL PRIMARY KEY,
email VARCHAR,
chat_id INT
)"""

CREATE_TASKS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS tasks(
id SERIAL PRIMARY KEY,
owner_id INT
)
"""


def ADD_USER(email: str, chat_id: int) -> str:
    return f"""
    INSERT INTO users (email, chat_id)
    VALUES ('{email}', {chat_id});
"""


def init_db() -> tuple[connection, cursor]:
    user_name = os.environ["POSTGRES_USER"]
    db_password = os.environ["POSTGRES_PASSWORD"]
    db_name = os.environ["POSTGRES_DB_NAME"]

    connection = psycopg2.connect(host='postgres', user=user_name,
                                  password=db_password, database=db_name)
    cursor = connection.cursor()

    cursor.execute(CREATE_USER_TABLE_QUERY)
    cursor.execute(CREATE_TASKS_TABLE_QUERY)
    connection.commit()
    return connection, cursor
