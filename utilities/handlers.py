import aiomysql
from enum import Enum

from flask import jsonify
from consts import *
from .utils import *
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

from models.models import Account, SAML_groups, SSO_configs, Tenant, Vendor
from utilities.db_and_queries.connections_and_queries import check_in_all_dbs, connect_to_db, fetch_all_query, fetch_one_query
from utilities.zendesk_api.zendesk_requests import get_auth_header_from_zendesk_api, get_ticket_emails_from_zd_dict, get_users_from_zd_ticket
from utilities.logger_config import log_execution_time, logger

from .utils import object_to_dict

class QueryEnum(Enum):
    tenant = GET_ACCOUNT_BY_ID_QUERY
    vendor = GET_VENDOR_BY_ID_QUERY

@log_execution_time
async def get_all_account_data_by_zendesk_ticket_number(ticket_number: str) -> Optional[Dict]:
    """
    Retrieves all account data associated with a given Zendesk ticket number.
    
    This function first obtains an authentication header from the Zendesk API using the `get_auth_header_from_zendesk_api` function.
    It then retrieves the users associated with the given ticket number using the `get_users_from_zd_ticket` function.
    From the retrieved user data, it extracts the email addresses using the `get_ticket_emails_from_zd_dict` function.
    For each customer email address, it attempts to fetch the associated account data using the `get_all_account_data_by_user_email` function.
    If an account is found, it returns the account data. Otherwise, it returns an empty dictionary.

    Args:
        ticket_number (str): The Zendesk ticket number to search for.

    Returns:
        Optional[Dict]: A dictionary containing the account data, or an empty dictionary if no account is found.
    """
    auth_header = await get_auth_header_from_zendesk_api(email='ZENDESK_EMAIL_TOKEN', api_token='ZENDESK_API_TOKEN')
    res_dict = await get_users_from_zd_ticket(auth_header=auth_header, ticket_number=ticket_number)

    if res_dict.get('error'):
        return {'error': res_dict.get('error')}
    
    emails = await get_ticket_emails_from_zd_dict(res_dict=res_dict)
    
    if emails['Customer']:
        for email in emails['Customer']:
            account = await get_all_account_data_by_user_email(user_email=email)

            if account:
                return account
    
    return {'error': 'ticket was not found'}   

@log_execution_time
async def get_all_account_data_by_user_email(user_email: str, region: Optional[str] = None) -> Dict[str,str]:    
    """
    Retrieves all account data associated with a given user email address.
    
    This function first fetches the account tenant ID associated with the given email address using the `_fetch_account_tenant_id_by_customer_email_from_db` function.
    If the account tenant ID is found, it then fetches the account ID using the `_fetch_tenant_id_by_account_tenant_id_from_db` function.
    Next, it fetches the vendor ID using the `_fetch_vendor_id_by_account_id_from_db` function.
    Finally, it calls the `get_all_account_data_by_vendor_id` function to retrieve the complete account data.

    Args:
        user_email (str): The user email address to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Dict[str, str]: A dictionary containing the account data, or None if no account is found.
    """
    # get accountTenantId by email
    user_dict = await _fetch_account_tenant_id_by_customer_email_from_db(email=user_email, region=region)

    if not user_dict:
        return {'error': 'email is not valid or cannot be found'}

    # get account Id by accountTenantId:
    account_tenant_id = user_dict.get('tenantId')
    account_tenant_response = await _fetch_tenant_id_by_account_tenant_id_from_db(account_tenant_id=account_tenant_id, region=region)
    if not account_tenant_response:
        return None   
    
    account_id = account_tenant_response.get('id')

    account_response = await _fetch_vendor_id_by_account_id_from_db(account_id=account_id, region=region)

    vendor_id = account_response.get('id')
    account = await get_all_account_data_by_vendor_id(vendor_id=vendor_id, region=region)
    
    return account 

