from authentication import get_access_token, CLIENT_ID, CLIENT_SECRET
import requests
import json
import os

def get_character_achievements_summary(access_token, region, locale, character_name, realm_name):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"dynamic-{region}", "locale": locale}
    character_url = f"https://{region}.api.blizzard.com/profile/wow/character/{realm_name.lower()}/{character_name.lower()}/achievements?namespace=profile-us&locale=en_US" # /summaries"    
    response = requests.get(character_url, headers=headers) # , params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get character achievements: {response.status_code} {response.text}")



if __name__ == "__main__":

    # Blizzard API constants
    REGION = "us"
    LOCALE = "en_US"

    # Character and realm information
    CHARACTER_NAME =  "Elkagorasa" 
    REALM_NAME = "Malfurion"

    Characters = [{"name": "Egerorius", "realm": "Stormrage"},{"name": "Eyerolls", "realm": "Stormrage"},{"name": "Erleoniance", "realm": "Stormrage"},{"name": "Erknea", "realm": "Malfurion"}]
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    for character in Characters:
        CHARACTER_NAME = character["name"]
        REALM_NAME = character["realm"]

        # Fetch and print character achievements
        try:
            character_achievements = get_character_achievements_summary(access_token, REGION, LOCALE, CHARACTER_NAME, REALM_NAME)
            print(f"Achievements for {CHARACTER_NAME} on {REALM_NAME}:")
            user_achievement_file = f"./{CHARACTER_NAME}_{REALM_NAME}_character_achievements.json"
            if not os.path.exists(user_achievement_file):
                with open(user_achievement_file, "w") as file:
                    json.dump(character_achievements, file, indent=4)      
           # print(json.dumps(character_achievements, indent=4)) 
        except Exception as e:
            print(f"Error fetching achievements for {CHARACTER_NAME} on {REALM_NAME}: {e}")        
    else:
        character_achievements = get_character_achievements_summary(access_token, REGION, LOCALE, CHARACTER_NAME, REALM_NAME)            
        with open(user_achievement_file, "w") as file:
            json.dump(character_achievements, file, indent=4)   
     