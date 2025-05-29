# blizzard-api-development-projects
Collection of code built to utilize blizzard's wow api. 

RecurseAchievementTree.py - given a specific user name and realm, it will pull down all the child achievements and return those steps that are still marked incomplete. I wrote this to pull down all the achivements for "A World Awoken" (achivement id = 19548). The final result is a json file and html document that details these incomplete. 

ConsolidateCharacterAchievements.py - Using an array of character-realm combos, it will pull down the JSON their achievement summary and generate a single JSON object. Wanted to test to see if the combined achievements of several characters would provide different results. Overall it changed by maybe 1 or 2 over the total. 

test_compareConolidated.py uses the consolidated json file created above, and runs same logic to combine achievements as recurseAchievementTree.py


