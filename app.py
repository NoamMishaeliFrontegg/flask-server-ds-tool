import os
import sys
import asyncio

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Add the project root directory to the Python path
sys.path.append(PROJECT_ROOT)

from flask import Flask, request, jsonify
from utilities.logger_config import logger, log_execution_time

import json
from flask_cors import CORS
from utilities.handlers import *
from utilities.utils import is_valid_email, is_valid_ticket_id, validate_uuid

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes


@app.route('/get_all_data_by_vendor_id', methods=['POST'])
@log_execution_time
async def get_data_by_vendor_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        vendor_id = data.get('vendorId', '')
        region = data.get('region', None)
        
        is_valid = validate_uuid(uuid_string=vendor_id)

        if not is_valid:
            return jsonify({'error': 'Invalid vendor id'})
        
        data = await get_all_account_data_by_vendor_id(vendor_id=vendor_id, region=region)
        logger.info('finished fetching account data by vendor id')

        return data
    
    else:
        logger.error('request\'s method not allowed')
        return jsonify({'error': 'Method not allowed'})

@app.route('/get_all_data_by_tenant_id', methods=['POST'])
async def get_data_by_tenant_id():
    if request.method == 'POST':
        data = json.loads(request.data)
        
        tenant_id = data.get('tenantId', '')
        region = data.get('region', None)
        
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
    
    loop = asyncio.get_event_loop()

    vendors_list1 = [
    "0077ce24-c055-421b-ad67-c856ecf0a4a4",
    "02f12e7f-321b-4e3a-afbc-585052bf7ad7",
    "0331a77a-d6e2-43f6-a0a9-5cdeb20f8f86",
    "06b06a71-b512-4fbb-9ff9-3101a0880f20",
    "071ca3a4-aa15-464f-9eed-5e90078658b3",
    "078b70a4-8825-4651-9639-ef242dff6269",
    "07defd9f-3162-4798-af80-24da5740ac53",
    "0932b880-9ad3-4067-ba10-2157269306bd",
    "09c6b1a1-7cd2-4041-a5a9-f4c04af1d871",
    "0c58398e-28a3-4915-8e10-6ee702717b68",
    "0cea5c8d-25aa-4f7c-bdcc-fc30cb299b37",
    "0e7a38d2-0537-498d-8669-c015b618af21",
    "11825cce-b54c-4921-91bc-a6e66629a381",
    "12494da2-ad7f-49da-8d1d-09676b820f55",
    "12c929e3-a2fc-4370-a6dc-3a7a7d3af22e",
    "16335d66-52f9-40fa-a21d-618ebd597354",
    "16acffa3-87a4-4fa3-b426-9063b8c477a3",
    "16ae8b90-bfca-4c5a-8713-d396dc880fa6",
    "1700c1a0-a936-4e33-a1c8-09f8ed463e53",
    "1797e7db-138f-403c-96ef-7fb81b5f13e6",
    "1876aa65-aaef-48c4-8e05-bd4525a54ba5",
    "1896e252-26a4-4289-af60-45abf9276a1d",
    "198e817c-d540-43f4-a5f5-895ac873c4e4",
    "1b3608ed-9a9e-487e-bc05-e1285570694e",
    "1c4684d2-92c5-4338-8af8-860fe1c58409",
    "1c7a1e4d-ec86-462b-a6df-9d9c39515825",
    "1cc8757d-90ee-40fa-807a-af0020848577",
    "1d973360-6d17-4a3a-bd7e-c04f924d9bc3",
    "1e1683fd-0536-4d83-9c44-b11c10dbe079",
    "1eb7b186-83a7-427b-bfd2-0e5ad0957f01",
    "1edb919d-754f-44cd-8816-e918c4ee59be",
    "2084fcc9-c14c-4be3-9e87-e0fd1b78f23d",
    "21ac11fb-aa07-478a-8d08-add174be0d01",
    "22e305f3-2460-4f88-88e8-bf613df6a1dd",
    "231b369e-3581-442f-aa68-2a140c2bd1c6",
    "294c23d2-bd65-4e97-868c-61be009b3173",
    "2a21d520-ee71-4809-9350-7bc2b6bb6d5f",
    "2b5988b6-bcc3-451a-b90a-647e0612c13d",
    "2dc06386-73ff-4938-96e3-5725f6ffa463",
    "33c03b68-70ac-4371-b1b3-faf2af1638ca",
    "3558fc6b-f927-4228-a710-d36d2cffe362",
    "35cb92aa-b044-4a51-bacb-9e48694d3090",
    "37c87daf-c976-46f9-9520-48ea88c48dee",
    "397362e0-7cb1-42a6-a833-22b13d314ed0",
    "3ab22ad7-b281-4987-ba29-7f7925af877d",
    "3c736ee3-d8e7-435b-9d35-77c0e98062a9",
    "3eb73682-483b-40c8-8c69-5019e7cb1795",
    "3f5f4b49-9758-4a5d-a841-eda25502846b",
    "4061b4fd-bece-4971-9e9b-6ae7733f2aaf",
    "409861ac-e7ef-4b4e-9319-5f8f7d93e0e3",
    "418c7fac-07e6-4942-b28b-7f5a264f0599",
    "43738c33-bcfd-499d-84a3-7a09e11cebb2",
    "4691d2c4-d8c3-46f9-be65-99c385b9e2cc",
    "487f1654-91db-4d00-9aeb-cd44df859399",
    "4ac19828-9362-46c8-a0ec-3a3e77b011c8",
    "4baa2f0c-c2e5-495c-9766-819df1e827cd",
    "4d16edaa-abe5-4f9b-a298-45699e1a2d9b",
    "50440671-7472-4c72-a3b9-7623d3798903",
    "51e33e71-841f-4bde-be26-b1e9586d9f18",
    "5384938d-c45e-4b76-95cc-b328756e548b",
    "539fc712-987a-461f-a22e-2a6c927e379c",
    "54a17d56-c354-4f1b-9279-3e9b941b6af5",
    "559679b5-d35f-4fbc-92c9-2f624ace042c",
    "55dde133-5850-4f21-843f-0441b000f302",
    "56135d3f-70c3-492b-97b8-ca7b40ff0955",
    "58822d2e-e000-464d-bba1-7572fd389514",
    "58ebbf27-dae5-4131-829e-f8dbdbb680f8",
    "59136b8a-7ccf-4bf2-9560-5aadb52255bb",
    "5a2be81c-eb76-4f6b-8665-8c24c696f7e7",
    "5c67c8b4-b39f-43ab-a14b-9da49b61471a",
    "5e1c2ed4-0d67-4561-8460-4fb10ac3f5e4",
    "61f0601f-932a-489e-8216-0bda0232bb71",
    "62869637-3816-4b72-8316-8479587b3576",
    "63f7160b-f85e-4ce8-8132-2c5880fd6c10",
    "64664836-29ba-402e-8915-094f2cb84225",
    "656173f6-cb10-49d0-b96e-c586815ccd38",
    "65fff289-f6a2-462d-bf0d-073da424b760",
    "6717ff5f-778d-49d4-8886-ed731124b945",
    "6774f0fb-645a-4c82-9610-1c5e768f253a",
    "67fd48c1-55bb-4c6f-a89c-dbd32bf18cf8",
    "67ff0240-0ffd-477d-a49c-97c8f0fdc8e5",
    "69510fc0-878a-4d7d-abff-20a03a2862e6",
    "697cf7dc-848c-4195-b86c-ac8e08d5bf1f",
    "6a5daba7-2584-480f-9026-7870832d1eaa",
    "6b3ac381-0287-47c8-9c42-85bb2d24410a",
    "6d0d5214-7b37-4d30-8b29-2126d53ad47a",
    "6e962234-079f-4487-9b88-02b668beea30",
    "6edbd73f-1346-4f7a-adf9-e1e4d60f0e68",
    "70e1a140-49cb-43cc-893b-916b9f9df48e",
    "71cbcdf1-3dfa-40de-81c8-2a4c85ba7dfb",
    "71f35041-1f09-4690-8f79-76967c9becaf",
    "729ebd8e-093c-4d7c-9334-48bf07e15929",
    "74efb024-4ddb-4ea3-b3f4-4d1489c8edd5",
    "756e0637-1ce1-4cea-a26d-fb298c5f0958",
    "79157627-276f-4bb1-9030-2522da8f9531",
    "7b92509c-31a5-40ec-8554-c0515daca502",
    "7bc25ed7-5679-4322-a5d0-d86573799b83",
    "7cec9e44-b1ac-47b6-8fae-f1dbf3adb527",
    "7d11e885-4315-4a50-8914-7a62d1605ca5",
    "7dcf45d4-fd89-44d5-bd83-17a31071f534",
    "7fc0daa2-0e60-4017-8183-5510ceec91b3",
    "810965fe-d785-413f-a9c2-dbd6ea03602a",
    "8350c73a-71ef-4fc8-a869-4f8f9a14bcc5",
    "838e21a4-3643-4fa1-a43e-89342b6b2e54",
    "84ca1953-12d2-41d7-a40d-9ef1d214e4f6",
    "864e3010-810a-44e7-85ce-2a82d2414292",
    "86704d1f-20a1-491d-b949-0984d65a4de9",
    "893596d2-f8a2-4cdd-9012-c19e2aa31d62",
    "8a137e27-71fb-4052-8f25-a99117894296",
    "8aa3c959-f641-4ebf-8330-dd95823b2c1c",
    "90c46627-57c9-4eaa-a3ac-57fd13392296",
        "9265eb77-83d4-441b-9006-76b7d41e652a",
        "962ba0da-230b-4ce4-8947-7e27a9da809d",
        "9705461a-a76c-414d-a1e6-1713b261bf0c",
        "97c9f40e-91f2-4099-ae5e-4ad9e6b9ff3c",
        "9938f231-02a1-4c10-881b-396f37b93f13",
        "9aa9edb6-674a-4411-863b-79e1b93e3955",
        "9bf8ac2c-39cc-43a0-96eb-26b2e53a565f",
        "9d6c8b59-bfc6-4d3d-b7d5-7404f0d83f93",
        "9d7a3cb1-0253-4ecc-bb55-fbb5c4bed9e2",
        "9e07455a-6956-49e0-8d85-09ff9ec682fd",
        "9ea8d650-9bb6-4bdc-b429-efdb867783ad",
        "9f390830-4f76-40c2-b8fd-84b518a12510",
        "9f6e8431-63e5-4bd6-98b3-a02aebf296bc",
        "a0ebdd38-cfc6-4a9b-844b-74664e6c8065",
        "a125bc3c-1e89-4e40-a1c3-83983d378d49",
        "a1ad17c7-a488-4030-81dc-3bbef9fdd9ba",
        "a2c3dfd2-012e-4d6a-ae3a-b06a0f02383f",
        "a34a0ea1-4f15-493f-b150-7201a70efc39",
        "a3b8ccf7-676d-41e4-927f-6bc3feffa45f",
        "a46aab3a-beb0-4dff-b35a-61447d7d98e1",
        "a4943b24-34b2-4dfe-a70a-e7d0aaa84513",
        "a4ea86fe-72ff-4cbd-b21f-ae68a1042396",
        "a6e369e9-affc-459b-958f-0c582ce9cb52",
        "a7b050c9-2c1a-4b02-a50c-f4f331358d54",
        "a87fda69-0be0-415f-accc-96c7abd1e1c0",
        "a9fc4f67-7906-4ee8-890c-7ab37dd63fd3",
        "aa07086b-7700-4832-bb2d-f03c8d7a0216",
        "ac08fc28-01d3-42bf-b8d6-22e593388749",
        "ae2f3224-e1dd-4e6d-ad48-156eea608c85",
        "aec23f48-43f2-4cb6-ab3f-de34c3ee2bb4",
        "b4fe6a4d-fa75-4663-a08b-0439a5b7c4c3",
        "b59ad540-cddb-4a70-bfdc-3c1355a299a4",
        "b5ce73df-42c2-4667-ac9c-f0658d537316",
        "b96ed1dd-4091-4ecf-81cc-26fb08fe4ecb",
        "be438ae6-d666-49ce-a162-7845f7dde1a1",
        "bee15273-d1e3-4d6d-a7fb-de02b21f84d4",
        "bf5bc023-8a39-480c-bfab-bf7c4d13d763",
        "c0fd08f8-acf0-4f17-9305-7461f5d56d48",
        "c20c8e1d-9bc8-467b-b9c8-1c7e07c52f73",
        "c2855aa9-2b32-4f69-86ac-e227c528016d",
        "c2d4ae80-6a2e-40ba-ba7a-a471f761955b",
        "c3179ae0-3837-4c42-9478-d32a438b8f06",
        "c3394435-0840-4399-b8a2-d73d0f3bf26a",
        "c78f4929-aeec-4fc8-8091-49c1f03c20f1",
        "c7b0e538-a217-411f-a0df-d80f4c9e59a9",
        "c81b39ba-2ecb-4970-9936-4fb88bd94397",
        "c9acd321-2890-444c-b26f-0f0edc6dc932",
        "c9eb19fb-8d69-4873-8ab4-0095aa3ed4b3",
        "cb9865d6-c597-4b9d-9511-62b7c48c34aa",
        "cceee230-dd14-4f00-934a-7bc28c9dfb62",
        "cdccc1e3-d7cd-4c4e-b65e-d5ce6bf875c5",
        "ce108f00-48a5-4b8d-9dd3-f3d549d11b7c",
        "ce4c581c-d9db-4879-9c77-96848de5de83",
        "cfbcb2f7-ea8b-48e4-925d-854a85b99681",
        "d17896b9-d61b-4836-84f0-e09d2a52e826",
        "d19ccbf7-55ef-47e2-aa17-69141fd75c00",
        "d1a70173-80db-46f0-9efa-efe6bb72e052",
        "d33b2b96-3fbe-4c95-9454-3257ad2f712a",
        "d62d1c40-ff52-4a70-b6f9-37f24080c498",
        "d6730e61-2608-4b3e-b400-31fb9458d206",
        "d704742e-9b36-4e53-92f3-669e3bf88139",
        "d795a4d1-6069-4a5c-8e73-ae622e45bbbf",
        "d804f6eb-67e2-4e90-afe2-497118b01a8f",
        "d939b4c3-05de-4221-8e14-7068cfb4ca64",
        "da45aacb-da8d-4f30-a89c-0f834680f276",
        "dcb8781c-5bdc-4686-8a7f-3b375d08a3fd",
        "de156507-c1fd-4fd9-9cd7-9c3ee9d37263",
        "e3e369b4-a36f-4159-bf66-c9c42ca89ebc",
        "e513c95f-8ca7-439e-87e2-95f2bd5e4aee",
        "e6d80d3a-276b-4a34-be31-8888a23bafa8",
        "e72e5194-8985-4d6e-b57f-c53de6ddf234",
        "e776a440-d72f-4783-932f-f0fc1be45dd6",
        "eaf7d0a6-46ac-4a30-ad48-17c33834bc75",
        "eb8b976b-042c-4b93-98f9-8764480a6a2f",
        "ec308ce3-514c-48d5-8379-b34c93096a8f",
        "eca010e1-8af0-4d41-b3fd-6229cf3c39b1",
        "ed305604-7c88-4b8e-a498-1b573d1f1224",
        "ed37953b-1f42-4fe7-85bb-f24ca710f2c4",
        "ef85ec27-c08a-40da-b806-20c65f2b83c0",
        "f091d791-519a-4e74-8041-ccd5ae123be0",
        "f376e0fb-4d40-44ae-b6d2-a2b78b51e458",
        "f55e18e2-b05a-4e06-b4f0-5fde9b23f05f",
        "f5914022-1de2-4313-9040-2f05b6a8d450",
        "f623f61e-beec-412e-bff1-9c2b5e3b6bb7",
        "f6969f5a-3a07-43da-b081-1257ab20e1ad",
        "f797f92e-9504-4112-bdae-90f32162e670",
        "f9626d56-cb69-455b-80fc-8aa90cb246f1",
        "fb4ca3db-d08f-4a20-b0fa-67c7c0f2659c",
        "fc5a9229-3cb0-4658-ab7e-99731844bf33",
        "fcf3a281-727a-4355-be05-2afff7fc1291",
        "fd254326-9554-420a-94ae-6bc325124d2c",
        "fdbf13ef-fa26-4929-a7fc-af7620bb2029"
    ]
    
    uuids = [
    "0103d3a8-08e0-451d-98a8-77a0c7e7b31f",
    "06e04fb5-1109-4314-9196-2b324c88dcc9",
    "13196eb2-92d4-411a-bc46-2873c7e3396b",
    "2d9d6273-0c7c-4262-8371-601cb0a8a264",
    "3dda1537-5d79-4ca3-97f2-b0229cdabfce",
    "47b98db9-8fcb-4376-8b7f-ad63413feaaf",
    "49af3ca1-ce0c-45d3-bfee-6808ec0cd336",
    "579d8903-5757-47b5-8252-817815a6132b",
    "5c1c68a7-2b4d-4b8c-9777-b6ef0732b324",
    "6243faf7-96c6-4815-b933-cedf9df5b890",
    "636e1c79-0c30-4b12-9cd1-19ee7dbcfbf9",
    "649b540e-1036-431a-82ef-f61fcc53c3cc",
    "6ddd8ee2-a155-47dc-9ce6-488a0e216fce",
    "70b18a66-f57c-48c4-8e76-ee990f9c46db",
    "750e2bad-3164-47e2-ba06-ef98fcd8ab52",
    "7a542b46-a342-47c0-bdcc-b8e57c0b6d49",
    "a1319328-a1e4-4191-8208-6cb7913f4599",
    "a2ac8f77-f824-480e-a851-efc562437dd0",
    "a4717347-9cae-414b-8f7f-fc07ed00643d",
    "bac3a47a-f9e9-4d98-87e7-6b9f22189c9e",
    "bbf129ac-0850-4440-84b4-bd2feee6e4cb",
    "ca2b8159-99b2-4d5b-855e-95434cda0141",
    "dc7474ad-6feb-4ca4-94a4-207fb0223871",
    "ff6413b2-cfda-4f37-b72c-cb25488d65ea"
]
    
    try:
        results = []
        for vendor_id in uuids:
            data = loop.run_until_complete(check_in_all_dbs(func=fetch_one_query, query=GET_ALL_ENV_NAMES_BY_VENDOR_ID.format(f"'{vendor_id}'"), db_type='GENERAL'))
            # print("#vendor id:\t", vendor_id, "\t\tenv name:\t", data.get('environmentName'))
            if data and data.get('environmentName'):
                asd = 'vendor id:\t' +  vendor_id + "\t\tenv name:\t" + data.get('environmentName')
            else: 
                asd = 'vendor id:\t' +  vendor_id + "\t\tenv name:\t" + 'NO ENV. FOUND'
                
            results.append(asd)
    finally:
        for res in results:
            print(res)
        print('\n', len(results))
        loop.close()
    
    
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
        
    