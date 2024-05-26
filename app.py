import os
import sys

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Add the project root directory to the Python path
sys.path.append(PROJECT_ROOT)

from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from zendesk_api.zendesk_requests import get_auth_header_from_zendesk_api, get_ticket_emails_from_zd_dict, get_users_from_zd_ticket
from db_and_queries.handlers import check_customer_region, find_user_roles_in_db, get_saml_groups_by_config_id, get_sso_configs_by_config_id, get_domains_by_vendor_id, get_sso_config_id_by_domain_and_vendor_id, remove_trial_process, get_account_id_by_vendor_id, get_environments_ids_by_account_id
from db_and_queries.utilis import authenticate_as_vendor, get_production_env_variables, is_valid_email, request_white_lable, validate_uuid

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
            print(selected_option, "\n",query_id,"\n",is_valid)
            customer_region = check_customer_region(id_type=selected_option, id=stripped_query_id)
            print(customer_region)
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

@app.route('/get_domains_by_vendor_id', methods=['POST'])
def domains_by_vendor():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', None)
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
                
        vendor_domains = get_domains_by_vendor_id(vendor_id=stripped_vendor_id, region=region)
            
        if vendor_domains:                    
            return jsonify(vendor_domains)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_sso_configs_id_by_domain_and_vendorid', methods=['POST'])
def sso_config_id_by_domain_and_vendor_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        vendor_id = data.get('vendorId', '')
        domain = data.get('domain', '')
        region = data.get('region', None)
        
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
                
        sso_config_id_dict = get_sso_config_id_by_domain_and_vendor_id(vendor_id=stripped_vendor_id, domain=domain, region=region)
            
        if sso_config_id_dict:                    
            return jsonify(sso_config_id_dict)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_sso_configs_by_domain_and_vendorid', methods=['POST'])
def sso_configs_by_domain_and_vendor_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        vendor_id = data.get('vendorId', '')
        domain = data.get('domain', '')
        region = data.get('region', None)
        
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
                
        sso_config_id_dict = get_sso_config_id_by_domain_and_vendor_id(vendor_id=stripped_vendor_id, domain=domain, region=region)
        
        if sso_config_id_dict:    
            all_configs = []               
            config_ids = sso_config_id_dict.get("domain")
            for row in config_ids:
                sso_configs_dict = get_sso_configs_by_config_id(config_id=row.get("ssoConfigId"), region=region)
                print(sso_configs_dict)
                all_configs.append(sso_configs_dict)
            return all_configs
            
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_sso_configs_by_config_id', methods=['POST'])
def sso_configs_by_config_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        config_id = data.get('configId', '')
        region = data.get('region', None)
        stripped_config_id = str(config_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_config_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
        
        sso_configs_dict = get_sso_configs_by_config_id(config_id=stripped_config_id, region=region)
        print(sso_configs_dict)
        
        if sso_configs_dict:                    
            return jsonify(sso_configs_dict)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_saml_groups_by_config_id', methods=['POST'])
def saml_groups_by_config_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        config_id = data.get('configId', '')
        region = data.get('region', None)
        
        stripped_config_id = str(config_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_config_id)

        if not is_valid:
            return jsonify({'Error': 'Invalid ID'})
        
        saml_groups_dict = get_saml_groups_by_config_id(config_id=stripped_config_id, region=region)
        print(saml_groups_dict)
        if saml_groups_dict:                    
            return jsonify(saml_groups_dict)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})

@app.route('/get_vendor_id_by_email', methods=['POST'])
def vendor_id_by_email():
    # needs to check with guy why i do not have an access for users table in our DB
    if request.method == 'POST':
        data = json.loads(request.data)
        
        email_address = data.get('emailAddress', '')
        region = data.get('region', None)
        
        is_valid = is_valid_email(email=email_address)

        if not is_valid:
            return jsonify({'Error': 'Invalid email address'})
        
        return {}
        # vendor = get_saml_groups_by_config_id(config_id=config_id, region=region)
            
        # if saml_groups_dict:                    
        #     return jsonify(saml_groups_dict)        
    
    else:
        return jsonify({'Error': 'Method not allowed'})


if __name__ == '__main__':
    # asdasd = check_customer_region(id_type='vendor', id='d058e199-6ed3-4049-8034-447bbd5004e9')
    # print('main:check_customer_region2:   ', asdasd)
    # asd = get_domains_by_vendor_id(vendor_id='04017595-4e5d-4e7e-aff6-93c58d489d2f', region=None)
    # asdd = get_domains_by_vendor_id(vendor_id='04017595-4e5d-4e7e-aff6-93c58d489d2f', region='EU')


    # asd = get_sso_config_id_by_domain_and_vendor_id(vendor_id='04017595-4e5d-4e7e-aff6-93c58d489d2f', region='EU', domain='roy.com')
    # sso_configs_dict = get_sso_configs_by_config_id(config_id='3324edff-8944-4363-98cd-849ef0bfd69c', region=None)
    # sso_configs_dict = get_saml_groups_by_config_id(config_id='3324edff-8944-4363-98cd-849ef0bfd69c', region=None)
    # sso_config_id_dict = get_sso_config_id_by_domain_and_vendor_id(vendor_id='04017595-4e5d-4e7e-aff6-93c58d489d2f', region='EU', domain='roy.com')
    # sso_config_id_dict = sso_configs_by_domain_and_vendor_id(vendor_id='04017595-4e5d-4e7e-aff6-93c58d489d2f', region='EU', domain='roy.com')


    # sso_config_id_dict = get_sso_config_id_by_domain_and_vendor_id(vendor_id='04017595-4e5d-4e7e-aff6-93c58d489d2f', region='EU', domain='roy.com')
    
    # if sso_config_id_dict:    
    #     all_configs = []               
    #     config_ids = sso_config_id_dict.get("domain")
    #     for row in config_ids:
    #         sso_configs_dict = get_sso_configs_by_config_id(config_id=row.get("ssoConfigId"), region='EU')
    #         all_configs.append(sso_configs_dict)

    #     print(all_configs)

    # if sso_config_id_dict:    
    #     all_configs = []               
    #     config_ids = sso_config_id_dict.get("result")
    #     for row in config_ids:
    #         sso_configs_dict = get_sso_configs_by_config_id(config_id=row.get("ssoConfigId"), region='EU')
    #         all_configs.append(sso_configs_dict)
    
    # print(all_configs)
            
    # res = asd.get("result")
    # for r in res:
    #     print(r.get("ssoConfigId"))
        # print(r.get("domain"))
        # print(r.get("ssoConfigId"), "\n")
        
    # print(sso_configs_dict)

    # auth_header = get_auth_header_from_zendesk_api(email='noam.mishaeli@frontegg.com', api_token='ZENDESK_API_TOKEN')
    # res_dict = get_users_from_zd_ticket(auth_header=auth_header, ticket_number='4224')
    # emails = get_ticket_emails_from_zd_dict(res_dict=res_dict)

    print("asdasd")
