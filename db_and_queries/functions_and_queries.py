from typing import Optional, Tuple
from consts import *
from db_and_queries.connection_and_mgmt import *
from enum import Enum
from collections import OrderedDict
from db_and_queries.utilis import *

class QueryEnum(Enum):
    tenant = GET_ACCOUNT_BY_ID_QUERY
    vendor = GET_VENDOR_BY_ID_QUERY
    # user = GET_USER_BY_ID_QUERY

# check in which DB the user is in
def check_customer_region(id_type: str, id: str) -> Optional[Dict]:    
    regions = ['EU', 'US']
    members = QueryEnum.__members__
    
    for region in regions:
        db = connect_to_db(user_name='USER_NAME', host=f'HOST_GENERAL_{region}', passwd=f'PASSWD_GENERAL_{region}')
        cursor = db.cursor(buffered=True)
        
        result = fetch_one_query(cursor=cursor, query=members[id_type].value.format(f"'{id}'"))
        print("\n\n",result, "\n\n")
        if result:
            parsed_result = parse_response(cursor=cursor, result_to_parse=result)
            data = OrderedDict({'region': region, **parsed_result})
            db.close()
        
            return dict(data)
        
    return None

def remove_trial_process(vendor_id: str) -> Optional[Dict]:
    
    db = connect_to_db(user_name='USER_NAME', host='HOST_GENERAL_EU', passwd='PASSWD_GENERAL_EU')
    cursor = db.cursor()

    data = fetching_tenant_dict_from_db(cursor=cursor, client_id=vendor_id)
    production_client_id, production_secret = get_production_env_variables()
    auth_response = authenticate_as_vendor(production_client_id=production_client_id, production_client_secret=production_secret)

    result = remove_trial_request(tenant_id=data.get('tenant_id'), id=data.get('id'), production_vendor_token=auth_response.get('token'))

    # Disconnecting from the server
    db.close()     
        
    return result

def find_user_roles_in_db(user_id: str, tenant_id: str) -> Optional[Dict]:
    
    db = connect_to_db(user_name='USER_NAME', host='HOST_IDENTITY_EU', passwd='PASSWD_IDENTITY_EU')
    cursor = db.cursor(buffered=True)

    roles = find_user_role(cursor=cursor, user_id=user_id, tenant_id=tenant_id)
    
    db.close()
    return roles

def generic_query(query: str, cursor: mysql.connector.cursor_cext.CMySQLCursor) -> Optional[str]:    
    try:
        result = fetch_one_query(cursor=cursor, query=query)
        
        if result:
            parsed_result = parse_response(cursor=cursor, result_to_parse=result)
            return parsed_result

    except mysql.connector.Error as e:
        error_message = f"Error occurred: {e}"
        return error_message

    except Exception as e:
        # Handle any other unexpected exceptions
        error_message = f"An unexpected error occurred: {e}"
        return error_message
              

if __name__ == "__main__":
  search_tenant = check_customer_region(id_type='tenant', id='eb399604-647b-4a8a-9098-12185cef964d')
  print('\n', search_tenant)
  
  search_vendor = check_customer_region(id_type='vendor', id='d058e199-6ed3-4049-8034-447bbd5004e9')
  print('\n', search_vendor)
  