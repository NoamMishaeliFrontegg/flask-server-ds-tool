from typing import Any
from consts import *
import aiomysql
import os
from dotenv import load_dotenv
from typing import Any, Callable, Dict, Optional, Tuple, List

from utilities.logger_config import logger, log_execution_time

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
        password=passwd,
        port=3306
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
async def check_in_all_dbs(func: Callable[..., Tuple[Any, Any]], db_type: Optional[str] = GENERAL, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    This function iterates over all regions, connects to the database in each region, and calls the provided function to fetch the data.
    If data is found, the connection is closed and the data along with the region is returned.

    Args:
        func (Callable[..., Tuple[Any, Any]]): The function to call for fetching the data.
        db_type (Optional[str], optional): The type of database to connect to. Defaults to 'GENERAL'.
        *args: Additional arguments to pass to the function.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Dict[str, Any]: A dictionary containing the fetched data for each region, or an empty dict if no data is found.
    """
    region_data = {}
    for region in REGIONS:
        logger.debug(f'Checking {region} region')
        try:
            db_pool = await connect_to_db(user_name='USER_NAME', host=f'HOST_{db_type}_{region}', passwd=f'PASSWD_{db_type}_{region}')
            returned_data = await func(db_pool=db_pool, *args, **kwargs)
            logger.debug(f'Returned data for {region}: {returned_data}')
        except Exception as e:
            logger.error(f'Error connecting to or querying database for {region}: {str(e)}')
            continue
        finally:
            if 'db_pool' in locals():
                db_pool.close()
                await db_pool.wait_closed()

        if not returned_data:
            logger.debug(f'Could not find data in {region}')
            continue

        # Ensure region_data is a list for the given region
        if region not in region_data:
            region_data[region] = []

        # Append the relevant values to the region list (assuming 'id' is the key)
        if isinstance(returned_data, list):
        # print("\n",returned_data,"\n")
            for item in returned_data:
            
                if 'tenantId' in item:
                    region_data[region].append(item['tenantId'])
                else:
                    logger.warning(f'Unexpected data format for {region}: {item}')
        else:
            logger.warning(f'Unexpected data format for {region}: {returned_data}')

    logger.debug(f'Final region_data: {region_data}')
    return region_data
   
@log_execution_time
async def fetch_data_from_region(func: Callable[..., Tuple[Any, Any]], region: str, db_type: Optional[str] = GENERAL, *args: Any, **kwargs: Any) -> List:
    """
    This function connects to the database in a region, and calls the provided function
    to fetch the data. If data is found, the connection is closed and the data along with the region is returned.

    Args:
        func (Callable[..., Tuple[Any, Any]]): The function to call for fetching the data.
        db_type (Optional[str], optional): The type of database to connect to. Defaults to 'GENERAL'.
        region: str represent the region 
        *args: Additional arguments to pass to the function.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Dict[str, str]: A dictionary containing the fetched data and the region, or None if no data is found.
    """
    region_data = {}
    logger.info(f'connecting to {region} region')
    
    db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_{db_type}_{region}', passwd=f'PASSWD_{db_type}_{region}')
    returned_data = await func(db_pool=db_pool,*args, **kwargs)
    db_pool.close()
    await db_pool.wait_closed()
    
    if not returned_data:   
        logger.debug(f'could not find in {region}')
        return region_data
    
    # Initialize the region key if it doesn't exist
    if region not in region_data:
        # Determine if the data has a single key or multiple keys
        if len(returned_data[0].keys()) == 1:
            # Single key scenario
            key = list(returned_data[0].keys())[0]
            region_data[region] = {key: []}
            for item in returned_data:
                region_data[region][key].append(item[key])
        else:
            # Multiple keys scenario
            region_data[region] = returned_data
    
    return region_data
    