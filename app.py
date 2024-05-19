from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from db_and_queries.functions_and_queries import check_customer_region, find_user_roles_in_db, remove_trial_process
from db_and_queries.utilis import validate_uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/find_customer_region', methods=['GET', 'POST'])
def find_customer_region():
    if request.method == 'GET':
        return f'This is a GET request'
    
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
            
            return jsonify({'result': 'An error occured'})

        return jsonify({'result': 'Invalid ID!'})
                
    else:
        return 'Method not allowed'
    
@app.route('/remove_trial', methods=['GET', 'POST'])
def remove_trial():
    if request.method == 'GET':
        print("asd")
        return f'This is a GET request'
    
    elif request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        stripped_vendor_id = str(vendor_id).strip('\'"')
        is_valid = validate_uuid(uuid_string=stripped_vendor_id)

        if is_valid:
            result = remove_trial_process(vendor_id=stripped_vendor_id)
            
            if result:
                return jsonify(result)

        return jsonify({'result': 'Invalid ID!'})
    
    else:
        return 'Method not allowed'
    
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
    
    
if __name__ == '__main__':
    app.run(debug=True)
