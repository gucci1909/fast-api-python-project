# hubspot.py

import base64
import json

from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from controllers.hubspot.hubspot_config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTHORIZATION_URL, SCOPE
from controllers.hubspot.hubspot_controller import prepare_hubspot_state, process_hubspot_callback, fetch_hubspot_credentials
from helpers.hubspot.helper import fetch_hubspot_companies

encoded_client_id_secret = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()

async def authorize_hubspot(user_id, org_id): 
    encoded_state, code_challenge = await prepare_hubspot_state(user_id, org_id)
    
    auth_url = f'{AUTHORIZATION_URL}&state={encoded_state}&code_challenge={code_challenge}&code_challenge_method=S256&scope={SCOPE}'
    
    return auth_url

async def oauth2callback_hubspot(request: Request):
    query_params = request.query_params
    if request.query_params.get('error'):
       raise HTTPException(status_code=400, detail=request.query_params.get('error_description'))
   
    try:
        await process_hubspot_callback(query_params, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    except HTTPException as e:
        raise e

    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
  return await fetch_hubspot_credentials(user_id, org_id)

def create_integration_item_metadata_object(item):
    """
    Args:
        The item from the API response.

    Returns:
        A transformed dictionary containing `id` and `properties`.
    """
    return {
        "id": item.get("id"),
        "properties": item.get("properties"),
    }
    
async def get_items_hubspot(credentials):
    credentials = json.loads(credentials)
    access_token = credentials.get("access_token")

    raw_results = await fetch_hubspot_companies(access_token)
    print(raw_results)

    # Transform each item using the metadata object function
    filtered_results = [create_integration_item_metadata_object(item) for item in raw_results]
    print(filtered_results)

    return filtered_results