from typing import Any, Callable, Dict, Tuple, List, Union
import mysql.connector
from .consts import *
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

def fetch_one_query(cursor: mysql.connector.cursor.MySQLCursor, query: str) -> Tuple:
    """Execute a query and fetch one result row.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): The cursor object.
        query (str): The SQL query to execute.

    Returns:
        tuple: The fetched result row.
    """
    try:
        cursor.execute(query)
        row_data = cursor.fetchone()
        
        if row_data:
            column_names = [desc[0] for desc in cursor.description]
            row_dict = dict(zip(column_names, row_data))
            
            return row_dict
    
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

def check_in_all_dbs(func: Callable[..., Tuple[Any, Any]], *args: Any, **kwargs: Any) -> Tuple[Dict,str]:
    for region in REGIONS:
        db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()     
        data = func(cursor=cursor,*args, **kwargs)
        
        if data:
            db.close()
            return data, region
        
        else:
            db.close()
            
    return None

def find_user_role(cursor: mysql.connector.cursor_cext.CMySQLCursor, user_id: str, tenant_id: str) -> Union[str, List[str]]:
    # get user's tenant id with user_id and tenant_id from 'users_tenants' table
    user_tenant_id = fetch_one_query(cursor=cursor, query=GET_USER_TENANT_BY_USER_ID_AND_TEN_ID_QUERY.format(f"'{user_id}'", f"'{tenant_id}'"))
    if user_tenant_id:
        paresed_user = parse_response(cursor=cursor, result_to_parse=user_tenant_id)

    if paresed_user:
        # get role id with user_tenant_id from 'users_tenants_roles'
        user_tenant_role = fetch_all_query(cursor=cursor, query=GET_ROLES_BY_USER_TEN_ID_QUERY.format(f"'{paresed_user.get('id')}'"))

    if user_tenant_role:
        paresed_user_tenant = parse_response(cursor=cursor, result_to_parse=user_tenant_role)

    if paresed_user_tenant:
        roles_list = []
        # get role name with user_tenant_id from 'users_tenants_roles'
        for role in paresed_user_tenant.get('roleId'):
            user_tenants_roles = fetch_one_query(cursor=cursor, query=GET_ROLE_NAME_BY_ID_QUERY.format(f"'{role}'"))
            
            if user_tenants_roles:
                paresed_user_tenants_roles = parse_response(cursor=cursor, result_to_parse=user_tenants_roles)
                roles_list.append(paresed_user_tenants_roles.get('key'))
        return roles_list
    
    return ''

def fetching_tenant_dict_from_db(cursor: mysql.connector.cursor_cext.CMySQLCursor, client_id: str) -> Dict[str,str]:
    vendor_query_result = fetch_one_query(cursor=cursor, query=GET_VENDOR_BY_ID_QUERY.format(f"'{client_id}'"))

    if not vendor_query_result:
        return {}
    
    account_query_result = fetch_one_query(cursor=cursor, query=GET_TENANT_BY_ID_QUERY.format(f"'{vendor_query_result.get('accountId')}'"))
        
    if not account_query_result:
        return {}

    tenant_query_result = fetch_one_query(cursor=cursor, query=GET_TENANT_CONFIGURATIONS_QUERY.format(f"'{account_query_result.get('accountTenantId')}'"))
   
    if tenant_query_result:    
        return { "id": tenant_query_result.get("id"), "tenant_id": tenant_query_result.get("tenantId")}
    
    return {}
