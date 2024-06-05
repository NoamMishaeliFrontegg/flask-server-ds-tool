from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

    
@dataclass(frozen=False)
class Builder_configs:
    id: str = None
    name: str = None

@dataclass(frozen=False)
class SSO_configs:
    id: str = None
    name: str = None

@dataclass(frozen=False)
class Tenant:
    id: str = None #accountId in DB
    name: str = None
    meta_data: str = None
    vendor_id: str = None
    sso_configs: SSO_configs = None
    builder_configs: Builder_configs = None

@dataclass(frozen=False)
class Vendor:
    id: str = None 
    env_name: str = None
    app_url: str = None
    login_url: str = None
    host: str = None
    region: str = None
    country: str = None
    fe_stack: str = None
    be_stack: str = None
    account_id: str = None
    meta_data: str = None
    tenants: List[Tenant] = None

@dataclass(frozen=False)
class Account:
    id: str = None
    name: str = None
    number_of_environments: int = 0
    vendors: List[Vendor] = None
    builder_config: Builder_configs = None

@dataclass(frozen=False)
class Context:
    id: str = None
    account: Account = None