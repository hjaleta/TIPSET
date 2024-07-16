from tips.download_data import download_data
from tips.parse_data import parse_data
from datetime import datetime
import os
import json
from tips.config import (DOWNLOAD_DATA, 
                         EXCLUDE_PLAYERS, 
                         INCLUDE_PHASES, 
                         IS_GITHUB_ACTION)



print(f"DOWNLOAD_DATA: {DOWNLOAD_DATA}")

# Step 1 - Download and parse the data to csv
if DOWNLOAD_DATA == "true":
    download_data()
    
elif DOWNLOAD_DATA == "false":
    pass
else:
    raise ValueError(f"DOWNLOAD_DATA must be either 'true' or 'false'. It is currently set to {DOWNLOAD_DATA}")


# Step 2 - Calculate the scores
tournament = parse_data(exclude_players=EXCLUDE_PLAYERS, include_phases = INCLUDE_PHASES)

# Step 3 (maybe) - Create statistics plots

# now = datetime.now()
# print(now)


# Step 4 - Use scores to create a leaderboard (either by writing to a csv or modifying rst)

tournament.build_player_guesses_rst(include=INCLUDE_PHASES)
tournament.build_rst_home_page_and_leaderboard(is_github_action = IS_GITHUB_ACTION)
