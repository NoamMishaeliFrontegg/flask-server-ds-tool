from typing import Optional
from enum import Enum

from flask import jsonify

from .zendesk_api.zendesk_requests import get_auth_header_from_zendesk_api, get_ticket_emails_from_zd_dict, get_users_from_zd_ticket

from consts import *
from .db_and_queries.connections_and_queries import *
from .utils import *


class QueryEnum(Enum):
    tenant = GET_ACCOUNT_BY_ID_QUERY
    vendor = GET_VENDOR_BY_ID_QUERY
    # user = GET_USER_BY_ID_QUERY

async def check_customer_region(id_type: str, id: str) -> Optional[Dict]:    
    members = QueryEnum.__members__
    
    result = await check_in_all_dbs(func=fetch_one_query, query=members[id_type].value.format(f"'{id}'"))

    if result:
        updated_res = dict(result[0])
        updated_res['region'] = result[1]
        return updated_res
        
    return None

async def remove_trial_process(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    
    if not region:
        data = await check_in_all_dbs(func=fetching_tenant_dict_from_db, client_id=vendor_id)
        data = dict(data[0])
        
    else:
        db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_tenant_dict_from_db(cursor=cursor, client_id=vendor_id)
        db.close()     
        
    if data:
        production_client_id, production_secret = get_production_env_variables()
        auth_response = authenticate_as_vendor(production_client_id=production_client_id, production_client_secret=production_secret)
        result = remove_trial_request(tenant_id=data.get('tenant_id'), id=data.get('id'), production_vendor_token=auth_response.get('token'))
        
        if result:
            return result
        
    return None

async def find_user_roles_in_db(user_id: str, tenant_id: str) -> Optional[Dict]:
    
    db = await connect_to_db(user_name='USER_NAME', host='HOST_IDENTITY_EU', passwd='PASSWD_IDENTITY_EU')
    cursor = db.cursor(buffered=True)

    roles = find_user_role(cursor=cursor, user_id=user_id, tenant_id=tenant_id)
    
    db.close()
    return roles

async def get_environments_ids_by_account_id(account_id: str, region: str) -> Optional[str]:
    
    db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
    cursor = db.cursor()
    
    vendor_query_result = fetch_all_query(cursor=cursor, query=GET_ENV_IDS_BY_ACCOUNT_ID_QUERY.format(f"'{account_id}'"))
    if vendor_query_result:
        vendor_dict_response = parse_response(cursor=cursor, result_to_parse=vendor_query_result)        
        db.close()     
        
        return vendor_dict_response.get('id')
    
    db.close()  
    return None

async def get_account_id_by_vendor_id(vendor_id: str, region: str) -> Optional[str]:
    
    db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
    cursor = db.cursor()
    
    vendor_query_result = fetch_one_query(cursor=cursor, query=GET_VENDOR_BY_ID_QUERY.format(f"'{vendor_id}'"))
    if vendor_query_result:
        vendor_dict_response = parse_response(cursor=cursor, result_to_parse=vendor_query_result)        
        db.close()     
        
        return vendor_dict_response.get('accountId')
    
    db.close()     
        
    return None

async def get_domains_by_vendor_id(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_domains_by_vendor_id, vendor_id=vendor_id)
                
    else:
        db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_domains_by_vendor_id(cursor=cursor, vendor_id=vendor_id)
        db.close()     
        
    if data:
        return data
   
    return None

async def get_sso_config_id_by_domain_and_vendor_id(vendor_id: str, domain: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_sso_config_id_by_domain_and_vendor_id, vendor_id=vendor_id, domain=domain)
                
    else:
        db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_sso_config_id_by_domain_and_vendor_id(cursor=cursor, vendor_id=vendor_id, domain=domain)
        db.close()     
        
    if data:
        return data
    
    return None

async def get_sso_configs_by_config_id(config_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_sso_configs_by_config_id, config_id=config_id)
                
    else:
        db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_sso_configs_by_config_id(cursor=cursor,  config_id=config_id)
        db.close()     
        
    if data:
        return data
    
    return None

async def get_saml_groups_by_config_id(config_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = await check_in_all_dbs(func=fetching_saml_groups_by_config_id, config_id=config_id)
        
    else:
        db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_saml_groups_by_config_id(cursor=cursor,  config_id=config_id)
        db.close()     
        
    if data:
        return data
    
    return None

async def get_account_tenant_id_from_customer_email(email: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data_with_region = await check_in_all_dbs(func=fetching_account_tenant_id_by_email, db_type='IDENTITY', email=email)
        
        if data_with_region:
            data = data_with_region[0]
            region = data_with_region[1]
    
    else:
        db = await connect_to_db(user_name='USER_NAME', host=f'HOST_IDENTITY_{region}', passwd=f'PASSWD_IDENTITY_{region}')
        cursor = db.cursor()
        data = fetching_account_tenant_id_by_email(cursor=cursor,  email=email)
        db.close()     
        
    if data:        
        return data
    
    return None

async def get_tenant_id_by_account_tenant_id(account_tenant_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data_with_region = await check_in_all_dbs(func=fetching_account_id_by_account_tenant_id, account_tenant_id=account_tenant_id)
        
        if data_with_region:
            data = data_with_region[0]
            region = data_with_region[1]
    
    else:
        db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_account_id_by_account_tenant_id(cursor=cursor,  account_tenant_id=account_tenant_id)
        db.close()     
        
    if data:       
        return data
    
    return None

async def get_vendor_id_by_tenant_id(account_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data_with_region = await check_in_all_dbs(func=fetching_vendor_id_by_account_id, account_id=account_id)
        if data_with_region:
            data = data_with_region[0]
            region = data_with_region[1]
    
    else:
        db = await connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_vendor_id_by_account_id(cursor=cursor,  account_id=account_id)
        db.close()     
        
    if data:        
        return data
    
    return None

async def manage_vendor_id_from_email(email: str, region: Optional[str] = None) -> Optional[Dict]:
    data = await get_account_tenant_id_from_customer_email(email=email, region=region)

    if not data:
        return jsonify('None') 
    
    account_tenant_response = data.get('account_tenant_response')
    account_tenant_id = account_tenant_response.get('tenantId')
    account_tenant_response = await get_tenant_id_by_account_tenant_id(account_tenant_id=account_tenant_id, region=region)

    if not account_tenant_response:
        return jsonify('None')    
    
    account_tenant_response_dict = account_tenant_response.get('account_tenant_response')
    account_id = account_tenant_response_dict.get('id')
    account_response = await get_vendor_id_by_tenant_id(account_id=account_id, region=region)

    if not account_response:
        return jsonify('None')    

    account_response_dict = account_response.get('account_response')
    
    if account_response_dict.get('id'):
        return account_response_dict.get('id')
    
    return jsonify('None')  
    
async def manage_vendor_id_from_zendesk_ticket(ticket_number: str, region: Optional[str] = None) -> Optional[Dict]:
    # zendesk logic
    auth_header = await get_auth_header_from_zendesk_api(email='ZENDESK_EMAIL_TOKEN', api_token='ZENDESK_API_TOKEN')
    res_dict = await get_users_from_zd_ticket(auth_header=auth_header, ticket_number=ticket_number)
    emails = get_ticket_emails_from_zd_dict(res_dict=res_dict)
    
    if emails['Customer']:
        print(emails['Customer'], "\t", len(emails['Customer']))
        for email in emails['Customer']:
            print(email)
            # email = emails['Customer'][0]     
            vendor_id = await manage_vendor_id_from_email(email=email, region=region)

            return vendor_id
    
    return {}   


if __name__ == "__main__":
  
    db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_US', passwd=f'PASSWD_GENERAL_US')
    cursor = db.cursor()
    
    