@log_execution_time
async def get_all_account_data_by_tenant_id(tenant_id: str,  region: Optional[str] = None) -> Dict[str,str]: 
    """
    Retrieves all account data associated with a given tenant ID.
    
    This function first fetches the account dictionary associated with the given tenant ID using the `_fetch_account_by_tenant_id_from_db` function.
    If the account is found, it extracts the vendor ID and calls the `get_all_account_data_by_vendor_id` function to retrieve the complete account data.
    If the region is not provided, it attempts to retrieve the region from the account dictionary.

    Args:
        tenant_id (str): The tenant ID to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Dict[str, str]: A dictionary containing the account data, or an error message if no account is found.
    """
    account_dict = await _fetch_account_by_tenant_id_from_db(tenant_id=tenant_id, region=region)
        
    if not account_dict:
        return {'error': 'tenant was not found'}
    
    vendor_id = account_dict.get('vendorId')
    
    if account_dict.get('region') and not region:
        region = account_dict.get('region')
        
    account = await get_all_account_data_by_vendor_id(vendor_id=vendor_id, region=region)
    
    return account 

@log_execution_time
async def get_all_account_data_by_vendor_id(vendor_id: str,  region: Optional[str] = None) -> Dict[str,str]:
    """
    Retrieves all account data associated with a given vendor ID.
    
    This function first fetches the account dictionary, account main data, and a database connection pool associated with the given vendor ID using the `_fetch_account_dict_by_vendor_id_from_db` function.
    If the account is found, it creates an `Account` object and populates it with the account ID, name, and region.
    It then fetches a list of `Vendor` objects associated with the account using the `_fetch_all_vendors_by_account_id_from_db` function and assigns it to the `vendors` attribute of the `Account` object.
    Finally, it converts the `Account` object to a dictionary and returns it.

    Args:
        vendor_id (str): The vendor ID to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Dict[str, str]: A dictionary containing the account data, or an error message if no account is found.
    """
    load_dotenv()
    # prod_vendor_id = os.getenv("PROD_VENDOR_ID")
    # if vendor_id == prod_vendor_id:
    #     return jsonify({'error': 'Nice try! are trying to f@#k my app?!\nDONT ENTER FRONTEGG\'S PROD ID'})
    
    account_dict, account_main_data, db_pool = await _fetch_account_dict_by_vendor_id_from_db(vendor_id=vendor_id, region=region)
    
    if account_dict.get('error'):
        return account_dict
    
    #  3. generate account model and assign id and name
    account = Account(
        id=account_dict.get('id'),
        name=account_dict.get('name'),
        region=account_main_data.get('region'),
    )
    
    vendors_list = await _fetch_all_vendors_by_account_id_from_db(account_id=account_main_data.get('account_id'), db_pool=db_pool)
    
    account.number_of_environments = len(vendors_list)
    account.vendors = vendors_list
    
    account_dict = object_to_dict(obj=account)
    
    return account_dict

@log_execution_time
async def check_if_white_label(vendor_id: str, region: Optional[str] = None) -> int:
    """
    Check if a vendor is in white label mode.

    Args:
        vendor_id (str): The unique identifier of the vendor.
        region (Optional[str]): The region to search for the vendor. Defaults to None.

    Returns:
        int: vendor_id if the vendor is in white label mode, 0 otherwise.

    Note:
        Relies on _fetch_vendor_by_id_from_db for fetching vendor data.
    """
    vendor_dict = await _fetch_vendor_by_id_from_db(vendor_id=vendor_id, region=region)
    is_white_labeled = vendor_dict.get('whiteLabelMode')
    if is_white_labeled == 1:
        return vendor_id 
    
    return 0

