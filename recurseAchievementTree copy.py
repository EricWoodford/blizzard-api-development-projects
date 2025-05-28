# developer portal  https://develop.battle.net/access/clients

import requests
from json2html import json2html
import json
import os

# Blizzard API credentials
CLIENT_ID = "a3d019a5f8f54f01be450e5dd7fab98e"
CLIENT_SECRET = "JsHYM4Hd7wqXf1fsKpGGffAJV28sQ4ZP"
TOKEN_URL = "https://oauth.battle.net/token"
REALM_STATUS_URL = "https://us.api.blizzard.com/data/wow/realm/index"
REGION = "us"
LOCALE = "en_US"
CHARACTER_NAME =  "Erlenmeyer"
REALM_NAME = "Stormrage"

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

# return specific achievement info from achievement id
def get_achievement_from_id(access_token, region, achievement_id, locale):
    """
    Fetch achievement information by achievement ID.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"static-{region}", "locale": locale}   
    achievement_url = f"https://{region}.api.blizzard.com/data/wow/achievement/{achievement_id}"
    response = requests.get(achievement_url, headers=headers, params=params)
    if response.status_code == 200:
        fileName = f"./user_data/achievement_{achievement_id}.json"
        if not os.path.exists(fileName):
            with open(fileName, "w") as file:
                json.dump(response.json(), file, indent=4)   
        return response.json() 
    else:
        return False # raise Exception(f"Failed to get achievement info: {response.status_code} {response.text}")

def get_character_achievement_id(achievements_json, achivement_id):
    for achievement in achievements_json.get("achievements", []):
        if achievement.get("achievement", {}).get("id") == achivement_id:
            return achievement
    return False

def get_character_achievements_summary(access_token, region, locale, character_name, realm_name):
    """
    Query the Realm Status API to get a list of realms.
    character_name = "Elkagorasa".tolower()
    realm_name = "Malfurion".tolower()
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"dynamic-{region}", "locale": locale}
    character_url = f"https://{region}.api.blizzard.com/profile/wow/character/{realm_name.lower()}/{character_name.lower()}/achievements?namespace=profile-us&locale=en_US" # /summaries"    
    #character_url = "https://us.api.blizzard.com/profile/wow/character/stormrage/enervati/achievements?namespace=profile-us&locale=en_US"
    response = requests.get(character_url, headers=headers) # , params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get character achievements: {response.status_code} {response.text}")

def fetch_achievement_tree(access_token, REGION, LOCALE, achievement_id):
    achievement_data = get_achievement_from_id(access_token, REGION, achievement_id, LOCALE)
    children = achievement_data.get('child_criteria', [])

    def recurse_children(achievement_id, parent_id=None):
       # print(f"Fetching children for achievement ID: {achievement_id} from parent ID: {parent_id}")
        achievement_data = get_achievement_from_id(access_token, REGION, achievement_id, LOCALE)
        if not achievement_data:
         #   print(f"Failed to fetch data for achievement ID: {achievement_id}")
            return []
        children = achievement_data.get("criteria",[]).get('child_criteria', [])
        if not children:  # Stop criteria: if no child criteria are present
            return []
        child_ids = []
        for child in children:
            if 'achievement' in child:
                child_ids.append(child['achievement']['id'])
                child_ids.extend(recurse_children(child['achievement']['id'], achievement_id))
        return child_ids

    full_tree = {
        "id": achievement_id,
        "children": recurse_children(achievement_id)
    }

    return json.dumps(full_tree, indent=4)

# Example usage
if __name__ == "__main__":
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    achievement_id = "19458"  # Example achievement ID
    fileName = f"masterList_{achievement_id}.json"
    if not os.path.exists(fileName):
        achievement_tree = fetch_achievement_tree(access_token, REGION, LOCALE, achievement_id)
        #print("got new achievement tree" )
       # print(json.dumps(achievement_tree, indent=4))
        with open(fileName, "w") as file:
            json.dump(achievement_tree, file, indent=4)   
    else: 
        with open(fileName, "r") as file:
            achievement_tree = json.loads(json.load(file))
    
    #print(json.dumps(achievement_tree, indent=4))
    user_achievement_file = f"./{CHARACTER_NAME}_{REALM_NAME}_character_achievements.json"
    if os.path.exists(user_achievement_file):
        with open(user_achievement_file, "r") as file:
            character_achievements = json.load(file)
    else:
        character_achievements = get_character_achievements_summary(access_token, REGION, LOCALE, CHARACTER_NAME, REALM_NAME)            
        with open(user_achievement_file, "w") as file:
            json.dump(character_achievements, file, indent=4)      
   #print(json.dumps(character_achievements, indent=4))
    # loop through achievement_tree and see if the achievement is in the character_achievements
    # if so, see if the achievement criteria is marked as completed
    # return a list of not completed achievements
    not_completed_achievements = []
    for achievement_id in achievement_tree.get('children', []):
       # print(f"Checking achievement {achievement_id}")
        for character_achievement in character_achievements.get("achievements", []):
           # 
            if character_achievement.get("achievement", {}).get("id") == achievement_id:
                #print(json.dumps(character_achievement, indent=4))
                if character_achievement.get("criteria", {}).get("is_completed", {}) != True:          
                   # print(f"Achievement {achievement_id} is not completed")
                    not_completed_achievements.append(achievement_id)
                   # print(json.dumps(character_achievement, indent=4))               
                break        
            # check if the achievement is completed
    print(f"Not completed achievements: {not_completed_achievements}")
    print(f"Total not completed achievements: {len(not_completed_achievements)}")
    for achievement_id in not_completed_achievements:
        achievement_data = get_achievement_from_id(access_token, REGION, achievement_id, LOCALE)
        if achievement_data:
            print(f"Achievement ID: {achievement_id}")
            print(f"Name: {achievement_data.get('name')}")
            print(f"Description: {achievement_data.get('description')}")
            print(f"is_account_wide: {achievement_data.get('is_account_wide')}" )
            #print(f"Points: {achievement_data.get('points')}")
            #print(f"Reward: {achievement_data.get('reward')}")
            print(f"Criteria: {achievement_data.get('criteria', [])}")
