import re

from .connections_and_queries import *
# from dotenv import load_dotenv
# from consts import *
import uuid

@log_execution_time    
async def validate_uuid(uuid_string: str) -> bool:
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

@log_execution_time
async def is_valid_email(email: str) -> bool:
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
 