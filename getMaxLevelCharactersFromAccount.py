# developer portal  https://develop.battle.net/access/clients

import requests
from json2html import json2html
import json
import os
from collections import defaultdict


# Blizzard API credentials
CLIENT_ID = "a3d019a5f8f54f01be450e5dd7fab98e"
CLIENT_SECRET = "JsHYM4Hd7wqXf1fsKpGGffAJV28sQ4ZP"
TOKEN_URL = "https://oauth.battle.net/token"
# Blizzard API constants
REGION = "us"
LOCALE = "en_US"

# Character and realm information
CHARACTER_NAME =  "Eruptan"
REALM_NAME = "Stormrage"
# Achievement hash to store achievement IDs and their children
achievement_hash = defaultdict(list)
# Achievement ID to start with
achievement_id = "19458" 

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



def get_all_max_level_characters(access_token): 
    headers = {"Authorization": f"Bearer {access_token}"}  
    url = "https://us.api.blizzard.com/profile/user/wow?namespace=profile-us&locale=en_US"
    response = requests.get(url, headers=headers) #, params=params)
    return response.json()


# Example usage
if __name__ == "__main__":
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)    
    headers = {"Authorization": f"Bearer {access_token}"}  
    response = requests.get("https://us.api.blizzard.com/profile/user/wow?namespace=profile-us&locale=en_US", headers=headers) 
    print(response.status_code)
