BASE_PATH = 'https://api.frontegg.com'
SUBSCRIPTION_CONFIGURATION = '/subscriptions/resources/billing/tenant-configurations/v1/'
ZENDESK_TICKET_URL = 'https://frontegg-help.zendesk.com/api/v2/tickets/'
ZENDESK_USERS_FROM_TICKET_URL = 'https://frontegg-help.zendesk.com/api/v2/tickets/{}?include=users'


GET_VENDOR_BY_ID_QUERY = 'SELECT * FROM frontegg_vendors.vendors v WHERE v.id ={}'
GET_VENDORS_IDS_BY_ACCOUNT_ID_QUERY = 'SELECT * FROM frontegg_vendors.vendors v  WHERE v.accountId={}'
GET_TENANT_BY_ID_QUERY = 'SELECT x.* from frontegg_vendors.accounts x WHERE x.id={}'
GET_ACCOUNT_BY_ID_QUERY ='SELECT x.* FROM frontegg_backoffice.accounts x WHERE x.accountId={}'
GET_TENANT_CONFIGURATIONS_QUERY = 'SELECT x.* from frontegg_subscriptions.tenant_configurations x WHERE x.tenantId={}'

GET_USER_TENANT_BY_USER_ID_AND_TEN_ID_QUERY = 'SELECT x.* from frontegg_identity.users_tenants x WHERE x.userId={} AND x.tenantId={}'
GET_ROLES_BY_USER_TEN_ID_QUERY = 'SELECT x.* FROM frontegg_identity.users_tenants_roles x WHERE x.userTenantId={}'
GET_ROLE_NAME_BY_ID_QUERY = 'SELECT x.* FROM frontegg_identity.roles x WHERE x.id={}'

GET_SSO_DOMAINS_BY_VENDOR = 'SELECT * FROM frontegg_team_management.sso_domains sd WHERE sd.vendorId={}'
GET_SSO_CONFIGS_BY_SSO_CONFIG_ID = 'SELECT * FROM frontegg_team_management.sso_configs sc WHERE sc.id={}'
GET_SAML_GROUPS_BY_SSO_CONFIG_ID = 'SELECT * FROM frontegg_team_management.saml_groups sg WHERE sg.samlConfigId={}'

GET_ACCOUNT_TENANT_ID_BY_EMAIL_AND_FE_PROD_ID = 'SELECT * FROM frontegg_identity.users u WHERE u.email={} AND u.vendorId={}'
GET_ACCOUNT_ID_BY_ACCOUNT_TENANT_ID = 'SELECT * FROM frontegg_vendors.accounts a WHERE a.accountTenantId={}'
GET_VENDOR_ID_BY_ACCOUNT_ID = 'SELECT * FROM frontegg_vendors.vendors v  WHERE v.accountId={}'

AND_DOMAIN = 'AND sd.domain = {}'

REGIONS = ['EU', 'US']
# REGIONS = ['EU', 'US', 'CA', 'AU']

PROD_VENDOR_ID = '86744d15-3970-4ca1-82e9-2cd281728624'


"""
1. get domains by vendor:  -----   DONE
GET_SSO_DOMAINS_BY_VENDOR

2. get sso config IDs by vendor and domain:  -----   DONE
GET_SSO_DOMAINS_BY_VENDOR + AND_DOMAIN

3. get sso config by config ID:  -----   DONE
GET_SSO_CONFIGS_BY_SSO_CONFIG_ID

4. SAML GROUPS by config ID:   -----   DONE
GET_SAML_GROUPS_BY_SSO_CONFIG_ID

5. get sso conf for all domains from vendor id
6. get saml groups for all domains from vendor id
7. get 6 and 7 from email
"""
