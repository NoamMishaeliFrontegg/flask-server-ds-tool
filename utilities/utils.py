from enum import Enum
import re
from typing import Tuple

from .db_and_queries.connections_and_queries import *
from dotenv import load_dotenv
from consts import *
import requests
import os
import uuid

class BaseUrl(Enum):
    eu = BASE_EU_PATH
    us = BASE_US_PATH
    ca = BASE_CA_PATH
    au = BASE_AU_PATH
    
def validate_uuid(uuid_string: str) -> bool:
    """
    Validates whether the given string is a valid UUID (Universally Unique Identifier) version 4.

    Args:
        uuid_string (str): The string representing the UUID to be validated.

    Returns:
        bool: True if the input string is a valid UUID version 4, False otherwise.
    """
    if not uuid_string:
        return False  # Return False if no ID is provided
    
    try:
        uuid_obj = uuid.UUID(uuid_string, version=4)
        is_valid = str(uuid_obj) == uuid_string
    except ValueError:
        is_valid = False    
    
    return is_valid

def authenticate_as_vendor(production_client_id: str, production_client_secret: str):
    """
    Authenticates with the FrontEgg API as a vendor using the provided production client ID and secret.

    Args:
        production_client_id (str): The production client ID for authentication.
        production_client_secret (str): The production client secret for authentication.

    Returns:
        The function returns the JSON response from the authentication API.
    """
    url = BASE_EU_PATH + FRONTEGG_AUTH_AS_VENDOR
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
    """
    Sends a PUT request to the FrontEgg API to remove a trial request for a specific tenant and configuration ID.

    Args:
        tenant_id (str): The ID of the tenant for which the trial request should be removed.
        id (str): The configuration ID for which the trial request should be removed.
        production_vendor_token (str): The authentication token for the vendor.

    Returns:
        int: The HTTP status code of the API response.
    """
    url = BASE_EU_PATH + SUBSCRIPTION_CONFIGURATION + tenant_id
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
    """
    Retrieves the production client ID and secret from environment variables.

    Returns:
        Tuple[str, str]: A tuple containing the production client ID (first element) and the production secret (second element).
    """
    load_dotenv()
    production_client_id = os.getenv("PRODUCTION_CLIENT_ID")
    production_secret = os.getenv("PRODUCTION_SECRET")
    
    return production_client_id, production_secret

def request_white_lable(is_enabled: bool, vendor_id: str, token: str, region: str = 'EU') -> Tuple[str,str]:
    """
    Sends a PUT request to the FrontEgg API to enable or disable the white-label mode for a specific vendor.

    Args:
        is_enabled (bool): A boolean indicating whether the white-label mode should be enabled or disabled.
        vendor_id (str): The ID of the vendor for which the white-label mode should be updated.
        token (str): The authentication token for the vendor.

    Returns:
        Tuple[str, str]: A tuple containing the HTTP status code (first element) and the response text (second element) from the API.
    """

    url =  BaseUrl.__members__[region.lower()].value + FRONTEGG_WHITE_LABEL 
        
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

async def is_valid_email(email: str) -> bool:
    """
    Validate the given email address using regular expressions.

    Args:
        email (str): The email address to be validated.

    Returns:
        bool: True if the email address is valid, False otherwise.
    """
    # Regular expression pattern for email validation
    email_regex = "^([^\s@]+@[^\s@]+\.[^\s@]+)$"
    # Check if the email matches the pattern
    if re.match(email_regex, email):
        return True
    else:
        return False
    
def is_valid_ticket_id(ticket_id: str) -> bool:
    """
    Validate the given ticket id using regular expressions.

    Args:
        ticket (str): The ticket id to be validated.

    Returns:
        bool: True if the ticket id is valid, False otherwise.
    """
    # Regular expression pattern for email validation
    ticket_regex = r'^\d{4}$'

    # Check if the email matches the pattern
    if re.match(ticket_regex, ticket_id):
        return True
    else:
        return False

async def is_domain_in_email(email: str, domain: str) -> bool:
    """
    Checks if the given domain is present in the email address.

    Args:
        email (str): The email address to be checked.
        domain (str): The domain name to search for.

    Returns:
        bool: True if the domain is present in the email address, False otherwise.
    """
    # Extract the domain part from the email address
    email_domain = email.split('@')[-1]

    # Check if the given domain is present in the email domain (case-insensitive)
    if email_domain.lower() == domain.lower():
        return True
    else:
        return False
    
def object_to_dict(obj, exclude_keys=None) -> Dict[str,str]:
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
        return {k: object_to_dict(v, exclude_keys) for k, v in obj.items() if k not in exclude_keys}
    elif isinstance(obj, (list, tuple, set)):
        return [object_to_dict(item, exclude_keys) for item in obj]
    elif hasattr(obj, "__dict__"):
        obj_dict = {k: object_to_dict(v, exclude_keys) for k, v in obj.__dict__.items() if k not in exclude_keys}
        return obj_dict
    else:
        return obj
