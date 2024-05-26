from typing import Optional
from enum import Enum

from .consts import *
from .connections_and_queries import *
from .utilis import *


class QueryEnum(Enum):
    tenant = GET_ACCOUNT_BY_ID_QUERY
    vendor = GET_VENDOR_BY_ID_QUERY
    # user = GET_USER_BY_ID_QUERY

def check_customer_region(id_type: str, id: str) -> Optional[Dict]:    
    members = QueryEnum.__members__
    
    result = check_in_all_dbs(func=fetch_one_query, query=members[id_type].value.format(f"'{id}'"))

    if result:
        updated_res = dict(result[0])
        updated_res['region'] = result[1]
        return updated_res
        
    return None

def remove_trial_process(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    
    if not region:
        data = check_in_all_dbs(func=fetching_tenant_dict_from_db, client_id=vendor_id)
        data = dict(data[0])
        
    else:
        db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
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

def find_user_roles_in_db(user_id: str, tenant_id: str) -> Optional[Dict]:
    
    db = connect_to_db(user_name='USER_NAME', host='HOST_IDENTITY_EU', passwd='PASSWD_IDENTITY_EU')
    cursor = db.cursor(buffered=True)

    roles = find_user_role(cursor=cursor, user_id=user_id, tenant_id=tenant_id)
    
    db.close()
    return roles

def get_environments_ids_by_account_id(account_id: str, region: str) -> Optional[str]:
    
    db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
    cursor = db.cursor()
    
    vendor_query_result = fetch_all_query(cursor=cursor, query=GET_ENV_IDS_BY_ACCOUNT_ID_QUERY.format(f"'{account_id}'"))
    if vendor_query_result:
        vendor_dict_response = parse_response(cursor=cursor, result_to_parse=vendor_query_result)        
        db.close()     
        
        return vendor_dict_response.get('id')
    
    db.close()  
    return None

def get_account_id_by_vendor_id(vendor_id: str, region: str) -> Optional[str]:
    
    db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
    cursor = db.cursor()
    
    vendor_query_result = fetch_one_query(cursor=cursor, query=GET_VENDOR_BY_ID_QUERY.format(f"'{vendor_id}'"))
    if vendor_query_result:
        vendor_dict_response = parse_response(cursor=cursor, result_to_parse=vendor_query_result)        
        db.close()     
        
        return vendor_dict_response.get('accountId')
    
    db.close()     
        
    return None

def get_domains_by_vendor_id(vendor_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = check_in_all_dbs(func=fetching_domains_by_vendor_id, vendor_id=vendor_id)
                
    else:
        db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_domains_by_vendor_id(cursor=cursor, vendor_id=vendor_id)
        db.close()     
        
    if data:
        return data

    """
    if data.get('result'):
            # res = data.get("result")
            res = {'domains': [], 'ssoConfigId': []}
            
            for row in data.get('result'):
                res['domains'].append(row.get("domain"))
                res['ssoConfigId'].append(row.get("ssoConfigId"))

                # print(row.get("domain"))
                # print(row.get("ssoConfigId"), "\n")
            return res
        
    """
   
    return None

def get_sso_config_id_by_domain_and_vendor_id(vendor_id: str, domain: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = check_in_all_dbs(func=fetching_sso_config_id_by_domain_and_vendor_id, vendor_id=vendor_id, domain=domain)
                
    else:
        db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_sso_config_id_by_domain_and_vendor_id(cursor=cursor, vendor_id=vendor_id, domain=domain)
        db.close()     
        
    if data:
        return data
    
    return None

def get_sso_configs_by_config_id(config_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = check_in_all_dbs(func=fetching_sso_configs_by_config_id, config_id=config_id)
                
    else:
        db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_sso_configs_by_config_id(cursor=cursor,  config_id=config_id)
        db.close()     
        
    if data:
        return data
    
    return None

def get_saml_groups_by_config_id(config_id: str, region: Optional[str] = None) -> Optional[Dict]:
    if not region:
        data = check_in_all_dbs(func=fetching_saml_groups_by_config_id, config_id=config_id)
        
    else:
        db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor()
        data = fetching_saml_groups_by_config_id(cursor=cursor,  config_id=config_id)
        db.close()     
        
    if data:
        return data
    
    return None




if __name__ == "__main__":
  
    db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_US', passwd=f'PASSWD_GENERAL_US')
    cursor = db.cursor()
    
    