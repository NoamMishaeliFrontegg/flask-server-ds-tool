from typing import Dict, Tuple
import mysql.connector
from consts import *
import os
from dotenv import load_dotenv

load_dotenv('.env')

def connect_to_db(user_name: str, host: str, passwd: str) -> mysql.connector.connection_cext.CMySQLConnection:
    user_name = os.getenv(user_name)
    host = os.getenv(host)
    passwd = os.getenv(passwd)
    
    # Connecting from the server
    db = mysql.connector.connect(user = user_name,
                                host = host,
                                passwd = passwd)

    return db

# def fetch_one_query(cursor: mysql.connector.cursor_cext.CMySQLCursor, query: str) -> Tuple: 
#     """_summary_
#     Args:
#         cursor (mysql.connector.cursor_cext.CMySQLCursor): _description_
#         query (str): _description_
#         id (str): _description_

#     Returns:
#         Tuple: _description_
#     """
#     cursor.execute(query)
#     return cursor.fetchone()

def fetch_one_query(cursor: mysql.connector.cursor.MySQLCursor, query: str) -> tuple:
    """Execute a query and fetch one result row.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): The cursor object.
        query (str): The SQL query to execute.

    Returns:
        tuple: The fetched result row.
    """
    try:
        cursor.execute(query)
        return cursor.fetchone()
    except mysql.connector.Error as e:
        # Handle specific MySQL errors here
        print(f"MySQL Error: {e}")
        return None
    except Exception as e:
        # Handle other unexpected errors here
        print(f"Unexpected Error: {e}")
        return None

def fetch_all_query(cursor: mysql.connector.cursor_cext.CMySQLCursor, query: str) -> Tuple: 
    """_summary_
    Args:
        cursor (mysql.connector.cursor_cext.CMySQLCursor): _description_
        query (str): _description_
        id (str): _description_

    Returns:
        Tuple: _description_
    """
    cursor.execute(query)
    return cursor.fetchall()

def parse_response(cursor: mysql.connector.cursor_cext.CMySQLCursor, result_to_parse: Tuple) -> Dict:
    """_summary_

    Args:
        cursor (mysql.connector.cursor_cext.CMySQLCursor): _description_
        result_to_parse (Tuple): _description_

    Returns:
        Dict: _description_
    """
    columns = [desc[0] for desc in cursor.description]
    
    # if result is not None (i.e., there is at least one row returned)
    if result_to_parse and isinstance(result_to_parse, Tuple):
        # get the column names from the cursor description
        # create a dictionary using zip() to pair column names with values
        return dict(zip(columns, result_to_parse))
    
    if result_to_parse and isinstance(result_to_parse, list):
        result = {column: tuple() for column in columns}

        for obj in result_to_parse:
            if isinstance(obj, tuple) and len(obj) == len(columns):
                for i, value in enumerate(obj):
                    result[columns[i]] += (value,)
            else:
                raise ValueError("Invalid object format") 
        return result
    return {}


