import os
import sys
import asyncio

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Add the project root directory to the Python path
sys.path.append(PROJECT_ROOT)

from flask import Flask, request, jsonify
from utilities.new_flows import *

import json
from flask_cors import CORS
# from utilities.handlers import check_customer_region, find_user_roles_in_db, get_all_data_by_vendor_id, get_saml_groups_by_config_id, get_sso_configs_by_config_id, get_domains_by_vendor_id, get_sso_config_id_by_domain_and_vendor_id, manage_vendor_id_from_email, manage_vendor_id_from_zendesk_ticket, remove_trial_process, get_account_id_by_vendor_id, get_vendors_ids_by_account_id
from utilities.utils import authenticate_as_vendor, get_production_env_variables, is_valid_email, is_valid_ticket_id, request_white_lable, validate_uuid

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes

@app.route('/find_customer_region', methods=['GET', 'POST'])
async def find_customer_region():
    if request.method == 'GET':
        return f'GET request is not available'
    
    elif request.method == 'POST':
        data = json.loads(request.data)
        selected_option = data.get('selectedOption', '')
        query_id = data.get('queryId', '')
       
        stripped_query_id = str(query_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_query_id)

        if is_valid and (len(selected_option) > 1):
            customer_region = await check_customer_region(id_type=selected_option, id=stripped_query_id)
            if customer_region:
                return jsonify(customer_region)
            
            return jsonify({'Error': 'An error occured'})

        return jsonify({'Error': 'Invalid ID!'})
                
    else:
        return jsonify({'Error': 'Method not allowed'})
    
@app.route('/remove_trial', methods=['GET', 'POST'])
async def remove_trial():
    if request.method == 'GET':
        return f'GET request is not available'
    
    elif request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', None)
        
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if is_valid:
            result = await remove_trial_process(vendor_id=stripped_vendor_id, region=region)
            
            if result:
                return jsonify(result)

        return jsonify({'Error': ['Invalid ID!', 'Wrong Region']})
    
    else:
        return jsonify({'Error': 'Method not allowed'})
    
@app.route('/user_roles_db', methods=['GET', 'POST'])
async def find_users_roles_db():
    if request.method == 'GET':
        data = json.loads(request.data)
        user_id = data.get('userId', '')
        tenant_id = data.get('tenantId', '')

        result = await find_user_roles_in_db(tenant_id=tenant_id, user_id=user_id)
        return jsonify(result)
    
    elif request.method == 'POST':
        return f'This is a POST request'
    
    else:
        return 'Method not allowed'

@app.route('/white_label', methods=['POST'])
async def white_label():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        is_enabled = data.get('isEnabled', '')
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)
        white_label_counter = 0

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
        
        if bool(is_enabled):
            production_client_id, production_secret = get_production_env_variables()

            auth_response = authenticate_as_vendor(
                production_client_id=production_client_id, 
                production_client_secret=production_secret
                )
        
            account_id = await get_account_id_by_vendor_id(vendor_id=stripped_vendor_id, region='EU')
            
            if account_id:
                env_ids = await get_vendors_ids_by_account_id(account_id=account_id, region='EU')            

            if env_ids:
                for id in env_ids:    

                    response = request_white_lable(
                        is_enabled=is_enabled, 
                        vendor_id=id, 
                        token=auth_response.get('token')
                        )
                    
                    if response.get('status_code') == 200:
                        white_label_counter += 1
                        
                return jsonify({'status_code': 200, 'number_of_envs': len(env_ids), 'white_labeled': white_label_counter})        
        
        return jsonify({'Error': 'You selected the body-param as disabled'})
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/validate_uuid', methods=['GET'])
def validate_uuid_from_ui():
    if request.method == 'GET':
        id = request.args.get('id')
        stripped_id = str(id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_id)
        
        if is_valid:
            return jsonify({"isValid": True})

        return jsonify({"isValid": False})
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_domains_by_vendor_id', methods=['POST'])
async def domains_by_vendor():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', None)
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
                
        vendor_domains = await get_domains_by_vendor_id(vendor_id=stripped_vendor_id, region=region)
            
        if vendor_domains:                    
            return jsonify(vendor_domains)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_sso_configs_id_by_domain_and_vendorid', methods=['POST'])
async def sso_config_id_by_domain_and_vendor_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        vendor_id = data.get('vendorId', '')
        domain = data.get('domain', '')
        region = data.get('region', None)
        
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
                
        sso_config_id_dict = await get_sso_config_id_by_domain_and_vendor_id(vendor_id=stripped_vendor_id, domain=domain, region=region)
            
        if sso_config_id_dict:                    
            return jsonify(sso_config_id_dict)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_sso_configs_by_domain_and_vendorid', methods=['POST'])
