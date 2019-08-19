import os
from sqlalchemy.sql import text
from sqlalchemy import create_engine


# def connectToPostgres():
#     url = getUrl()
#     engine = create_engine(url)
#     connection = engine.connect()
#     return connection

_connections = []


def get_connection():
    if _connections:
        return _connections[0]
    else:
        connection = create_engine(get_connect_str()).connect()
        _connections.append(connection)
        return connection


def execute_query(sql):
    connection = get_connection()
    cursor = connection.execute(text(sql).execution_options(autocommit=True))
    return cursor


def get_connect_str():
    url = os.environ['POSTGRES_URL']
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    return "postgresql+psycopg2://{0}:{1}@localhost:5432/postgres".format(user, password)


def insert_sentiment(sentiment, score, id, col1, col2):
    connection = get_connection()
    sql = "UPDATE replies_from_dm_me_your_cats_friends \
            SET {0} = {1}, {2} = '{3}' \
            WHERE id = {4}"\
        .format(col1, score, col2, sentiment, id)
    connection.execute(text(sql).execution_options(autocommit=True))


def insert_clean_text(text, id):
    connection = get_connection()
    if text.find("'"):
        text = text.replace("'", "''")
    sql = "UPDATE replies_from_dm_me_your_cats_friends \
            SET clean_after_python_text = '{0}' WHERE id = {1}".format(text, id)
    print(sql)
    connection.execute(text(sql).execution_options(autocommit=True))


def insert_clsf_sentiment(score, id, col1, col2):
    sentiment = "positive" if score == 1 else "negative"
    connection = get_connection()
    sql = "UPDATE replies_from_dm_me_your_cats_friends \
            SET {0} = '{1}' ," \
           "{2} = {3} \
            WHERE id = {4}" \
        .format(col1, sentiment, col2, score, id)
    connection.execute(text(sql).execution_options(autocommit=True))


def get_ids_text():
    connection = get_connection()
    sql = "SELECT id, original_text FROM replies_from_dm_me_your_cats_friends"
    cursor = connection.execute(text(sql)
                                .execution_options(autocommit=True))
    return cursor










