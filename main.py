from tips.download_data import download_data
from tips.parse_data import parse_data
from datetime import datetime
import os
import json

DOWNLOAD_DATA = os.getenv("DOWNLOAD_DATA", "false")
EXCLUDE_PLAYERS = ["Test1", "Test 1", "Test2", "Test 2", "Test3", "Test 3", "Test 17"]
INCLUDE_PHASES = ["group_stage", "bonus", "last_16", "quarter_finals", "semi_finals"]


IS_GITHUB_ACTION = os.getenv("IS_GITHUB_ACTION", "false")

print(f"DOWNLOAD_DATA: {DOWNLOAD_DATA}")

# Step 1 - Download and parse the data to csv
if DOWNLOAD_DATA == "true":
    download_data()
    
elif DOWNLOAD_DATA == "false":
    pass
else:
    raise ValueError(f"DOWNLOAD_DATA must be either 'true' or 'false'. It is currently set to {DOWNLOAD_DATA}")


# Step 2 - Calculate the scores
tournament = parse_data(exclude_players=EXCLUDE_PLAYERS)

# Step 3 (maybe) - Create statistics plots

# now = datetime.now()
# print(now)


# Step 4 - Use scores to create a leaderboard (either by writing to a csv or modifying rst)

tournament.build_player_guesses_rst(include=INCLUDE_PHASES)
tournament.build_rst_home_page_and_leaderboard(is_github_action = IS_GITHUB_ACTION)
