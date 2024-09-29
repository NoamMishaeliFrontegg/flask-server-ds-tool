BASE_EU_PATH = 'https://api.frontegg.com'
BASE_US_PATH = 'https://api.us.frontegg.com'
BASE_CA_PATH = 'https://api.ca.frontegg.com'
BASE_AU_PATH = 'https://api.au.frontegg.com'

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

GET_ALL_ENV_NAMES_BY_VENDOR_ID = 'SELECT v.environmentName FROM frontegg_vendors.vendors v WHERE v.id ={}'


AND_DOMAIN = 'AND sd.domain = {}'

GENERAL = 'GENERAL'
IDENTITY = 'IDENTITY'
REGIONS = ['EU', 'US', 'CA']
# REGIONS = ['EU', 'US', 'CA', 'AP']



# P1 # search vendors by email
CHECK_IF_EMAIL_EXISTS_IN_REGION = 'SELECT u.tenantId FROM frontegg_identity.users u WHERE u.email={} AND u.vendorId={}'
# P2 # get vendors by accountId
GET_VENDORS_IDS_BY_ACCOUNT_TENANT_ID = 'SELECT v.id, v.environmentName, v.loginURL, v.appURL FROM frontegg_vendors.vendors v JOIN frontegg_vendors.accounts a ON  a.id = v.accountId WHERE a.accountTenantId={}'

# P3 # get tenatns    
GET_TENTANS_OF_VENDOR = 'SELECT x.* FROM frontegg_backoffice.accounts x WHERE x.vendorId={}'

# P3.3 # get saml config id
GET_SAML_GROUPS_BY_SSO_ID ='SELECT * FROM frontegg_team_management.saml_groups sg WHERE sg.samlConfigId={}'

# P3 # get applications of vendor
GET_VENDOR_APPLICATIONS ='SELECT * FROM frontegg_applications.applications a WHERE a.vendorId={}'
# P3.1 # get all tenants under an application
GET_TENANTS_OF_APPLICATIONS ='SELECT a.name, appt.tenantId FROM frontegg_applications.applications_tenants appt JOIN frontegg_backoffice.accounts a ON appt.tenantId = a.accountId WHERE appt.appId={}'

# P3 # get builder config
GET_BUILDER_CONFIGURATIONS = 'SELECT be.config, be.env FROM frontegg_dashboard_env_builder.builder_environment be WHERE be.accountId={} ORDER BY be.createdAt DESC LIMIT 1'

# Allowed Origins
GET_ALLOWED_ORIGINS= 'SELECT ao.origin FROM frontegg_vendors.allowed_origins ao WHERE ao.vendorId={}'

# Custom domain
GET_CUSTOM_DOMAIN = 'SELECT cd.domain FROM frontegg_vendors.custom_domains cd WHERE cd.vendorId={}'

# Impersonation
GET_IMPERSONATION_SETTINGS = 'SELECT ic.enabled, ic.sendEmailNotifications, ic.allowTenantAudits FROM frontegg_identity.impersonation_configuration ic WHERE ic.vendorId={}'

# Groups
GET_GROUPS = 'SELECT * FROM frontegg_identity.groups g WHERE g.tenantId={}'

# SSO
GET_SSO_CONFIGS = 'SELECT sc.enabled,sc.validated , sd.domain, sc.spEntityId, sc.acsUrl, sc.ssoEndpoint, sc.createdAt FROM frontegg_team_management.sso_domains sd JOIN frontegg_team_management.sso_configs sc  ON sd.ssoConfigId = sc.id WHERE sd.tenantId={}'