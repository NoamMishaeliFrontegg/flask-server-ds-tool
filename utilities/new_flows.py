
"""

    # region checked in _get_account_dict_by_vendor_id but for tenant and email its checekd again - need to resolve it 
    # add fetch builder configurations to account object
    # add white label and remove trial scripts 
    
"""

from typing import Dict, List, Optional, Tuple

import aiomysql
from consts import *
from models.models import Account, SAML_groups, SSO_configs, Tenant, Vendor
from utilities.db_and_queries.connections_and_queries import check_in_all_dbs, connect_to_db, fetch_all_query, fetch_one_query
from utilities.handlers import get_account_by_tenant_id, get_account_tenant_id_by_customer_email, get_tenant_id_by_account_tenant_id, get_vendor_by_id, get_vendor_id_by_account_id
from utilities.zendesk_api.zendesk_requests import get_auth_header_from_zendesk_api, get_ticket_emails_from_zd_dict, get_users_from_zd_ticket


async def get_all_account_data_by_zendesk_ticket_number(ticket_number: str) -> Optional[Dict]:
    # zendesk logic
    auth_header = await get_auth_header_from_zendesk_api(email='ZENDESK_EMAIL_TOKEN', api_token='ZENDESK_API_TOKEN')
    res_dict = await get_users_from_zd_ticket(auth_header=auth_header, ticket_number=ticket_number)
    emails = await get_ticket_emails_from_zd_dict(res_dict=res_dict)
    
    if emails['Customer']:
        for email in emails['Customer']:
            account = await get_all_account_data_by_user_email(user_email=email)

            if account:
                return account
    
    return {}   

async def get_all_account_data_by_user_email(user_email: str, region: Optional[str] = None) -> Dict[str,str]:
    # get accountTenantId by email
    user_dict = await get_account_tenant_id_by_customer_email(email=user_email, region=region)

    if not user_dict:
        return None

    # get account Id by accountTenantId:
    account_tenant_id = user_dict.get('tenantId')
    account_tenant_response = await get_tenant_id_by_account_tenant_id(account_tenant_id=account_tenant_id, region=region)
    if not account_tenant_response:
        return None   
    
    account_id = account_tenant_response.get('id')

    account_response = await get_vendor_id_by_account_id(account_id=account_id, region=region)

    vendor_id = account_response.get('id')
    account = await get_all_account_data_by_vendor_id(vendor_id=vendor_id, region=region)
    
    return account 

async def get_all_account_data_by_tenant_id(tenant_id: str,  region: Optional[str] = None) -> Dict[str,str]: 
    account_dict = await get_account_by_tenant_id(tenant_id=tenant_id, region=region)
    
    if not account_dict:
        return {'Error': 'vendor was not found'} ,{} , None
    
    vendor_id = account_dict.get('vendorId')
    
    if account_dict.get('region') and not region:
        region = account_dict.get('region')
        
    account = await get_all_account_data_by_vendor_id(vendor_id=vendor_id, region=region)
    
    return account 

async def get_all_account_data_by_vendor_id(vendor_id: str,  region: Optional[str] = None) -> Dict[str,str]:

    account_dict, account_main_data, db_pool = await get_account_dict_by_vendor_id(vendor_id=vendor_id, region=region)
    
    if account_dict.get('Error'):
        return account_dict.get('Error')
    
    #  3. generate account model and assign id and name
    account = Account(
        id=account_dict.get('id'),
        name=account_dict.get('name'),
        region=account_main_data.get('region'),
    )
    
    vendors_list = await _get_all_vendors_by_account_id(account_id=account_main_data.get('account_id'), db_pool=db_pool)
    
    account.number_of_environments = len(vendors_list)
    account.vendors = vendors_list
    
    account_dict = _object_to_dict(obj=account)
    
    return account_dict
    
async def get_account_dict_by_vendor_id(vendor_id: str,  region: Optional[str] = None) -> Tuple[Dict[str,str], Dict[str,str], Optional[aiomysql.pool.Pool]]:
    
    vendor_dict = await get_vendor_by_id(vendor_id=vendor_id)
    
    if not vendor_dict:
        return {'Error': 'vendor was not found'} ,{} , None
    
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
        return {'Error': 'account was not found'}, {}, None
    
    return account_dict, {'account_id': vendor_dict.get('accountId'),'region': vendor_dict.get('region')}, db_pool

