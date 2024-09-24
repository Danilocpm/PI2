import pymysql
import json

timeout = 60

def load_config():
    with open('configdb.json') as f:
        return json.load(f)

def get_connection():
    config = load_config()
    connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=config["db"],
        host=config["host"],
        password=config["password"],
        read_timeout=timeout,
        port=config["port"],
        user=config["user"],
        write_timeout=timeout,
    )
    return connection
