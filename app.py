import os
import sys

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Add the project root directory to the Python path
sys.path.append(PROJECT_ROOT)

from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from db_and_queries.handlers import check_customer_region, find_user_roles_in_db, remove_trial_process, get_account_id_by_vendor_id, get_environments_ids_by_account_id
from db_and_queries.utilis import authenticate_as_vendor, get_production_env_variables, request_white_lable, validate_uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/find_customer_region', methods=['GET', 'POST'])
def find_customer_region():
    if request.method == 'GET':
        return f'GET request is not available'
    
    elif request.method == 'POST':
        data = json.loads(request.data)
        selected_option = data.get('selectedOption', '')
        query_id = data.get('queryId', '')
        
        stripped_query_id = str(query_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_query_id)
        
        if is_valid and (len(selected_option) > 1):
            customer_region = check_customer_region(id_type=selected_option, id=stripped_query_id)
            
            if customer_region:
                return jsonify(customer_region)
            
            return jsonify({'Error': 'An error occured'})

        return jsonify({'Error': 'Invalid ID!'})
                
    else:
        return jsonify({'Error': 'Method not allowed'})
    
@app.route('/remove_trial', methods=['GET', 'POST'])
def remove_trial():
    if request.method == 'GET':
        return f'GET request is not available'
    
    elif request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', None)
        
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if is_valid:
            result = remove_trial_process(vendor_id=stripped_vendor_id, region=region)
            
            if result:
                return jsonify(result)

        return jsonify({'Error': ['Invalid ID!', 'Wrong Region']})
    
    else:
        return jsonify({'Error': 'Method not allowed'})
    
@app.route('/user_roles_db', methods=['GET', 'POST'])
def find_users_roles_db():
    if request.method == 'GET':
        data = json.loads(request.data)
        user_id = data.get('userId', '')
        tenant_id = data.get('tenantId', '')

        result = find_user_roles_in_db(tenant_id=tenant_id, user_id=user_id)
        return jsonify(result)
    
    elif request.method == 'POST':
        return f'This is a POST request'
    
    else:
        return 'Method not allowed'

@app.route('/white_label', methods=['POST'])
def white_label():
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
        
            account_id = get_account_id_by_vendor_id(vendor_id=stripped_vendor_id, region='EU')
            
            if account_id:
                env_ids = get_environments_ids_by_account_id(account_id=account_id, region='EU')            

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
    
if __name__ == '__main__':
    # asdasd = check_customer_region(id_type='vendor', id='d058e199-6ed3-4049-8034-447bbd5004e9')
    # print('main:check_customer_region2:   ', asdasd)
    print("asd")