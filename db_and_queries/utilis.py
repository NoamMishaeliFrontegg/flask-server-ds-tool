from typing import Any, Dict, List, Optional, Tuple, Union
from db_and_queries.connection_and_mgmt import *
from dotenv import load_dotenv
from consts import *
import requests
import os
import mysql.connector
import uuid

def validate_uuid(uuid_string: str) -> bool:
    if not uuid_string:
        return False  # Return False if no ID is provided
    
    try:
        uuid_obj = uuid.UUID(uuid_string, version=4)
        is_valid = str(uuid_obj) == uuid_string
    except ValueError:
        is_valid = False    
    
    return is_valid

def fetching_tenant_dict_from_db(cursor: mysql.connector.cursor_cext.CMySQLCursor, client_id: str) -> Dict[str,str]:
    vendor_query_result = fetch_one_query(cursor=cursor, query=GET_VENDOR_BY_ID_QUERY.format(f"'{client_id}'"))
    if vendor_query_result:
        vendor_dict_response = parse_response(cursor=cursor, result_to_parse=vendor_query_result)
        
    if vendor_dict_response:
        account_query_result = fetch_one_query(cursor=cursor, query=GET_TENANT_BY_ID_QUERY.format(f"'{vendor_dict_response.get('accountId')}'"))
        
    if account_query_result:
        account_dict_response = parse_response(cursor=cursor, result_to_parse=account_query_result)

    if account_dict_response:
        tenant_query_result = fetch_one_query(cursor=cursor, query=GET_TENANT_CONFIGURATIONS_QUERY.format(f"'{account_dict_response.get('accountTenantId')}'"))

    if tenant_query_result:
        tenant_dict_response = parse_response(cursor=cursor, result_to_parse=tenant_query_result)
            
    if tenant_dict_response:    
        return { "id": tenant_dict_response.get("id"), "tenant_id": tenant_dict_response.get("tenantId")}
    
    return {}

def authenticate_as_vendor(production_client_id: str, production_client_secret: str):
    url = "https://api.frontegg.com/auth/vendor/"
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    data = {
        "clientId": production_client_id,
        "secret": production_client_secret
    }
    response = requests.post(url, headers=headers, json=data)

    return response.json()

def remove_trial_request(tenant_id, id, production_vendor_token):
    url = BASE_PATH + SUBSCRIPTION_CONFIGURATION + tenant_id
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {production_vendor_token}"
    }
    payload = {
        "providerType": "Stripe",
        "externallyManaged": "prod_M81QRPpLeQ8Sea",
        "configurationId": id   
    }
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code

def get_production_env_variables() -> Tuple[str,str]:    
    load_dotenv()
    production_client_id = os.getenv("PRODUCTION_CLIENT_ID")
    production_secret = os.getenv("PRODUCTION_SECRET")
    
    return production_client_id, production_secret

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

def request_white_lable(is_enabled: bool, vendor_id: str, token: str) -> Tuple[str,str]:
    url = "https://api.frontegg.com/vendors/whitelabel-mode"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    payload = {
        "vendorId": vendor_id,
        "enabled": is_enabled
    }   

    response = requests.request("GET", url, headers=headers, json=payload)
    
    return {"status_code": response.status_code, "text": response.text}