async def sso_configs_by_domain_and_vendor_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        vendor_id = data.get('vendorId', '')
        domain = data.get('domain', '')
        region = data.get('region', None)
        
        stripped_domain = str(domain).strip('\'"')
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
                
        sso_config_id_dict = await get_sso_config_id_by_domain_and_vendor_id(vendor_id=stripped_vendor_id, domain=stripped_domain, region=region)

        if sso_config_id_dict:    
            all_configs = []
            for configId in sso_config_id_dict.get('ssoConfigId'):
                sso_configs_dict = await get_sso_configs_by_config_id(config_id=configId, region=region)
                all_configs.append(sso_configs_dict)

            return all_configs
            
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_sso_configs_by_config_id', methods=['POST'])
async def sso_configs_by_config_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        config_id = data.get('configId', '')
        region = data.get('region', None)
        stripped_config_id = str(config_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_config_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
        
        sso_configs_dict = await get_sso_configs_by_config_id(config_id=stripped_config_id, region=region)
        
        if sso_configs_dict:                    
            return jsonify(sso_configs_dict)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_saml_groups_by_config_id', methods=['POST'])
async def saml_groups_by_config_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        config_id = data.get('configId', '')
        region = data.get('region', None)
        
        stripped_config_id = str(config_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_config_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
        
        saml_groups_dict = await get_saml_groups_by_config_id(config_id=stripped_config_id, region=region)

        if saml_groups_dict:                    
            return jsonify(saml_groups_dict)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_vendor_id_by_email', methods=['POST'])
async def vendor_id_by_email():
    # needs to check with guy why i do not have an access for users table in our DB
    if request.method == 'POST':
        data = json.loads(request.data)
        
        email_address = data.get('emailAddress', '')
        region = data.get('region', None)
        
        is_valid = is_valid_email(email=email_address)

        if not is_valid:
            return jsonify({'Error': 'Invalid email address'})
        
        vendor_id = await manage_vendor_id_from_email(email=email_address, region=region)
        
        asd = await get_all_data_by_vendor_id(vendor_id=vendor_id)
        print("\nASDASDASDASD\n\n", asd, "\n\n")
        return jsonify(asd)
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_vendor_id_by_ticket_id', methods=['POST'])
async def vendor_id_by_ticket_id():
    # needs to check with guy why i do not have an access for users table in our DB
    if request.method == 'POST':
        data = json.loads(request.data)
        
        ticket_number = data.get('ticketNumber', '')
        region = data.get('region', None)

        is_valid = is_valid_ticket_id(ticket_id=ticket_number)

        if not is_valid:
            return jsonify({'Error': 'Invalid ticket id'})
        
        vendor_id = await manage_vendor_id_from_zendesk_ticket(ticket_number=ticket_number, region=region)
        asd = await get_all_data_by_vendor_id(vendor_id=vendor_id)

        return jsonify(asd)
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_all_data_by_vendor_id', methods=['POST'])
async def get_data_by_vendor_id():
    # needs to check with guy why i do not have an access for users table in our DB
    if request.method == 'POST':
        data = json.loads(request.data)
        
        vendor_id = data.get('vendorId', '')
        region = data.get('region', None)

        is_valid = validate_uuid(uuid_string=vendor_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid vendor id'})
        
        data = await get_all_account_data_by_vendor_id(vendor_id=vendor_id, region=region)
        print(data)
        return data
    
    else:
        return jsonify({'Error': 'Method not allowed'})



if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()

    try:
        print("######### Without Region ############\n")
        # account = loop.run_until_complete(get_all_account_data_by_vendor_id("764e295e-7139-4a54-b871-b937eb8927d5"))
        # print("\naccount by vendor\n\n", account)
        # account = loop.run_until_complete(get_all_account_data_by_tenant_id("854df473-17a8-42f1-bdfa-d88d6c1bf1fc"))
        # print("\naccount by tenant\n\n", account)
        # account = loop.run_until_complete(get_all_account_data_by_user_email("noam.mishaeli@frontegg.com"))
        # print("\naccount by email\n\n", account)
        # account = loop.run_until_complete(get_all_account_data_by_zendesk_ticket_number("4346"))
        # print("\naccount by email\n\n", account)
        
        
        # print("######### Region ############\n")
        
        # account = loop.run_until_complete(get_all_account_data_by_vendor_id("764e295e-7139-4a54-b871-b937eb8927d5", region='EU'))
        # print("\naccount by vendor\n\n", account)
        # account = loop.run_until_complete(get_all_account_data_by_tenant_id("854df473-17a8-42f1-bdfa-d88d6c1bf1fc", region='EU'))
        # print("\naccount by tenant\n\n", account)
        # account = loop.run_until_complete(get_all_account_data_by_user_email("noam.mishaeli@frontegg.com", region='EU'))
        # print("\naccount by email\n\n", account)
        
        
        # should implement by ticket
        # implement validation for any id returned - make sure it is not a constant in our db and uuid instead
    finally:
        loop.close()
        
    