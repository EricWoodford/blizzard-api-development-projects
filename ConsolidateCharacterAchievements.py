# read all of the character_achivement.json files in the directory
import json
import os
# compare similar achievements in each of the files.
# createa list of all ahcievement ids, and if ANY of the json files are marked true for that achievement, mark it as true in the output.
import glob     
import sys

if __name__ == "__main__":
    try:
        # get a list of all json files in the current directory
        json_files = glob.glob("*character_achievements.json")        
        print(f"Found {len(json_files)} character_achievements.json files.")
        if not json_files:
            print("No character_achievements.json files found in the current directory.")
            sys.exit(1)
        consolidated_achievements = {}
        for file in json_files:
            with open(file, 'r') as f:
                data = json.load(f)
                for achievement in data.get('achievements', []):
                    achievement_id = achievement.get('id')
#                    print(achievement)
                    if achievement_id is not None:
                        if achievement_id not in consolidated_achievements:
                            consolidated_achievements[achievement_id] = False
                        if "criteria" in achievement and isinstance(achievement.get("criteria"), dict):
                            if achievement.get("criteria", {}).get('is_completed', False) == True and not consolidated_achievements[achievement_id]:
                                print(achievement_id, file)
                                consolidated_achievements[achievement_id] = True
        # dump json to a file
        sorted_achievements = dict(sorted(consolidated_achievements.items()))
        with open('consolidated_achievements.json', 'w') as outfile:
            json.dump(sorted_achievements, outfile, indent=4)
        """ 
        print("Consolidated Achievements:")
        
        for achievement_id, completed in consolidated_achievements.items():
        if completed:
            # Only print achievements that are completed
            print(f"Achievement ID: {achievement_id}, Completed: {completed}")
        """
    finally:
        if not json_files:
            print("No character_achievements.json files found in the current directory.")
            sys.exit(1)