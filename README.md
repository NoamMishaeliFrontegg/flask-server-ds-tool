
## Flask Server For DevSuc/Support Tool

Install requirements

```bash
$ pip install -r requirements.txt
```

Create .env file in project's root directory 

```bash
$ touch .env
```

Or

```bash
$ nano .env
```

Add the following key-value pairs with your apono credentials to the .env file 
```bash
USER_NAME = ''

# EU
HOST_GENERAL_EU = ''
PASSWD_GENERAL_EU = ''
HOST_IDENTITY_EU = ''
PASSWD_IDENTITY_EU = ''

# US
HOST_GENERAL_US = ''
PASSWD_GENERAL_US = ''
HOST_IDENTITY_US = ''
PASSWD_IDENTITY_US = ''

# AP
HOST_GENERAL_AP = ''
PASSWD_GENERAL_AP = ''
HOST_IDENTITY_AP = ''
PASSWD_IDENTITY_AP = ''

# CAD
HOST_GENERAL_CAD = ''
PASSWD_GENERAL_CAD = ''
HOST_IDENTITY_CAD = ''
PASSWD_IDENTITY_CAD = ''

CLIENT_ID = ''
SECRET = ''
PRODUCTION_CLIENT_ID = ''
PRODUCTION_SECRET = ''
ZENDESK_API_TOKEN = ''
ZENDESK_EMAIL_TOKEN = ''
PROD_VENDOR_ID = ''

```

Run server

```bash
$ flask run
```
    
