
GET_VENDOR_BY_ID_QUERY = 'SELECT x.* from frontegg_vendors.vendors x WHERE id={}'
GET_TENANT_BY_ID_QUERY = 'SELECT x.* from frontegg_vendors.accounts x WHERE id={}'
GET_ACCOUNT_BY_ID_QUERY ='SELECT x.* FROM frontegg_backoffice.accounts x WHERE accountId={}'
GET_TENANT_CONFIGURATIONS_QUERY = 'SELECT x.* from frontegg_subscriptions.tenant_configurations x WHERE tenantId={}'

GET_USER_TENANT_BY_USER_ID_AND_TEN_ID_QUERY = 'SELECT x.* from frontegg_identity.users_tenants x WHERE userId={} AND tenantId={}'
GET_ROLES_BY_USER_TEN_ID_QUERY = 'SELECT x.* FROM frontegg_identity.users_tenants_roles x WHERE userTenantId={}'
GET_ROLE_NAME_BY_ID_QUERY = 'SELECT x.* FROM frontegg_identity.roles x WHERE id={}'

BASE_PATH = 'https://api.frontegg.com'
SUBSCRIPTION_CONFIGURATION = '/subscriptions/resources/billing/tenant-configurations/v1/'

