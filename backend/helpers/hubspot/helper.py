# hubspot.helpers.py
import httpx

from fastapi import HTTPException
from controllers.hubspot.hubspot_config import COMPANY_URL

'''
adding companies to view
this will be a post request as explained in screen_recording
api url = 'https://api.hubapi.com/crm/v3/objects/companies'
headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
json part for request to adding companies through a post request
{
  "properties": {
    "name": "VectorShift_123",
    "domain": "gucci1909.com",
    "city": "Bangalore",
    "phone": "555-555-555",
    "state": "Karnataka"
  }
}
'''

async def fetch_hubspot_companies(access_token):
    """
    Args:
        The HubSpot API access token.

    Returns:
        A list of company data from the API response.
    """
    if not access_token:
        raise HTTPException(status_code=400, detail="Access token is missing.")

    url = f'{COMPANY_URL}'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch data from HubSpot API."
        )

    response_data = response.json()
    return response_data.get("results", [])