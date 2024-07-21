from typing import Any, Callable, Dict, Optional, Tuple, List, Union
from consts import *
import aiomysql
import os
from dotenv import load_dotenv

from utilities.logger_config import log_execution_time, logger

load_dotenv('.env')

@log_execution_time
async def connect_to_db(user_name: str, host: str, passwd: str) -> aiomysql.pool.Pool:
    """
    Establish a connection to the database and return a connection pool.

    This function retrieves the database connection credentials from the environment variables
    and creates a connection pool using aiomysql.

    Args:
        user_name (str): The environment variable key for the database username.
        host (str): The environment variable key for the database host.
        passwd (str): The environment variable key for the database password.

    Returns:
        aiomysql.pool.Pool: A connection pool for interacting with the database.
    """
    user_name = os.getenv(user_name)
    host = os.getenv(host)
    passwd = os.getenv(passwd)
    
    db_pool = await aiomysql.create_pool(
        user=user_name,
        host=host,
        password=passwd
    )
    return db_pool

async def fetch_one_query(db_pool: aiomysql.pool.Pool, query: str, args: Any=None):
    """Execute a query and fetch one result row.

    Args:
        pool (aiomysql.pool.Pool): The connection pool.
        query (str): The SQL query to execute.
        args (tuple, optional): Query arguments. Defaults to None.

    Returns:
        dict or None: The fetched result row as a dictionary, or None if no row was found or an error occurred.
    """
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                row_data = await cur.fetchone()

                if row_data:
                    column_names = [desc[0] for desc in cur.description]
                    row_dict = dict(zip(column_names, row_data))
                    
                    return row_dict
                
                else:
                    return None
                
    except aiomysql.Error as e:
        logger.error('MySQL Error: {e}')
        return None
    except Exception as e:
        logger.error('Unexpected Error: {e}')
        return None
    
    finally:
        await db_pool._wakeup()

async def fetch_all_query(db_pool: aiomysql.pool.Pool, query: str, args: Any=None):
    """Execute a query and fetch all result rows.

    Args:
        pool (aiomysql.pool.Pool): The connection pool.
        query (str): The SQL query to execute.
        args (tuple, optional): Query arguments. Defaults to None.

    Returns:
        list or None: A list of dictionaries representing the fetched rows, or None if an error occurred.
    """
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                rows = await cur.fetchall()
                column_names = [desc[0] for desc in cur.description]

                # result_dict = {col: [row[i] for row in rows] for i, col in enumerate(column_names)}
                # return dict(result_dict)
                result_list = [dict(zip(column_names, row)) for row in rows]
                
        return result_list
            
    except aiomysql.Error as e:
        logger.error('MySQL Error: {e}')
        return None
    except Exception as e:
        logger.error('Unexpected Error: {e}')
        return None
    
    finally:
        await db_pool._wakeup()

@log_execution_time
async def check_in_all_dbs(func: Callable[..., Tuple[Any, Any]], db_type: Optional[str] = GENERAL, *args: Any, **kwargs: Any) -> Dict[str,str]:
    """
    Check all databases for the requested data using the specified function.

    This function iterates over all regions, connects to the database in each region, and calls the provided function
    to fetch the data. If data is found, the connection is closed and the data along with the region is returned.

    Args:
        func (Callable[..., Tuple[Any, Any]]): The function to call for fetching the data.
        db_type (Optional[str], optional): The type of database to connect to. Defaults to 'GENERAL'.
        *args: Additional arguments to pass to the function.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Dict[str, str]: A dictionary containing the fetched data and the region, or None if no data is found.
    """
    for region in REGIONS:
        logger.debug(f'checking in {region}')
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_{db_type}_{region}', passwd=f'PASSWD_{db_type}_{region}')

        data = await func(db_pool=db_pool,*args, **kwargs)
        
        if data:
            db_pool.close()
            await db_pool.wait_closed()
            data['region'] = region
            return data
        
        db_pool.close()
        await db_pool.wait_closed()
        logger.debug(f'could not find in {region}')

    return None

