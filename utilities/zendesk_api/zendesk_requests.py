
import os
from typing import Dict
import requests
import base64
from dotenv import load_dotenv

from consts import ZENDESK_USERS_FROM_TICKET_URL

from utilities.utils import is_domain_in_email, is_valid_email

load_dotenv('.env')

async def get_auth_header_from_zendesk_api(email: str, api_token: str) -> str:
    # Combine email/token and API token with a colon (:)
    credentials = f"{os.getenv(email)}/token:{os.getenv(api_token)}"

    # Encode credentials using base64
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    # Build the Authorization header
    return f"Basic {encoded_credentials}"
    
async def get_users_from_zd_ticket(auth_header: str, ticket_number: str) -> Dict[str,str]:
    url = ZENDESK_USERS_FROM_TICKET_URL.format(ticket_number)
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def get_ticket_emails_from_zd_dict(res_dict: Dict[str,str]) -> Dict[str,str]:
    emails_dict = {
        'Agent': [],
        'Customer': []
    }

    for user in res_dict.get('users'):
        
        if is_valid_email(email=user.get('email')):
            
            if is_domain_in_email(email=user.get('email'), domain='frontegg.com'):
                emails_dict['Agent'].append(user.get('email'))    
            else:
                emails_dict['Customer'].append(user.get('email'))
                
        else:
            print(f'Email is not valid {user.get("email", None)}')

    return emails_dict
