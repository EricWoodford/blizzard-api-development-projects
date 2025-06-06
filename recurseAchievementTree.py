# reference: developer portal  https://develop.battle.net/access/clients

from authentication import get_access_token, CLIENT_ID, CLIENT_SECRET
import requests
from json2html import json2html
import json
import os
from collections import defaultdict


# Blizzard API constants
REGION = "us"
LOCALE = "en_US"

# Character and realm information
CHARACTER_NAME =  "Erlenmeyer" 
REALM_NAME = "Stormrage"
# Achievement ID to start with
#achievement_id = "19458"  # a world awoken
achievement_id = "40953" # a farewell to arms

# Achievement hash to store achievement IDs and their children
achievement_hash = defaultdict(list)



# return specific achievement info from achievement id
def get_achievement_from_id(access_token, region, achievement_id, locale):    
    fileName = f"./achievement_data/achievement_{achievement_id}.json"

    # see if the achievement_data directory exists, if not, create it
    if not os.path.exists("./achievement_data"):
        os.makedirs("./achievement_data")
    
    # if the achievement info has already been fetched, load it from the file
    # otherwise, fetch it from the API and save it to the file
    if os.path.exists(fileName):
        with open(fileName, "r") as file:
            return json.load(file)

    # grab the achievement info from the API    
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"static-{region}", "locale": locale}   
    achievement_url = f"https://{region}.api.blizzard.com/data/wow/achievement/{achievement_id}"
    response = requests.get(achievement_url, headers=headers, params=params)
    if response.status_code == 200:        
        if not os.path.exists(fileName):
            with open(fileName, "w") as file:
                json.dump(response.json(), file, indent=4)   
        return response.json() 
    else:
        return False # raise Exception(f"Failed to get achievement info: {response.status_code} {response.text}")

# return specific character achievement info from the character achievement sumamry json
def get_character_achievement_id(achievements_json, achivement_id):
    for achievement in achievements_json.get("achievements", []):
        if achievement.get("achievement", {}).get("id") == achivement_id:
            return achievement
    return False

# returns character achievements summary from the API
# https://develop.battle.net/documentation/world-of-warcraft/profile-apis
def get_character_achievements_summary(access_token, region, locale, character_name, realm_name):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"dynamic-{region}", "locale": locale}
    character_url = f"https://{region}.api.blizzard.com/profile/wow/character/{realm_name.lower()}/{character_name.lower()}/achievements?namespace=profile-us&locale=en_US" # /summaries"    
    #character_url = "https://us.api.blizzard.com/profile/wow/character/stormrage/enervati/achievements?namespace=profile-us&locale=en_US"
    response = requests.get(character_url, headers=headers) # , params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get character achievements: {response.status_code} {response.text}")


# recursively fetch the achievement tree for a given achievement ID
# and return a JSON object with the achievement ID and its children
def fetch_achievement_tree(access_token, REGION, LOCALE, achievement_id):
    
    achievement_data = get_achievement_from_id(access_token, REGION, achievement_id, LOCALE)
    children = achievement_data.get('child_criteria', [])

    def recurse_children(achievement_id, parent_id=None):
       # print(f"Fetching children for achievement ID: {achievement_id} from parent ID: {parent_id}")
        achievement_data = get_achievement_from_id(access_token, REGION, achievement_id, LOCALE)
        if not achievement_data:         
            return []
        # if achievement_data doesn't have criteria, return an empty list
        if 'criteria' not in achievement_data or not achievement_data.get('criteria', {}).get('child_criteria', []):
            return []
        children = achievement_data.get("criteria",[]).get('child_criteria', [])
        if not children:  # Stop criteria: if no child criteria are present
            return []
        child_ids = []
        for child in children:
            if 'achievement' in child:
                child_ids.append(child['achievement']['id'])
                child_ids.extend(recurse_children(child['achievement']['id'], achievement_id))
        achievement_hash[achievement_id].extend(child_ids)
        return child_ids        

    full_tree = {
        "id": achievement_id,
        "children": [recurse_children(achievement_id)]
    }    
    return json.dumps(full_tree, indent=10)



