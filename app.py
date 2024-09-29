import os
import sys



# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Add the project root directory to the Python path
sys.path.append(PROJECT_ROOT)

from flask import Flask, request, jsonify
from consts import *

import json
from flask_cors import CORS
from utilities.utils import is_valid_email, validate_uuid
from utilities.logger_config import logger, log_execution_time
from utilities.connections_and_queries import check_in_all_dbs, fetch_all_query, fetch_data_from_region, fetch_one_query

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes

########################### Page 1 ################################    
@app.route('/get_regions_by_email', methods=['POST'])
async def get_regions_by_email():
    if request.method == 'POST':
        data = json.loads(request.data)
        email = data.get('emailAddress', '')
        is_valid = await is_valid_email(email=email)

        if not is_valid:
            return jsonify({'error': 'Invalid email address'})
        
        data = await check_in_all_dbs(func=fetch_all_query,query=CHECK_IF_EMAIL_EXISTS_IN_REGION.format(f"'{email}'", f"'{os.getenv('PROD_VENDOR_ID')}'"), db_type=IDENTITY)
        logger.info('finished checking regions for user')

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})   

###################################################################
########################### Page 2 ################################    

@app.route('/get_vendors_by_account_tenant_id', methods=['POST'])
async def get_vendors_by_account_tenant_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        account_tenant_id = data.get('accountTenantId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=account_tenant_id)

        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_VENDORS_IDS_BY_ACCOUNT_TENANT_ID.format(f"'{account_tenant_id}'"), db_type=GENERAL)
        logger.info('finished fetching vendors by account tenant id')

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})   

###################################################################
########################### Page 3 ################################    
# need to get vendor's data for each vendor after a click on the desired vendor

# builder configs -> fetch configs
@app.route('/get_builder_configurations', methods=['POST'])
async def get_builder_conf():
    if request.method == 'POST':
        data = json.loads(request.data)
        account_id = data.get('accountTenantId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=account_id)

        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_BUILDER_CONFIGURATIONS.format(f"'{account_id}'"), db_type=GENERAL)
        logger.info('finished fetching builder configurations')
        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})   

# applications button -> fetch applications data 
@app.route('/get_applications', methods=['POST'])
async def get_applications():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=vendor_id)

        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_VENDOR_APPLICATIONS.format(f"'{vendor_id}'"), db_type=GENERAL)
        logger.info(f'finished fetching applications for {vendor_id}')

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})  
    
# application button -> fetch tenants of an applications
@app.route('/get_tenants_application', methods=['POST'])
async def get_tenants_application():
    if request.method == 'POST':
        data = json.loads(request.data)
        app_id = data.get('appId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=app_id)
        
        logger.info(f'start fetching tenants of application {app_id} in {region}')

        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_TENANTS_OF_APPLICATIONS.format(f"'{app_id}'"), db_type=GENERAL)
        logger.info(f'finished fetching tenants of application {app_id}')

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})   
    
# fetch tenants
@app.route('/get_tenants', methods=['POST'])
async def get_tenants():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=vendor_id)
        
        print(vendor_id, "\t", region)
        
        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_TENTANS_OF_VENDOR.format(f"'{vendor_id}'"), db_type=GENERAL)
        logger.info(f'finished fetching tenants under vendor {vendor_id}')
        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})   
    
# fetch custom domain
@app.route('/get_custom_domain', methods=['POST'])
async def get_custom_domain():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=vendor_id)
        
        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_CUSTOM_DOMAIN.format(f"'{vendor_id}'"), db_type=GENERAL)
        logger.info(f'finished fetching custom domain for vendor {vendor_id}')
        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})  

# fetch allowed origins
@app.route('/get_allowed_origins', methods=['POST'])
async def get_allowed_originss():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=vendor_id)
    
        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_ALLOWED_ORIGINS.format(f"'{vendor_id}'"), db_type=GENERAL)
        logger.info(f'finished fetching allowed origins for vendor {vendor_id}')
        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})  

# fetch impersonation settings
@app.route('/get_impresonation_settings', methods=['POST'])
async def get_impresonation_settings():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=vendor_id)
    
        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_IMPERSONATION_SETTINGS.format(f"'{vendor_id}'"), db_type=IDENTITY)
        logger.info(f'finished fetching impersonation settings for vendor {vendor_id}')
        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})  

# fetch impersonation settings
@app.route('/get_tenants_groups', methods=['POST'])
async def get_tenants_groups():
    if request.method == 'POST':
        data = json.loads(request.data)
        tenant_id = data.get('tenantId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=tenant_id)
    
        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_GROUPS.format(f"'{tenant_id}'"), db_type=IDENTITY)
        logger.info(f'finished fetching groups for tenant {tenant_id}')
            
        if not data:
            return jsonify({'error': 'groups were not found'})
            # return {}

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})  

#fetch SSO configs
@app.route('/get_sso_configs', methods=['POST'])
async def get_sso_configs():
    if request.method == 'POST':
        data = json.loads(request.data)
        tenant_id = data.get('tenantId', '')
        region = data.get('region', '')
        is_valid = await validate_uuid(uuid_string=tenant_id)
    
        if not is_valid or not region:
            return jsonify({'error': 'Invalid request'})
        
        data = await fetch_data_from_region(func=fetch_all_query,region=region, query=GET_SSO_CONFIGS.format(f"'{tenant_id}'"), db_type=GENERAL)
        logger.info(f'finished fetching groups for tenant {tenant_id}')
        
        if not data:
            return jsonify({'error': 'sso configs were not found'})
            # return {}

        return data
    
    else:
        return jsonify({'error': 'Method not allowed'})  

