# developer portal  https://develop.battle.net/access/clients

import requests
import json
import os


from authentication import get_access_token, CLIENT_ID, CLIENT_SECRET

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