@log_execution_time
async def _fetch_account_dict_by_vendor_id_from_db(vendor_id: str,  region: Optional[str] = None) -> Tuple[Dict[str,str], Dict[str,str], Optional[aiomysql.pool.Pool]]:
    """
    Retrieves the account dictionary, account main data, and a database connection pool associated with a given vendor ID.
    
    This function first fetches the vendor dictionary associated with the given vendor ID using the `_fetch_vendor_by_id_from_db` function.
    If the vendor is found, it extracts the account ID and region, connects to the appropriate database using the `connect_to_db` function, and fetches the account details using the `fetch_one_query` function.
    If the account is found, it returns a tuple containing the account dictionary, account main data dictionary, and the database connection pool.
    Otherwise, it returns an error message and empty dictionaries.

    Args:
        vendor_id (str): The vendor ID to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Tuple[Dict[str, str], Dict[str, str], Optional[aiomysql.pool.Pool]]: A tuple containing the account dictionary,
            account main data dictionary, and a database connection pool (or None if no account is found).
    """  
    vendor_dict = await _fetch_vendor_by_id_from_db(vendor_id=vendor_id)

    if not vendor_dict:
        return {'error': 'vendor was not found'} ,{} , None
    
    if vendor_dict.get('region') and not region:
        region = vendor_dict.get('region')
    
    account_id =  vendor_dict.get('accountId') 
            
    # 2. fetch account dict
    if account_id and region:    
        db_pool  = await connect_to_db(
            user_name='USER_NAME', 
            host=f'HOST_GENERAL_{region}', 
            passwd=f'PASSWD_GENERAL_{region}'
        )
        
        account_dict = await fetch_one_query(
            db_pool=db_pool, 
            query=GET_ACCOUNT_DETAILS_BY_ID.format(f"'{account_id}'")
        )          
          
    if not account_dict:            
        return {'error': 'account was not found'}, {}, None
    
    return account_dict, {'account_id': vendor_dict.get('accountId'),'region': vendor_dict.get('region')}, db_pool

@log_execution_time
async def _fetch_all_vendors_by_account_id_from_db(account_id: str, db_pool: aiomysql.pool.Pool) -> List[Vendor]:
    """
    Retrieves a list of Vendor objects associated with a given account ID.
    
    This function first fetches all vendor IDs associated with the given account ID using the `fetch_all_query` function.
    It then creates a list of `Vendor` objects, populating each object with vendor data and a list of `Tenant` objects retrieved using the `_fetch_all_tenants_by_vendor_id_from_db` function.

    Args:
        account_id (str): The account ID to search for.
        db_pool (aiomysql.pool.Pool): The database connection pool.

    Returns:
        List[Vendor]: A list of Vendor objects.
    """   
    #  4. use accountId to fetch all vendors for account
    vendors_res = await fetch_all_query(db_pool=db_pool, query=GET_VENDORS_IDS_BY_ACCOUNT_ID_QUERY.format(f"'{account_id}'"))          
    # 5. generate vendors list into account model and fill with vendors data
    vendors_list = []
    
    for vendor in vendors_res:
        vendor_obj = Vendor(
            id=vendor.get('id'),
            env_name=vendor.get('environmentName'),
            app_url=vendor.get('appURL'),
            login_url=vendor.get('loginURL'),
            host=vendor.get('host'),
            country=vendor.get('country'),
            fe_stack=vendor.get('frontendStack'),
            be_stack=vendor.get('backendStack'),
            account_id=vendor.get('accountId'),
        )
        
        tenants_list = await _fetch_all_tenants_by_vendor_id_from_db(vendor_id=vendor.get('id'), db_pool=db_pool)
            
        vendor_obj.tenants = tenants_list
        vendors_list.append(vendor_obj)
    
    return vendors_list

@log_execution_time
async def _fetch_all_tenants_by_vendor_id_from_db(vendor_id: str, db_pool: aiomysql.pool.Pool) -> List[Tenant]:
    """
    Retrieves a list of Tenant objects associated with a given vendor ID.
    
    This function first fetches all tenant data associated with the given vendor ID using the `fetch_all_query` function.
    It then creates a list of `Tenant` objects, populating each object with tenant data, SSO configurations retrieved using the `_fetch_sso_configs_by_account_id_from_db` function, and SAML groups retrieved using the `_fetch_saml_groups_by_config_id_from_db` function.

    Args:
        vendor_id (str): The vendor ID to search for.
        db_pool (aiomysql.pool.Pool): The database connection pool.

    Returns:
        List[Tenant]: A list of Tenant objects.
    """   
    # 6. for each vendor get all tenans by:
    tenants_res = await fetch_all_query(db_pool=db_pool, query=GET_ALL_TENANTS_BY_VENDOR_ID.format(f"'{vendor_id}'"))          
    tenants_list = []

    # 7. generate tenants list into vendor model and fill with tenat data
    for tenant in tenants_res:
        tenant_obj = Tenant(
            id=tenant.get('accountId'),
            name=tenant.get('name'),
            meta_data=tenant.get('metadata'),
            vendor_id=tenant.get('vendorId')
        )
        
        sso_config_list, config_id = await _fetch_sso_configs_by_account_id_from_db(account_id=tenant.get('accountId'), db_pool=db_pool)     
        saml_groups_list = await _fetch_saml_groups_by_config_id_from_db(config_id=config_id, db_pool=db_pool)
        
        tenant_obj.sso_configs = sso_config_list
        tenant_obj.saml_groups = saml_groups_list
        
        tenants_list.append(tenant_obj)
        
    return tenants_list

