import os
import sys
import asyncio

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Add the project root directory to the Python path
sys.path.append(PROJECT_ROOT)

from flask import Flask, request, jsonify

import json
from flask_cors import CORS
from utilities.handlers import *
from utilities.utils import is_valid_email, is_valid_ticket_id, validate_uuid

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes


@app.route('/get_all_data_by_vendor_id', methods=['POST'])
async def get_data_by_vendor_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        vendor_id = data.get('vendorId', '')
        region = data.get('region', None)

        is_valid = validate_uuid(uuid_string=vendor_id)

        if not is_valid:
            return jsonify({'error': 'Invalid vendor id'})
        
        data = await get_all_account_data_by_vendor_id(vendor_id=vendor_id, region=region)

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})

@app.route('/get_all_data_by_tenant_id', methods=['POST'])
async def get_data_by_tenant_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        tenant_id = data.get('tenantId', '')
        region = data.get('region', None)

        is_valid = validate_uuid(uuid_string=tenant_id)

        if not is_valid:
            return jsonify({'error': 'Invalid tenant id'})
        
        data = await get_all_account_data_by_tenant_id(tenant_id=tenant_id, region=region)

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})
    
@app.route('/get_all_data_by_email', methods=['POST'])
async def get_data_by_email():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        email = data.get('emailAddress', '')
        region = data.get('region', None)
        is_valid = await is_valid_email(email=email)

        if not is_valid:
            return jsonify({'error': 'Invalid email address'})
        
        data = await get_all_account_data_by_user_email(user_email=email, region=region)

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})
    
@app.route('/get_all_data_by_ticket', methods=['POST'])
async def get_data_by_ticket():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        ticket = data.get('ticketNumber', '')

        is_valid = is_valid_ticket_id(ticket_id=ticket)

        if not is_valid:
            return jsonify({'error': 'Invalid ticket number'})
        
        data = await get_all_account_data_by_zendesk_ticket_number(ticket_number=ticket)

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})

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

        return jsonify({'error': ['Invalid ID!', 'Wrong Region']})
    
    else:
        return jsonify({'error': 'Method not allowed'})
    
@app.route('/white_label', methods=['POST'])
async def white_label():
    if request.method == 'POST':
        data = json.loads(request.data)

        vendor_id = data.get('vendorId', None)
        account_tenant_id = data.get('accountTenantId', None)
        is_enabled = data.get('isEnabled', '')
        region = data.get('region', '')
        
        data = await handle_white_label_process(
            vendor_id=vendor_id, 
            account_tenant_id=account_tenant_id, 
            is_enabled=is_enabled,
            region=region
            )
        
        return data
        # stripped_vendor_id = str(vendor_id).strip('\'"')
        # is_valid = validate_uuid(uuid_string=stripped_vendor_id)
        # white_label_counter = 0
        # white_label_vendors = []

        # if not is_valid:
        #     return jsonify({'error': 'Invalid ID'})
        
        # if bool(is_enabled):
        #     production_client_id, production_secret = get_production_env_variables()

        #     auth_response = authenticate_as_vendor(
        #         production_client_id=production_client_id, 
        #         production_client_secret=production_secret
        #         )
        
        #     account_id = await get_account_id_by_vendor_id(vendor_id=stripped_vendor_id, region=region)

        #     if account_id:
        #         env_ids = await get_vendors_ids_by_account_id(account_id=account_id, region=region)            

        #     if env_ids:
        #         for id in env_ids:    

        #             response = request_white_lable(
        #                 is_enabled=is_enabled, 
        #                 vendor_id=id, 
        #                 token=auth_response.get('token'),
        #                 region=region
        #                 )
                    
        #             if response.get('status_code') == 200:
        #                 print("\nMAIN\n", id)
        #                 is_vendor_white_label = await check_if_white_label(vendor_id=id, region=region)
                        
        #                 if is_vendor_white_label != 0:
        #                     white_label_counter += 1
        #                     white_label_vendors.append(id)
                                    
        #         return jsonify({'status_code': 200, 'number_of_envs': len(env_ids), 'white_labeled': white_label_counter, 'white_labeled_vendors': white_label_vendors})        
        
        # return jsonify({'error': 'You selected the body-param as disabled'})
    
    else:
        return jsonify({'error': 'Method not allowed'})


if __name__ == '__main__':
    
    # loop = asyncio.get_event_loop()
    print()

    # try:
    #     print("######### Without Region ############\n")
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
    # finally:
    #     loop.close()
        
    