if __name__ == "__main__":
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)    
    parent_achievement_name = get_achievement_from_id(access_token, REGION, achievement_id, LOCALE).get("name")
    if parent_achievement_name is None:
        print(f"Achievement ID {achievement_id} not found.")
        exit(1)

    # masterList is the all the acchievement ids related to this achievement_id
    fileName = f"masterList_{achievement_id}.json"
    # dictionary is a hash of achievement_id to child achievement ids, with parent achievement_id as the key
    dict_fileName = f"dictionary_{achievement_id}.json"
    # attempt to read the files locally to avoid unnecessary API calls
    if not os.path.exists(fileName) or not os.path.exists(dict_fileName):
        # this function generates the achievement hash as well as the achievement tree
        achievement_tree = fetch_achievement_tree(access_token, REGION, LOCALE, achievement_id)
        with open(fileName, "w") as file:
            json.dump(achievement_tree, file, indent=4)   
        with open(dict_fileName, "w") as file:
            json.dump(achievement_hash, file, indent=4)
    else: 
        with open(fileName, "r") as file:
            achievement_tree = json.loads(json.load(file))
        with open(dict_fileName, "r") as file:
            achievement_hash = json.load(file)
    
    if "Character_Reports" not in os.listdir():
        os.makedirs("Character_Reports")
    # get this characters achievement dump, if file exists, load it, otherwise fetch it from the API
    user_achievement_file = f"./Character_Reports/{CHARACTER_NAME}_{REALM_NAME}_character_achievements.json"
    if os.path.exists(user_achievement_file):
        with open(user_achievement_file, "r") as file:
            character_achievements = json.load(file)
    else:
        character_achievements = get_character_achievements_summary(access_token, REGION, LOCALE, CHARACTER_NAME, REALM_NAME)            
        with open(user_achievement_file, "w") as file:
            json.dump(character_achievements, file, indent=4)      
   
    # loop through achievement_tree and see if the achievement is in the character_achievements
    # if so, see if the achievement criteria is marked as completed
    # return a list of not completed achievements
    not_completed_achievements = []
   
    # achievement_tree will contain all achievements related to this achievement_id
    # the children value appears to be a double-nested list, so we need to access the first element
    all_achievements = achievement_tree.get("children", [])[0]        
    # remove entries from the list that do not have any children. 
    # these will likely be the leaves of the achievement tree
    filtered_dict = {k: v for k, v in achievement_hash.items() if v not in (None, [], "")}        
    short_list = list(filtered_dict.keys())

    # let's prune some branches off the achievement tree
    for achievement_id in short_list:
        for character_achievement in character_achievements.get("achievements", []):    
            if str(character_achievement.get("achievement", {}).get("id")) == str(achievement_id):
                if character_achievement.get("criteria", {}).get("is_completed", {}) != True:          
                    not_completed_achievements.append(achievement_id)
                    if achievement_id in all_achievements:
                            all_achievements.remove(achievement_id)     
                else:
                    # pull list of child achievements form achievement_hash and remove them from the achievement_tree 
                    for child_achievement_id in achievement_hash[str(achievement_id)]:
                        if child_achievement_id in all_achievements:
                            all_achievements.remove(child_achievement_id)               
                break

    
    # loop throught the remaining all_achievements and see if they are not completed in the character_achievements
    # if they are not completed, add them to the not_completed_achievements list
    for achievement_id in all_achievements:             
        for character_achievement in character_achievements.get("achievements", []):           # 
            if character_achievement.get("achievement", {}).get("id") == achievement_id:                
                if character_achievement.get("criteria", {}).get("is_completed", {}) != True:          
                    not_completed_achievements.append(achievement_id)                
                break                    

    
    # generate a report of not completed achievements and export to html
    achievement_report = []
    for achievement_id in not_completed_achievements:
        if achievement_hash.get(str(achievement_id)) == []:
            achievement_data = get_achievement_from_id(access_token, REGION, achievement_id, LOCALE)
            character_achievement_data = get_character_achievement_id(character_achievements, achievement_id)
            if achievement_data:
                # loop through achievement_data and character_achievement_data and extract all the character criteria where marked false, and return the achievement data value.
                incomplete_criteria = []
                for criteria in character_achievement_data.get("criteria", []).get("child_criteria", []):                    
                    if not criteria.get("is_completed", True):  
                        #print(f"{achievement_id} = {criteria}")
                        report_criteria = {}                      
                        for achievement_criteria in achievement_data.get("criteria", []).get("child_criteria", []):
                          #  print(achievement_criteria)
                            if criteria.get("id") == achievement_criteria.get("id"):
                                wowhead_url =  f"https://www.wowhead.com/achievement={achievement_id}&criteria={criteria.get('id')}"
                               # print(f"Found criteria {criteria.get('id')} in achievement {achievement_criteria}")
                               # criteria["name"] = achievement_criteria.get("name")
                               
                                report_criteria["description"] = f'<a href={wowhead_url} target="_blank">{achievement_criteria.get("description")}</a>'
                                if criteria.get("amount") is not None:
                                    report_criteria["amount"] = criteria.get("amount")
                                
                                #report_criteria["wowhead_url"] = wowhead_url
                                #report_criteria["is_completed"] = criteria.get("is_completed", False)
                                incomplete_criteria.append(report_criteria)
                               # break
                achievement_entry = {
                    "id": achievement_id,
                 #   "wowhead_url": f"https://www.wowhead.com/achievement={achievement_id}",
                    "name": achievement_data.get("name"),
                    "description": achievement_data.get("description"),
                  # "is_account_wide": achievement_data.get("is_account_wide"),
                    "criteria": incomplete_criteria # [0].get("description"), #character_achievement_data.get("criteria", []),                    
                    #"wowhead_url": incomplete_criteria[0].get("wowhead_url", f"https://www.wowhead.com/achievement={achievement_id}"),
                    #"amount_completed": incomplete_criteria[0].get("amount", 0)

                }
                achievement_report.append(achievement_entry)

    # start outputting the report
    achievement_report_file = f"./Character_Reports/{CHARACTER_NAME}_{REALM_NAME}_{parent_achievement_name}_achievement_report.html"
    achievement_report_json = f"./Character_Reports/{CHARACTER_NAME}_{REALM_NAME}_{parent_achievement_name}_achievement_report.json"
    with open(achievement_report_json, "w") as file:
        json.dump(achievement_report, file, indent=4)    

    # todays date for the report
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # convert the achievement_report to html  
    html_report = json2html.convert(json=achievement_report, table_attributes="border=1", escape=False)
    # add quick header and footer to the report
    html_report = f"<h2>{CHARACTER_NAME} {REALM_NAME}</h2><br /> {parent_achievement_name} <br />generated: {today} <br />"+ html_report
    html_report = html_report+ f"<br /> Total achievements in report: {len(achievement_report)}"
  
    with open(achievement_report_file, "w") as file:
        file.write(html_report)
  
    print(f"Achievement report saved to {achievement_report_file}")
    print(f"Total achievements in report: {len(achievement_report)}")   