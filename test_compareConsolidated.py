# read the consolidated_achievements.json file 
# compare achievement_ids from masterList_19458.json to see how many are "true" 

# read all of the character_achivement.json files in the directory
import json
import os
# compare similar achievements in each of the files.
# createa list of all ahcievement ids, and if ANY of the json files are marked true for that achievement, mark it as true in the output.
import glob     
import sys

if __name__ == "__main__":
    incoming_achievement_ids = []

    with open("consolidated_achievements.json", "r") as file:
        character_achievements = json.load(file)

    
    with open("masterList_40953.json", "r") as file:
        achievement_tree = json.loads(json.load(file))

    dict_fileName = f"dictionary_40953.json" 
    with open(dict_fileName, "r") as file:
        achievement_hash = json.load(file)

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
        if character_achievements.get(str(achievement_id),{}) is False:       
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
        if character_achievements.get(str(achievement_id),{}) is False:       
            not_completed_achievements.append(achievement_id)
            if achievement_id in all_achievements:
                all_achievements.remove(achievement_id)     

    
"""
    for achievement in achievement_tree.get("children", [])[0]:           
        if character_achievements.get(str(achievement),{}) is False:
            incoming_achievement_ids.append(achievement)
"""
print(f"Found {len(not_completed_achievements)} achievement IDs in the master list that are not marked as completed in the consolidated achievements.")