async def _get_all_vendors_by_account_id(account_id: str, db_pool: aiomysql.pool.Pool) -> List[Vendor]:
        #  4. use accountId to fetch all vendors for account
    vendors_res = await fetch_all_query(db_pool=db_pool, query=GET_ALL_VENDORS_BY_ACCOUNT_ID.format(f"'{account_id}'"))          
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
        
        tenants_list = await _get_all_tenants_by_vendor_id(vendor_id=vendor.get('id'), db_pool=db_pool)
            
        vendor_obj.tenants = tenants_list
        vendors_list.append(vendor_obj)
    
    return vendors_list

async def _get_all_tenants_by_vendor_id(vendor_id: str, db_pool: aiomysql.pool.Pool) -> List[Tenant]:
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
        
        sso_config_list, config_id = await _get_sso_configs_by_account_id(account_id=tenant.get('accountId'), db_pool=db_pool)     
        saml_groups_list = await _get_saml_groups_by_config_id(config_id=config_id, db_pool=db_pool)
        
        tenant_obj.sso_configs = sso_config_list
        tenant_obj.saml_groups = saml_groups_list
        
        tenants_list.append(tenant_obj)
        
    return tenants_list

async def _get_sso_configs_by_account_id(account_id: str, db_pool: aiomysql.pool.Pool) -> Tuple[List[SSO_configs], str]:
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
    
async def _get_saml_groups_by_config_id(config_id: str, db_pool: aiomysql.pool.Pool) -> List[SAML_groups]:
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
    
def _object_to_dict(obj, exclude_keys=None) -> Dict[str,str]:
    """
    Recursively converts an object and its nested objects into a dictionary.

    Args:
        obj (object): The object to be converted to a dictionary.
        exclude_keys (list or None): A list of keys to exclude from the dictionary.

    Returns:
        dict: A dictionary representing the object and its nested objects.
    """
    if exclude_keys is None:
        exclude_keys = []

    if isinstance(obj, dict):
        return {k: _object_to_dict(v, exclude_keys) for k, v in obj.items() if k not in exclude_keys}
    elif isinstance(obj, (list, tuple, set)):
        return [_object_to_dict(item, exclude_keys) for item in obj]
    elif hasattr(obj, "__dict__"):
        obj_dict = {k: _object_to_dict(v, exclude_keys) for k, v in obj.__dict__.items() if k not in exclude_keys}
        return obj_dict
    else:
        return obj

    

"""   
############  FLOW 1  ############ By Vendor ID

    connect to the first db in dbs list
        1. use the vendor id to fetch accountId:
            SELECT * FROM frontegg_vendors.vendors v WHERE v.id={} 
            - if not exists: return vendor not found and move to the next db
            
        2. use accountId to fetch account model details:
            SELECT * FROM frontegg_vendors.accounts a WHERE a.id={}
            - if not exists: return account not found and move to the next db

        3. generate account model and assign id and name
        
        4. use accountId to fetch all vendors for account:
            SELECT * FROM frontegg_vendors.vendors v WHERE v.accountId  = {}
            - if not exists: return vendors not found under this account and move to next db
            
        5. generate vendors list into account model and fill with vendors data
        
        6. for each vendor get all tenans by:
            SELECT x.* FROM frontegg_backoffice.accounts x WHERE x.vendorId ={}
            - if not exists: return tenants not found under this vendor and move to next vendor
        
        7. generate tenants list into vendor model and fill with tenat data

        8. return account model
        
############  FLOW 2  ############ By Tenant ID

    connect to the first db in dbs list
    0. use the tenant id to fetch vendor id:
       SELECT x.* FROM frontegg_backoffice.accounts x WHERE x.accountId ={}
    
    if vendor exists:
        start flow 1
    else: 
     move to the next db
    
############  FLOW 3  ############ By User Email


############  FLOW 3  ############ By ZD Ticket

     
"""