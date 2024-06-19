BASE_PATH = 'https://api.frontegg.com'
SUBSCRIPTION_CONFIGURATION = '/subscriptions/resources/billing/tenant-configurations/v1/'
ZENDESK_TICKET_URL = 'https://frontegg-help.zendesk.com/api/v2/tickets/'
FRONTEGG_WHITE_LABEL = '/vendors/whitelabel-mode'
FRONTEGG_AUTH_AS_VENDOR = '/auth/vendor/'
ZENDESK_USERS_FROM_TICKET_URL = 'https://frontegg-help.zendesk.com/api/v2/tickets/{}?include=users'

GET_VENDOR_BY_ID_QUERY = 'SELECT * FROM frontegg_vendors.vendors v WHERE v.id ={}'
GET_VENDORS_IDS_BY_ACCOUNT_ID_QUERY = 'SELECT * FROM frontegg_vendors.vendors v  WHERE v.accountId={}'

GET_ACCOUNT_DETAILS_BY_ID ='SELECT * FROM frontegg_vendors.accounts a WHERE a.id={}'
GET_ACCOUNT_BY_ID_QUERY ='SELECT x.* FROM frontegg_backoffice.accounts x WHERE x.accountId={}'
GET_ALL_TENANTS_BY_VENDOR_ID = 'SELECT x.* FROM frontegg_backoffice.accounts x WHERE x.vendorId ={}'
GET_ACCOUNT_ID_BY_ACCOUNT_TENANT_ID = 'SELECT * FROM frontegg_vendors.accounts a WHERE a.accountTenantId={}'

GET_SSO_DOMAINS_BY_TENANT = 'SELECT * FROM frontegg_team_management.sso_domains sd WHERE sd.tenantId={}'
GET_SSO_DOMAINS_BY_VENDOR = 'SELECT * FROM frontegg_team_management.sso_domains sd WHERE sd.vendorId={}'
GET_SSO_CONFIGS_BY_SSO_CONFIG_ID = 'SELECT * FROM frontegg_team_management.sso_configs sc WHERE sc.id={}'
GET_SAML_GROUPS_BY_SSO_CONFIG_ID = 'SELECT * FROM frontegg_team_management.saml_groups sg WHERE sg.samlConfigId={}'

GET_ROLE_NAME_BY_ID_QUERY = 'SELECT x.* FROM frontegg_identity.roles x WHERE x.id={}'
GET_ROLES_BY_USER_TEN_ID_QUERY = 'SELECT x.* FROM frontegg_identity.users_tenants_roles x WHERE x.userTenantId={}'
GET_USER_TENANT_BY_USER_ID_AND_TEN_ID_QUERY = 'SELECT x.* from frontegg_identity.users_tenants x WHERE x.userId={} AND x.tenantId={}'

GET_TENANT_CONFIGURATIONS_QUERY = 'SELECT x.* from frontegg_subscriptions.tenant_configurations x WHERE x.tenantId={}'

GET_ACCOUNT_TENANT_ID_BY_EMAIL_AND_FE_PROD_ID = 'SELECT * FROM frontegg_identity.users u WHERE u.email={} AND u.vendorId={}'

AND_DOMAIN = 'AND sd.domain = {}'

GENERAL = 'GENERAL'
IDENTITY = 'IDENTITY'
REGIONS = ['EU', 'US']
# REGIONS = ['EU', 'US', 'CA', 'AU']

# TODO:
# 1. edge case :: in search in all regions when an account is under few regions (for example - Talon) 
# 3. add creds for CA and AU
# 4. add a logger