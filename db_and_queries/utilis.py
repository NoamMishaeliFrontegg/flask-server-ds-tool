from typing import Tuple
from .connections_and_queries import *
from dotenv import load_dotenv
from .consts import *
import requests
import os
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

    response = requests.request("PUT", url, headers=headers, json=payload)
    
    return {"status_code": response.status_code, "text": response.text}
