# hubspot.controllers.py

import secrets
import json 
import base64
import hashlib
import asyncio
import httpx

from fastapi import HTTPException
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from controllers.hubspot.hubspot_config import STATE_KEY_PREFIX, VERIFIER_KEY_PREFIX, EXPIRATION_TIME, CREDENTIAL_KEY_PREFIX, TOKEN_URL

async def prepare_hubspot_state(user_id, org_id):
    """
    Prepares the state data, code verifier, and Redis keys for HubSpot authorization.
    Returns the encoded state and code challenge.
    """
    # Generate state data
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
    
    code_verifier = secrets.token_urlsafe(32)
    
    # Generate code verifier and code challenge (we can make a helper function for if we are using this for other auth urls also )
    hash_value = hashlib.sha256()
    hash_value.update(code_verifier.encode('utf-8'))
    code_challenge = base64.urlsafe_b64encode(hash_value.digest()).decode('utf-8').replace('=', '')
    
    
    try:
        await asyncio.gather(
            add_key_value_redis(
                f"{STATE_KEY_PREFIX}:{org_id}:{user_id}", 
                json.dumps(state_data), 
                expire=EXPIRATION_TIME,
            ),
            add_key_value_redis(
                f"{VERIFIER_KEY_PREFIX}:{org_id}:{user_id}", 
                code_verifier, 
                expire=EXPIRATION_TIME,
            ),
        )
    except Exception as e:
        # Log or handle errors during Redis operations
        print(f"Error storing data in Redis: {e}")
    
    return encoded_state, code_challenge

async def process_hubspot_callback(query_params, client_id, client_secret, redirect_uri):
    """
    Args:
        The query parameters from the request.
        The client ID for HubSpot.
        The client secret for HubSpot.
        The redirect URI registered with HubSpot.

    Returns:
       The response data from HubSpot token API.
    """
    
    code = query_params.get('code')
    encoded_state = query_params.get('state')
    
    # Decode state
    try:
        state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid state parameter.")
    
    # Validate state
    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')
    
    # Fetch state and verifier from Redis
    saved_state, code_verifier = await asyncio.gather(
        get_value_redis(f'{STATE_KEY_PREFIX}:{org_id}:{user_id}'),
        get_value_redis(f'{VERIFIER_KEY_PREFIX}:{org_id}:{user_id}'),
    )
    
    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail="State does not match.")
    
    # Exchange code for access token (we can make a helper function for if we are using this for other auth urls also )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{TOKEN_URL}',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': client_id,
                'client_secret': client_secret,
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'PostmanRuntime/7.43.0',
                'Accept': '*/*',
                'Cache-Control': 'no-cache',
            }
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve access token.")
    
    # Save credentials and clean up Redis
    try:
      await asyncio.gather(
        add_key_value_redis(f'{CREDENTIAL_KEY_PREFIX}:{org_id}:{user_id}', json.dumps(response.json()), expire=600),
        delete_key_redis(f'{STATE_KEY_PREFIX}:{org_id}:{user_id}'),
        delete_key_redis(f'{VERIFIER_KEY_PREFIX}:{org_id}:{user_id}'),
      )
    except Exception as e:
        # Log or handle errors during Redis operations
        print(f"Error storing data in Redis: {e}")
    
    return response.json()

async def fetch_hubspot_credentials(user_id, org_id):
    """
    Args:
        user ID.
        organization ID.

    Returns:
        HubSpot credentials.
    """
    # same key we used in process_hubspot_callback to save the credentials in json, we are trying to get here from redis.
    key = f'{CREDENTIAL_KEY_PREFIX}:{org_id}:{user_id}'
    
    credentials = await get_value_redis(key)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    
    try:
        credentials = json.loads(credentials)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail='Invalid credentials format.')
    
    try:
        await delete_key_redis(key)
    except Exception as e:
        print(f"Error deleting Redis key {key}: {e}")

    return credentials