@log_execution_time
async def fetching_account_tenant_id_by_email(db_pool: aiomysql.pool.Pool, email: str) -> Dict[str,str]:
    """
    Fetch the account tenant ID by email from the database.

    This function constructs and executes a query to fetch the account tenant ID associated with the given email.
    If a result is found, it is returned as a dictionary.

    Args:
        db_pool (aiomysql.pool.Pool): The connection pool.
        email (str): The email to search for.

    Returns:
        Dict[str, str]: A dictionary containing the account tenant ID, or None if no result is found.
    """
    query = GET_ACCOUNT_TENANT_ID_BY_EMAIL_AND_FE_PROD_ID.format(f"'{email}'", f"'{os.getenv('PROD_VENDOR_ID')}'")

    account_tenant_response = await fetch_one_query(db_pool=db_pool, query=query)
    
    if account_tenant_response:
        return account_tenant_response
    
    return None

@log_execution_time
async def fetching_account_id_by_account_tenant_id(db_pool: aiomysql.pool.Pool, account_tenant_id: str) -> Dict[str,str]:
    """
    Fetch the account ID by account tenant ID from the database.

    This function constructs and executes a query to fetch the account ID associated with the given account tenant ID.
    If a result is found, it is returned as a dictionary.

    Args:
        db_pool (aiomysql.pool.Pool): The connection pool.
        account_tenant_id (str): The account tenant ID to search for.

    Returns:
        Dict[str, str]: A dictionary containing the account ID, or None if no result is found.
    """
    query = GET_ACCOUNT_ID_BY_ACCOUNT_TENANT_ID.format(f"'{account_tenant_id}'")

    account_tenant_response = await fetch_one_query(db_pool=db_pool, query=query)

    if account_tenant_response:
        return account_tenant_response
    
    return None

@log_execution_time
async def fetching_vendor_id_by_account_id(db_pool: aiomysql.pool.Pool, account_id: str) -> Dict[str,str]:
    """
    Fetch the vendor ID by account ID from the database.

    This function constructs and executes a query to fetch the vendor ID associated with the given account ID.
    If a result is found, it is returned as a dictionary.

    Args:
        db_pool (aiomysql.pool.Pool): The connection pool.
        account_id (str): The account ID to search for.

    Returns:
        Dict[str, str]: A dictionary containing the vendor ID, or None if no result is found.
    """
    query = GET_VENDORS_IDS_BY_ACCOUNT_ID_QUERY.format(f"'{account_id}'")

    account_response = await fetch_one_query(db_pool=db_pool, query=query)

    if account_response:
        return account_response
    
    return None

@log_execution_time
async def fetching_tenant_dict_from_db(db_pool: aiomysql.pool.Pool, client_id: str) -> Dict[str,str]:
    """
    Fetch the tenant dictionary from the database using the client ID.

    This function constructs and executes queries to fetch the vendor, account, and tenant details associated
    with the given client ID. If all details are found, they are combined into a single dictionary and returned.

    Args:
        db_pool (aiomysql.pool.Pool): The connection pool.
        client_id (str): The client ID to search for.

    Returns:
        Dict[str, str]: A dictionary containing the tenant details, or an empty dictionary if no results are found.
    """
    vendor_query_result = await fetch_one_query(db_pool=db_pool, query=GET_VENDOR_BY_ID_QUERY.format(f"'{client_id}'"))

    if not vendor_query_result:
        return {}
    
    account_query_result = await fetch_one_query(db_pool=db_pool, query=GET_ACCOUNT_DETAILS_BY_ID.format(f"'{vendor_query_result.get('accountId')}'"))
        
    if not account_query_result:
        return {}           

    tenant_query_result = await fetch_one_query(db_pool=db_pool, query=GET_TENANT_CONFIGURATIONS_QUERY.format(f"'{account_query_result.get('accountTenantId')}'"))
   
    if tenant_query_result:    
        return { 'id': tenant_query_result.get('id'), 'tenant_id': tenant_query_result.get('tenantId')}
    
    return {}


async def fetching_env_name_by_vendor_id(db_pool: aiomysql.pool.Pool, vendor_id: str) -> Dict[str,str]:
    query = GET_ACCOUNT_TENANT_ID_BY_EMAIL_AND_FE_PROD_ID.format(f"'{vendor_id}'")

    data = await fetch_one_query(db_pool=db_pool, query=query)
    
    if data:
        return data
    
    return None