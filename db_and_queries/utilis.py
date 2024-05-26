import re
from typing import Tuple
from .connections_and_queries import *
from dotenv import load_dotenv
from .consts import *
import requests
import os
import uuid

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
    """
    Sends a PUT request to the FrontEgg API to remove a trial request for a specific tenant and configuration ID.

    Args:
        tenant_id (str): The ID of the tenant for which the trial request should be removed.
        id (str): The configuration ID for which the trial request should be removed.
        production_vendor_token (str): The authentication token for the vendor.

    Returns:
        int: The HTTP status code of the API response.
    """
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
    """
    Retrieves the production client ID and secret from environment variables.

    Returns:
        Tuple[str, str]: A tuple containing the production client ID (first element) and the production secret (second element).
    """
    load_dotenv()
    production_client_id = os.getenv("PRODUCTION_CLIENT_ID")
    production_secret = os.getenv("PRODUCTION_SECRET")
    
    return production_client_id, production_secret

def request_white_lable(is_enabled: bool, vendor_id: str, token: str) -> Tuple[str,str]:
    """
    Sends a PUT request to the FrontEgg API to enable or disable the white-label mode for a specific vendor.

    Args:
        is_enabled (bool): A boolean indicating whether the white-label mode should be enabled or disabled.
        vendor_id (str): The ID of the vendor for which the white-label mode should be updated.
        token (str): The authentication token for the vendor.

    Returns:
        Tuple[str, str]: A tuple containing the HTTP status code (first element) and the response text (second element) from the API.
    """
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

def is_valid_email(email: str) -> bool:
    """
    Validate the given email address using regular expressions.

    Args:
        email (str): The email address to be validated.

    Returns:
        bool: True if the email address is valid, False otherwise.
    """
    # Regular expression pattern for email validation
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    # Check if the email matches the pattern
    if re.match(email_regex, email):
        return True
    else:
        return False
    
def is_domain_in_email(email: str, domain: str) -> bool:
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