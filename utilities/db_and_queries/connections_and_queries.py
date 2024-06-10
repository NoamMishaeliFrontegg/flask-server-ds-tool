from typing import Any, Callable, Dict, Optional, Tuple, List, Union
import mysql.connector
from consts import *
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv('.env')

async def connect_to_db(user_name: str, host: str, passwd: str) -> aiomysql.pool.Pool:
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
        print(f"MySQL Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
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
        print(f"MySQL Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None
    
    finally:
        await db_pool._wakeup()

async def check_in_all_dbs(func: Callable[..., Tuple[Any, Any]], db_type: Optional[str] = 'GENERAL', *args: Any, **kwargs: Any) -> Dict[str,str]:
    for region in REGIONS:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_{db_type}_{region}', passwd=f'PASSWD_{db_type}_{region}')

        data = await func(db_pool=db_pool,*args, **kwargs)
        
        if data:
            db_pool.close()
            await db_pool.wait_closed()
            data['region'] = region
            return data
        
        db_pool.close()
        await db_pool.wait_closed()

    return None

async def fetching_account_tenant_id_by_email(db_pool: aiomysql.pool.Pool, email: str) -> Dict[str,str]:
    # query = GET_ACCOUNT_TENANT_ID_BY_EMAIL_AND_FE_PROD_ID.format(f"'{email}'")
    query = GET_ACCOUNT_TENANT_ID_BY_EMAIL_AND_FE_PROD_ID.format(f"'{email}'", f"'{os.getenv('PROD_VENDOR_ID')}'")

    account_tenant_response = await fetch_one_query(db_pool=db_pool, query=query)
    
    if account_tenant_response:
        return account_tenant_response
    
    return None

async def fetching_account_id_by_account_tenant_id(db_pool: aiomysql.pool.Pool, account_tenant_id: str) -> Dict[str,str]:
    query = GET_ACCOUNT_ID_BY_ACCOUNT_TENANT_ID.format(f"'{account_tenant_id}'")

    account_tenant_response = await fetch_one_query(db_pool=db_pool, query=query)

    if account_tenant_response:
        return account_tenant_response
    
    return None

async def fetching_vendor_id_by_account_id(db_pool: aiomysql.pool.Pool, account_id: str) -> Dict[str,str]:
    query = GET_VENDORS_IDS_BY_ACCOUNT_ID_QUERY.format(f"'{account_id}'")

    account_response = await fetch_one_query(db_pool=db_pool, query=query)

    if account_response:
        return account_response
    
    return None



"""
async def get_data_from_all_dbs(func: Callable[..., Tuple[Any, Any]], db_type: Optional[str] = 'GENERAL', *args: Any, **kwargs: Any) -> Dict[str,str]:
    
    data_from_all_dbs = {}
    
    for region in REGIONS:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_{db_type}_{region}', passwd=f'PASSWD_{db_type}_{region}')

        data = await func(db_pool=db_pool,*args, **kwargs)
        
        if data:
            data_from_all_dbs[region] = data

        db_pool.close()

    return data_from_all_dbs

async def parse_response(db_pool: aiomysql.pool.Pool, result_to_parse: Tuple) -> Dict:
    
    Args:
        cursor (mysql.connector.cursor_cext.CMySQLCursor): _description_
        result_to_parse (Tuple): _description_

    Returns:
        Dict: _description_
    
    
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

async def find_user_role(db_pool: aiomysql.pool.Pool, user_id: str, tenant_id: str) -> Union[str, List[str]]:
    # get user's tenant id with user_id and tenant_id from 'users_tenants' table
    user_tenant_id = await fetch_one_query(db_pool=db_pool, query=GET_USER_TENANT_BY_USER_ID_AND_TEN_ID_QUERY.format(f"'{user_id}'", f"'{tenant_id}'"))
    if user_tenant_id:
        paresed_user = parse_response(cursor=cursor, result_to_parse=user_tenant_id)

    if paresed_user:
        # get role id with user_tenant_id from 'users_tenants_roles'
        user_tenant_role = await fetch_all_query(db_pool=db_pool, query=GET_ROLES_BY_USER_TEN_ID_QUERY.format(f"'{paresed_user.get('id')}'"))

    if user_tenant_role:
        paresed_user_tenant = parse_response(cursor=cursor, result_to_parse=user_tenant_role)

    if paresed_user_tenant:
        roles_list = []
        # get role name with user_tenant_id from 'users_tenants_roles'
        for role in paresed_user_tenant.get('roleId'):
            user_tenants_roles = await fetch_one_query(db_pool=db_pool, query=GET_ROLE_NAME_BY_ID_QUERY.format(f"'{role}'"))
            
            if user_tenants_roles:
                paresed_user_tenants_roles = parse_response(cursor=cursor, result_to_parse=user_tenants_roles)
                roles_list.append(paresed_user_tenants_roles.get('key'))
        return roles_list
    
    return ''

async def fetching_tenant_dict_from_db(db_pool: aiomysql.pool.Pool, client_id: str) -> Dict[str,str]:
    vendor_query_result = await fetch_one_query(db_pool=db_pool, query=GET_VENDOR_BY_ID_QUERY.format(f"'{client_id}'"))

    if not vendor_query_result:
        return {}
    
    account_query_result = await fetch_one_query(db_pool=db_pool, query=GET_TENANT_BY_ID_QUERY.format(f"'{vendor_query_result.get('accountId')}'"))
        
    if not account_query_result:
        return {}

    tenant_query_result = await fetch_one_query(db_pool=db_pool, query=GET_TENANT_CONFIGURATIONS_QUERY.format(f"'{account_query_result.get('accountTenantId')}'"))
   
    if tenant_query_result:    
        return { 'id': tenant_query_result.get('id'), 'tenant_id': tenant_query_result.get('tenantId')}
    
    return {}

async def fetching_domains_by_vendor_id(db_pool: aiomysql.pool.Pool, vendor_id: str) -> Dict[str,str]:
    all_domains = await fetch_all_query(db_pool=db_pool, query=GET_SSO_DOMAINS_BY_VENDOR.format(f"'{vendor_id}'"))
    
    if all_domains:
        return all_domains
    
    return None

async def fetching_sso_config_id_by_domain_and_vendor_id(db_pool: aiomysql.pool.Pool, vendor_id: str, domain: str) -> Dict[str,str]:
    query = GET_SSO_DOMAINS_BY_VENDOR.format(f"'{vendor_id}'") + ' ' +  AND_DOMAIN.format(f"'{domain}'")
    domain_dict = await fetch_all_query(db_pool=db_pool, query=query)

    if domain_dict:
        return domain_dict
    
    return None

async def fetching_sso_configs_by_config_id(db_pool: aiomysql.pool.Pool, config_id: str) -> Dict[str,str]:
    query = GET_SSO_CONFIGS_BY_SSO_CONFIG_ID.format(f"'{config_id}'")
    sso_configs = await fetch_all_query(db_pool=db_pool, query=query)

    if sso_configs:
        return sso_configs
    
    return None

async def fetching_saml_groups_by_config_id(db_pool: aiomysql.pool.Pool, config_id: str) -> Dict[str,str]:
    query = GET_SAML_GROUPS_BY_SSO_CONFIG_ID.format(f"'{config_id}'")
    saml_groups = await fetch_all_query(db_pool=db_pool, query=query)

    if saml_groups:
        return saml_groups
    
    return None

"""



# 
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 
# ---------------------------------------------------------------------------
#  needs to check the usage of GET_VENDOR_ID_BY_ACCOUNT_ID and why i did not 
#  used it instead of creating GET_VENDORS_IDS_BY_ACCOUNT_ID_QUERY
# ---------------------------------------------------------------------------
# 
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