async def _fetch_sso_configs_by_account_id_from_db(account_id: str, db_pool: aiomysql.pool.Pool) -> Tuple[List[SSO_configs], str]:
    """
    Retrieves a list of SSO configuration objects and the SSO configuration ID associated with a given account ID.
    
    This function first fetches all SSO domains associated with the given account ID using the `fetch_all_query` function.
    For each domain, it extracts the SSO configuration ID and fetches the corresponding SSO configurations.
    It then creates a list of `SSO_configs` objects, populating each object with the configuration data.

    Args:
        account_id (str): The account ID to search for.
        db_pool (aiomysql.pool.Pool): The database connection pool.

    Returns:
        Tuple[List[SSO_configs], str]: A tuple containing a list of SSO configuration objects and the SSO configuration ID.
    """
    config_id = ''
    sso_configs_list = []
    sso_config_obj_list = []
    
    # 8. for each tenant get all sso configs:
    domains_list = await fetch_all_query(db_pool=db_pool, query=GET_SSO_DOMAINS_BY_TENANT.format(f"'{account_id}'"))      
    for domain_row in domains_list:
        config_id = domain_row.get('ssoConfigId')
        
        if config_id:
            sso_config_query = GET_SSO_CONFIGS_BY_SSO_CONFIG_ID.format(f"'{config_id}'")
            sso_configs_list = await fetch_all_query(db_pool=db_pool, query=sso_config_query)
    
    if sso_configs_list:
        for sso_config in sso_configs_list:
            sso_config_obj = SSO_configs(
                id=sso_config.get('id'),
                vendorId=sso_config.get('vendorId'),
                tenantId=sso_config.get('tenantId'),
                domain=sso_config.get('domain'),
                validated=sso_config.get('validated'),
                ssoEndpoint=sso_config.get('ssoEndpoint'),
                publicCertificate=sso_config.get('publicCertificate'),
                signRequest=sso_config.get('signRequest'),
                acsUrl=sso_config.get('acsUrl'),
                type=sso_config.get('type'),
                spEntityId=sso_config.get('spEntityId'),
                config_metadata=sso_config.get('config_metadata'),
                skipEmailDomainValidation=sso_config.get('skipEmailDomainValidation'),
                overrideActiveTenant=sso_config.get('overrideActiveTenant'),
            )
            sso_config_obj_list.append(sso_config_obj)
    
    return sso_config_obj_list, config_id

async def _fetch_saml_groups_by_config_id_from_db(config_id: str, db_pool: aiomysql.pool.Pool) -> List[SAML_groups]:
    """
    Retrieves a list of SAML group objects associated with a given SSO configuration ID.
    
    This function fetches all SAML groups associated with the given SSO configuration ID using the `fetch_all_query` function.
    It then creates a list of `SAML_groups` objects, populating each object with the group data.

    Args:
        config_id (str): The SSO configuration ID to search for.
        db_pool (aiomysql.pool.Pool): The database connection pool.

    Returns:
        List[SAML_groups]: A list of SAML group objects.
    """
    saml_groups_obj = []
    
    saml_groups_query = GET_SAML_GROUPS_BY_SSO_CONFIG_ID.format(f"'{config_id}'")
    saml_groups = await fetch_all_query(db_pool=db_pool, query=saml_groups_query)
    
    if saml_groups:
        for saml_group in saml_groups:
            saml_group_obj = SAML_groups(
                id=saml_group.get('id'),
                samlConfigId=saml_group.get('samlConfigId'),
                enabled=saml_group.get('enabled'),
                group=saml_group.get('group')
            )
            
            saml_groups_obj.append(saml_group_obj)
    
    return saml_groups_obj

