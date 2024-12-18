# config.py
# we can create a config file, or use environment , when we deploy the api to a server, and we can store the auth url, client id and secret in aws env variables in code pipeline.

# HubSpot OAuth Configuration
CLIENT_ID = '2db91c1a-c979-4d8d-9bc9-0cc282c004cd'
CLIENT_SECRET = 'e8ba88a6-2587-4ea3-8290-efb349352559'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'

# OAuth Authorization URL and Scope for HubSpot
AUTHORIZATION_URL = f'https://app.hubspot.com/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}'
TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'
COMPANY_URL = 'https://api.hubapi.com/crm/v3/objects/companies'
SCOPE = 'crm.objects.companies.read crm.objects.companies.write'

# Constants for Redis key prefixes and expiration
STATE_KEY_PREFIX = "hubspot_state"
VERIFIER_KEY_PREFIX = "hubspot_verifier"
CREDENTIAL_KEY_PREFIX = "hubspot_credentials"
EXPIRATION_TIME = 600