#authentication.py
import requests
import os   
from dotenv import load_dotenv

# read credentials from .env file
from dotenv import load_dotenv
load_dotenv()
CLIENT_ID = os.getenv("BLIZZARD_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLIZZARD_CLIENT_SECRET")


# Blizzard API credentials
TOKEN_URL = "https://oauth.battle.net/token"

# get authentication token
# https://develop.battle.net/documentation/guides/getting-started
def get_access_token(client_id, client_secret):
    """
    Obtain an OAuth access token from Blizzard API.
    """
    response = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret)
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to get access token: {response.status_code} {response.text}")