# developer portal  https://develop.battle.net/access/clients
# clientid = "a3d019a5f8f54f01be450e5dd7fab98e"
# clientSecret = "JsHYM4Hd7wqXf1fsKpGGffAJV28sQ4ZP"
# oathURL = "https://oauth.battle.net/authorize"
# characterURL = "https://us.api.blizzard.com/profile/wow/character/"
# realmName = "Tichondrius"
# characterName = "Nerfherder"

import requests
from json2html import json2html

import json
import os
# Blizzard API credentials
CLIENT_ID = "a3d019a5f8f54f01be450e5dd7fab98e"
CLIENT_SECRET = "JsHYM4Hd7wqXf1fsKpGGffAJV28sQ4ZP"
TOKEN_URL = "https://oauth.battle.net/token"
REALM_STATUS_URL = "https://us.api.blizzard.com/data/wow/realm/index"
#REALM_STATUS_URL = "https://us.api.blizzard.com/data/wow/realm/3723?namespace=dynamic-us"
REGION = "us"
LOCALE = "en_US"

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

# get list of all realms
# https://develop.battle.net/documentation/world-of-warcraft/realm-status-api
def get_realm_index(access_token, region, locale):
    """
    Query the Realm Status API to get a list of realms.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"dynamic-{region}", "locale": locale}
    response = requests.get(REALM_STATUS_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get realm status: {response.status_code} {response.text}")

# get list of all character achievements.
# https://develop.battle.net/documentation/world-of-warcraft/character-achievements-api
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

# get a specific achievement by id
# https://develop.battle.net/documentation/world-of-warcraft/achievement-api
def get_achievement_info(access_token, region, achievement_id, locale):
    """
    Fetch achievement information by achievement ID.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"static-{region}", "locale": locale}
    achievement_url = f"https://{region}.api.blizzard.com/data/wow/achievement/{achievement_id}"
    response = requests.get(achievement_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get achievement info: {response.status_code} {response.text}")


        
        
    # Process to find incomplete child criteria for "A World Awoken"


def get_character_achievement(achievements_json, achievement_name):
    for achievement in achievements_json.get("achievements", []):
        if achievement.get("achievement", {}).get("name", "").lower() == achievement_name.lower():
            return achievement
    return False

def get_character_achievement_id(achievements_json, achivement_id):
    for achievement in achievements_json.get("achievements", []):
        if achievement.get("achievement", {}).get("id") == achivement_id:
            return achievement
    return False

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
        return response.json() 
    else:
        raise Exception(f"Failed to get achievement info: {response.status_code} {response.text}")

# get unsorted list of all achievements and ids    
def get_achievement_index(access_token, region, locale):
    """
    Fetch achievement index information.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"static-{region}", "locale": locale}   
    achievement_url = f"https://{region}.api.blizzard.com/data/wow/achievement/"
    response = requests.get(achievement_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json() 
    else:
        raise Exception(f"Failed to get achievement info: {response.status_code} {response.text}")


def recurse_incomplete_achievements(access_token, REGION, LOCALE, character_achievements, achievement_id, result= None):
    """
    Recursively find all incomplete achievements for a given achievement name.
    """
    if result is None:
        result = []
    #print(achievement_id)
   # if achievement_name is None:
   #     return "none"
    
    character_status = get_character_achievement_id(character_achievements, achievement_id)    
    achievement_detail = get_achievement_info(access_token, REGION, achievement_id, LOCALE) # get detailed achievement from id
        
    if not character_status:   # the API returned null results for a few achievements
       if achievement_detail.get("criteria").get("child_criteria") is not None:
   
            for criterion in achievement_detail.get("criteria", {}).get("child_criteria", []):
                if criterion.get("achievement") is not None: 
                    result.append(criterion.get("achievement").get("id")) 
                    recurse_incomplete_achievements(access_token, REGION, LOCALE, character_achievements, criterion.get("achievement").get("id"), result)                    
            return result                
       else: 
           return result    
    
    #loop through child_ctiteria of character_status and find matching child_criteria in achievement_detail
    for criterion in character_status.get("criteria", {}).get("child_criteria", []):
        
        if (criterion.get("is_completed") == False):                
            child_id = criterion.get("id")
            for child_criterion in achievement_detail.get("criteria", {}).get("child_criteria", []):    
                if child_criterion.get("id") == child_id: 
                    if child_criterion.get("achievement") is not None:  
                       result.append(child_criterion.get("achievement").get("id")) 
                       recurse_incomplete_achievements(access_token, REGION, LOCALE, character_achievements, child_criterion.get("achievement").get("id"), result)
                    else:
                        return result
                    break    
   
    return result



if __name__ == "__main__":
    try:
        # Step 1: Get an access token       
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
        
        # get character achievement status - may want refresh this every day or so
        if os.path.exists("character_achievements.json"):
            with open("character_achievements.json", "r") as file:
                character_achievements = json.load(file)
        else:
            character_achievements = get_character_achievements_summary(access_token, REGION, LOCALE, "Elkagorasa", "Malfurion")            
            with open("character_achievements.json", "w") as file:
                json.dump(character_achievements, file, indent=4)       

        #print(json.dumps(get_character_achievement(character_achievements, "Storm Chaser"),indent=4))
        requested_achievement_id = 19458  #40953 ## a farewell to arms # "A World Awoken"
        original_Achievement = get_achievement_from_id(access_token, REGION, requested_achievement_id, LOCALE)   
        with open("15985.json", "w") as file:
                json.dump(original_Achievement, file, indent=4)     
        print(json.dumps(original_Achievement, indent=4))
        for achievement in original_Achievement.get("criteria", {}).get("child_criteria", []):
            child_achievement_id = achievement.get("achievement").get("id")            
            child_achievement_criteria = get_achievement_from_id(access_token, REGION, child_achievement_id, LOCALE)
            print(json.dumps(child_achievement_criteria, indent=4))





        
        achievement_status = recurse_incomplete_achievements(access_token, REGION, LOCALE, character_achievements, requested_achievement_id)
       
        # loop through achievement_status and get_achievement_info for each achievement and output the name, description, and 
        achievement_json = []
        for achievement_name in achievement_status:  # array of achievement ids
            achievement_info = get_achievement_from_id(access_token, REGION, achievement_name, LOCALE)    
            character_status = get_character_achievement_id(character_achievements, achievement_name)
           # print(json.dumps(character_status, indent=4))
           # print(json.dumps(achievement_info, indent=4))
            if character_status is not False:  
                for criterion in character_status.get("criteria", {}).get("child_criteria", []):
                    if (criterion.get("is_completed") == False):                
                        child_id = criterion.get("id")
                        for child_criterion in achievement_info.get("criteria", {}).get("child_criteria", []):                            
                            if child_criterion.get("id") == child_id:                 
                                
                                if child_criterion.get("achievement") is not None: 
                                    #print("child")
                                    #print(json.dumps(child_criterion, indent=4))
                                    #print(json.dumps(criterion, indent=4))
                                    achievement_json.append({
                                        "name": achievement_info.get("name"),
                                        "criteria name": child_criterion.get("achievement").get("name"),
                                        "description": child_criterion.get("description"),
                                        #"description": achievement_info.get("description"),
                                        "id": child_criterion.get("achievement").get("id"),
                                        "amount": criterion.get("amount")
                                    })
                                break
            
            #achievement_json.append(character_status)
        sorted_data = sorted(achievement_json, key=lambda x: x.get("name", 0))
        filename = original_Achievement.get("name").replace(" ", "_") + ".html"
        print(f"Writing to {filename}")
        data = json.dumps(sorted_data)
        html_output = json2html.convert(json=data)
        with open(filename, "w", encoding="utf-8") as file:
            file.write("<html><body>")
            file.write(html_output)
            file.write("</body></html>")

       # print(html_output)
       # print(json.dumps(get_achievement_index(access_token, REGION, LOCALE),indent=4)) # get all achievements and ids

    
    except Exception as e:
        print(f"Error: {e}")