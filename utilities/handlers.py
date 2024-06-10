from typing import Optional
from enum import Enum

from flask import jsonify

# from .zendesk_api.zendesk_requests import get_auth_header_from_zendesk_api, get_ticket_emails_from_zd_dict, get_users_from_zd_ticket

from consts import *
from .db_and_queries.connections_and_queries import *
from .utils import *


class QueryEnum(Enum):
    tenant = GET_ACCOUNT_BY_ID_QUERY
    vendor = GET_VENDOR_BY_ID_QUERY

async def get_account_tenant_id_by_customer_email(email: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_account_tenant_id_by_email, db_type='IDENTITY', email=email)
    
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_IDENTITY_{region}', passwd=f'PASSWD_IDENTITY_{region}')
        data = await fetching_account_tenant_id_by_email(db_pool=db_pool,  email=email)
        db_pool.close()     
        await db_pool.wait_closed()

        
    if data:        
        return data
    
    return None

async def get_tenant_id_by_account_tenant_id(account_tenant_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_account_id_by_account_tenant_id, account_tenant_id=account_tenant_id)
    
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_account_id_by_account_tenant_id(db_pool=db_pool,  account_tenant_id=account_tenant_id)
        db_pool.close()     
        
    if data:       
        return data
    
    return None

async def get_vendor_id_by_account_id(account_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_vendor_id_by_account_id, account_id=account_id)
    
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_vendor_id_by_account_id(db_pool=db_pool,  account_id=account_id)
        db_pool.close()     
        
    if data:        
        return data
    
    return None