@log_execution_time    
async def _fetch_account_tenant_id_by_customer_email_from_db(email: str, region: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieves the account tenant ID associated with a given customer email address.
    
    This function fetches the account tenant ID from the appropriate database based on the provided email address.
    If no region is specified, it checks all databases using the `check_in_all_dbs` function. 
    Otherwise, it connects to the database for the specified region.

    Args:
        email (str): The customer email address to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Optional[Dict]: A dictionary containing the account tenant ID, or None if no data is found.
    """
    if not region:
        data = await check_in_all_dbs(func=fetching_account_tenant_id_by_email, db_type=IDENTITY, email=email)
    
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_IDENTITY_{region}', passwd=f'PASSWD_IDENTITY_{region}')
        data = await fetching_account_tenant_id_by_email(db_pool=db_pool,  email=email)
        db_pool.close()     
        await db_pool.wait_closed()

        
    if data:        
        return data
    
    return None

@log_execution_time
async def _fetch_tenant_id_by_account_tenant_id_from_db(account_tenant_id: str, region: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieves the tenant ID associated with a given account tenant ID.
    
    This function fetches the tenant ID from the appropriate database based on the provided account tenant ID.
    If no region is specified, it checks all databases using the `check_in_all_dbs` function. 
    Otherwise, it connects to the database for the specified region.

    Args:
        account_tenant_id (str): The account tenant ID to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Optional[Dict]: A dictionary containing the tenant ID, or None if no data is found.
    """    
    if not region:
        data = await check_in_all_dbs(func=fetching_account_id_by_account_tenant_id, account_tenant_id=account_tenant_id)
    
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_account_id_by_account_tenant_id(db_pool=db_pool,  account_tenant_id=account_tenant_id)
        db_pool.close()     
        
    if data:       
        return data
    
    return None

@log_execution_time
async def _fetch_vendor_id_by_account_id_from_db(account_id: str, region: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieves the vendor ID associated with a given account ID.
    
    This function fetches the vendor ID from the appropriate database based on the provided account ID.
    If no region is specified, it checks all databases using the `check_in_all_dbs` function. 
    Otherwise, it connects to the database for the specified region.

    Args:
        account_id (str): The account ID to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Optional[Dict]: A dictionary containing the vendor ID, or None if no data is found.
    """    
    if not region:
        data = await check_in_all_dbs(func=fetching_vendor_id_by_account_id, account_id=account_id)
    
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_vendor_id_by_account_id(db_pool=db_pool,  account_id=account_id)
        db_pool.close()     
        
    if data:        
        return data
    
    return None

@log_execution_time
async def _fetch_account_by_tenant_id_from_db(tenant_id: str, region: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieves the account dictionary associated with a given tenant ID.
    
    This function fetches the account details from the appropriate database based on the provided tenant ID.
    If no region is specified, it checks all databases using the `check_in_all_dbs` function.
    Otherwise, it connects to the database for the specified region.

    Args:
        tenant_id (str): The tenant ID to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Optional[Dict]: A dictionary containing the account details, or None if no data is found.
    """
    if not region:
        account_dict = await check_in_all_dbs(func=fetch_one_query, query=GET_ACCOUNT_BY_ID_QUERY.format(f"'{tenant_id}'"), db_type='GENERAL')
        
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        account_dict = await fetch_one_query(db_pool=db_pool,  query=GET_ACCOUNT_BY_ID_QUERY.format(f"'{tenant_id}'"))

        db_pool.close()     
        await db_pool.wait_closed()
    
    return account_dict

@log_execution_time
async def _fetch_vendor_by_id_from_db(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieves the vendor dictionary associated with a given vendor ID.
    
    This function first checks if a region is provided. If not, it attempts to retrieve the vendor data from all databases using the `check_in_all_dbs` function.
    If a region is provided, it connects to the appropriate database using the `connect_to_db` function and fetches the vendor details using the `fetch_one_query` function.
    Finally, it closes the database connection and returns the vendor dictionary.

    Args:
        vendor_id (str): The vendor ID to search for.
        region (Optional[str], optional): The region to search in. Defaults to None.

    Returns:
        Optional[Dict]: A dictionary containing the vendor data, or None if no vendor is found.
    """
    if not region:
        vendor_dict = await check_in_all_dbs(func=fetch_one_query, query=GET_VENDOR_BY_ID_QUERY.format(f"'{vendor_id}'"), db_type='GENERAL')

    else:         
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        vendor_dict = await fetch_one_query(db_pool=db_pool,  query=GET_VENDOR_BY_ID_QUERY.format(f"'{vendor_id}'"))
        db_pool.close()     
        await db_pool.wait_closed()
    
    return vendor_dict

@log_execution_time    
async def handle_white_label_process(vendor_id: str, account_id: str, is_enabled: str, region: str) -> Optional[Dict[str,str]]:
    # should implement the accounttenantid process
    
    if not account_id and not vendor_id:
        return jsonify({'error': 'None'})
        
    stripped_vendor_id = str(vendor_id).strip('\'"')
    is_valid = validate_uuid(uuid_string=stripped_vendor_id)
    white_label_counter = 0
    white_label_vendors = []
    
    if not is_valid:
        return jsonify({'error': 'Invalid ID'})
    
    if bool(is_enabled):
        production_client_id, production_secret = get_production_env_variables()

        auth_response = authenticate_as_vendor(
            production_client_id=production_client_id, 
            production_client_secret=production_secret
            )
    
        account_id = await get_account_id_by_vendor_id(vendor_id=stripped_vendor_id, region=region)

        if account_id:
            env_ids = await get_vendors_ids_by_account_id(account_id=account_id, region=region)            

        if env_ids:
            for id in env_ids:    

                response = request_white_lable(
                    is_enabled=is_enabled, 
                    vendor_id=id, 
                    token=auth_response.get('token'),
                    region=region
                    )
                
                if response.get('status_code') == 200:
                    is_vendor_white_label = await check_if_white_label(vendor_id=id, region=region)
                    
                    if is_vendor_white_label != 0:
                        white_label_counter += 1
                        white_label_vendors.append(id)
                                
            return jsonify({'status_code': 200, 'number_of_envs': len(env_ids), 'white_labeled': white_label_counter, 'white_labeled_vendors': white_label_vendors})        
    
    return jsonify({'error': 'You selected the body-param as disabled'})

# TODO: fix remove trial and white label to work with all regions 

async def remove_trial_process(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    
    if not region:
        data = await check_in_all_dbs(func=fetching_tenant_dict_from_db, client_id=vendor_id)
        data = dict(data)
        
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_tenant_dict_from_db(db_pool=db_pool, client_id=vendor_id)
        db_pool.close()     
        
    if data:
        production_client_id, production_secret = get_production_env_variables()
        auth_response = authenticate_as_vendor(production_client_id=production_client_id, production_client_secret=production_secret)
        result = remove_trial_request(tenant_id=data.get('tenant_id'), id=data.get('id'), production_vendor_token=auth_response.get('token'))
        
        if result:
            return result
        
    return None

async def get_account_id_by_vendor_id(vendor_id: str, region: str = 'EU') -> Optional[str]:
    
    db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
     
    vendor_query_result = await fetch_one_query(db_pool=db_pool, query=GET_VENDOR_BY_ID_QUERY.format(f"'{vendor_id}'"))
    if vendor_query_result:
        db_pool.close()     
        
        return vendor_query_result.get('accountId')
    
    db_pool.close()     
        
    return None

async def get_vendors_ids_by_account_id(account_id: str, region: str = 'EU') -> Optional[List[str]]:
    
    db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
    
    vendor_query_result = await fetch_all_query(db_pool=db_pool, query=GET_VENDORS_IDS_BY_ACCOUNT_ID_QUERY.format(f"'{account_id}'"))
    if vendor_query_result:     
        db_pool.close()     
        env_list = []
        
        for vendor in vendor_query_result:
            env_list.append(vendor.get('id'))
        
        return env_list
    
    db_pool.close()  
    return None