async def get_account_by_tenant_id(tenant_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        account_dict = await check_in_all_dbs(func=fetch_one_query, query=GET_ACCOUNT_BY_ID_QUERY.format(f"'{tenant_id}'"), db_type='GENERAL')
        region = account_dict.get('region')
        
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        account_dict = await fetch_one_query(db_pool=db_pool,  query=GET_ACCOUNT_BY_ID_QUERY.format(f"'{tenant_id}'"))

        db_pool.close()     
        await db_pool.wait_closed()
    
    return account_dict

async def get_vendor_by_id(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        vendor_dict = await check_in_all_dbs(func=fetch_one_query, query=GET_VENDOR_BY_ID_QUERY.format(f"'{vendor_id}'"), db_type='GENERAL')
        region = vendor_dict.get('region')

    else:         
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        vendor_dict = await fetch_one_query(db_pool=db_pool,  query=GET_VENDOR_BY_ID_QUERY.format(f"'{vendor_id}'"))
        db_pool.close()     
        await db_pool.wait_closed()
    
    return vendor_dict
    

"""   
async def check_customer_region(id_type: str, id: str) -> Optional[Dict]:    
    members = QueryEnum.__members__
    
    result = await check_in_all_dbs(func=fetch_one_query, query=members[id_type].value.format(f"'{id}'"))

    if result:
        return result
        
    return None

async def get_account_id_from_vendor_id(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_vendor_id_by_account_id, vendor_id=vendor_id)
    
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_vendor_id_by_account_id(db_pool=db_pool,  vendor_id=vendor_id)
        db_pool.close()     
        
    if data:        
        return data
    
    return None

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

async def find_user_roles_in_db(user_id: str, tenant_id: str) -> Optional[Dict]:
    
    db_pool  = await connect_to_db(user_name='USER_NAME', host='HOST_IDENTITY_EU', passwd='PASSWD_IDENTITY_EU')
      
    # roles = find_user_role(db_pool=db_pool, user_id=user_id, tenant_id=tenant_id)
    roles = {}
    db_pool.close()
    return roles

async def get_vendors_ids_by_account_id(account_id: str, region: str) -> Optional[str]:
    
    db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
     
    
    vendor_query_result = await fetch_all_query(db_pool=db_pool, query=GET_VENDORS_IDS_BY_ACCOUNT_ID_QUERY.format(f"'{account_id}'"))
    if vendor_query_result:     
        db_pool.close()     
        
        return vendor_query_result.get('id')
    
    db_pool.close()  
    return None

async def get_account_id_by_vendor_id(vendor_id: str, region: str) -> Optional[str]:
    
    db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
     
    vendor_query_result = await fetch_one_query(db_pool=db_pool, query=GET_VENDOR_BY_ID_QUERY.format(f"'{vendor_id}'"))
    if vendor_query_result:
        db_pool.close()     
        
        return vendor_query_result.get('accountId')
    
    db_pool.close()     
        
    return None

async def get_domains_by_vendor_id(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_domains_by_vendor_id, vendor_id=vendor_id)
                
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_domains_by_vendor_id(db_pool=db_pool, vendor_id=vendor_id)
        db_pool.close()     
        
    if data:
        return data
   
    return None

async def get_sso_config_id_by_domain_and_vendor_id(vendor_id: str, domain: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_sso_config_id_by_domain_and_vendor_id, vendor_id=vendor_id, domain=domain)
                
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_sso_config_id_by_domain_and_vendor_id(db_pool=db_pool, vendor_id=vendor_id, domain=domain)
        db_pool.close()     
        
    if data:
        return data
    
    return None

async def get_sso_configs_by_config_id(config_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_sso_configs_by_config_id, config_id=config_id)
                
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_sso_configs_by_config_id(db_pool=db_pool,  config_id=config_id)
        db_pool.close()     
        
    if data:
        return data
    
    return None

async def get_saml_groups_by_config_id(config_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_saml_groups_by_config_id, config_id=config_id)
        
    else:
        db_pool  = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')

        data = await fetching_saml_groups_by_config_id(db_pool=db_pool,  config_id=config_id)
        db_pool.close()     
        
    if data:
        return data
    
    return None

async def manage_vendor_id_from_email(email: str, region: Optional[str] = None) -> Optional[Dict]:
    data = await get_account_tenant_id_from_customer_email(email=email, region=region)

    if not data:
        return None
    
    # account_tenant_response = data.get('account_tenant_response')
    account_tenant_id = data.get('tenantId')
    account_tenant_response = await get_tenant_id_by_account_tenant_id(account_tenant_id=account_tenant_id, region=region)

    if not account_tenant_response:
        return None   
    
    account_id = account_tenant_response.get('id')
    account_response = await get_vendor_id_by_account_id(account_id=account_id, region=region)

    if not account_response:
        return None 
    
    if account_response.get('id'):
        vendor_id = account_response.get('id')
        return vendor_id
    
    return None 
   
async def manage_vendor_id_from_zendesk_ticket(ticket_number: str, region: Optional[str] = None) -> Optional[Dict]:
    # zendesk logic
    auth_header = await get_auth_header_from_zendesk_api(email='ZENDESK_EMAIL_TOKEN', api_token='ZENDESK_API_TOKEN')
    res_dict = await get_users_from_zd_ticket(auth_header=auth_header, ticket_number=ticket_number)
    emails = get_ticket_emails_from_zd_dict(res_dict=res_dict)
    
    if emails['Customer']:
        for email in emails['Customer']:
            vendor_id = await manage_vendor_id_from_email(email=email, region=region)

            if vendor_id:
                return vendor_id
    
    return {}   
        
async def get_all_data_by_vendor_id(vendor_id: str) -> Optional[Dict]:
    res_json = {}
    
    vendor_dict = await check_customer_region(id_type='vendor', id=vendor_id)
    
    if not vendor_dict:
        return None
    
    region = vendor_dict['region']
    
    res_json['general_info'] = {'vendor_id': vendor_id, 'region': region}
    res_json['vendor_dict'] = vendor_dict

    vendor_domains = await get_domains_by_vendor_id(vendor_id=vendor_id, region=region)
    for domain in vendor_domains['domain']:
        sso_config_id_dict = await get_sso_config_id_by_domain_and_vendor_id(vendor_id=vendor_id, domain=domain, region=region)
        
        if sso_config_id_dict:    
            all_configs = []
            for configId in sso_config_id_dict.get('ssoConfigId'):
                sso_configs_dict = await get_sso_configs_by_config_id(config_id=configId, region=region)
                all_configs.append(sso_configs_dict)

            res_json['sso_configs'] = all_configs

    return res_json     



"""