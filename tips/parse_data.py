from tips.structures import Game, GroupTable, Bonus, Player
from pydantic import BaseModel
import pandas as pd
import re
import textwrap
import os
from tips.data.spelling_dict import spelling_dict
from tips.util import rst_toctree, rst_csv_table
from typing import Optional, List
from datetime import datetime, timedelta
import warnings

endtime_dict = {
    "Efter 90 minuter": "90",
    "Efter 120 minuter": "120",
    "Efter straffar": "penalties"
}

class Tournament(BaseModel):
    players: List[Player] = []
    facit: Player = None
    max_points: int = 0
    
    def build_players(self, exclude_players: Optional[List[str]] = None):
        
        print(f"EXCLUDING PLAYERS: {exclude_players}")

        group_stage_df = pd.read_csv('tips/data/group_stage_ANSWERS.csv')
        # print(group_stage_df)

        if exclude_players is None:
            exclude_players = []

        # print(group_stage_df.columns)

        # self.players = []
        for index, row in group_stage_df.iterrows():
            player = Player(
                name = row["Vad heter du? (För- och efternamn)"].strip(),
                nick= row["Vad vill du ha för smeknamn i tipset?"].strip(),
                email= row["E-postadress"],
                is_facit = False
            )
            if player.name in exclude_players:
                pass
            else:
                self.players.append(player)
        
        
        facit_data_df = pd.read_csv('tips/data/group_stage_RESULTS.csv')
        self.facit = Player(
            name = facit_data_df.iloc[0]["Vad heter du? (För- och efternamn)"],
            nick = facit_data_df.iloc[0]["Vad vill du ha för smeknamn i tipset?"],
            email = facit_data_df.iloc[0]["E-postadress"],
            is_facit = True
        )
    
    def get_player(self, name):
        for player in self.players:
            if player.name == name:
                return player

        for player in self.players:
            if player.nick == name:
                return player
        
        if name in spelling_dict:
            print(f"Found spelling mistake for {name}, using correct spelling {spelling_dict[name]} instead.")
            return self.get_player(spelling_dict[name])

        return None   

    def add_guesses(self, exclude_players = Optional[List[str]]):
        
        

        if exclude_players is None:
            exclude_players = []

        event_index = 0

        for phase in ['group_stage', 'last_16', 'quarter_finals', 'semi_finals', 'final']:
            
            try:
                phase_df = pd.read_csv(f'tips/data/{phase}_ANSWERS.csv')
                print(f"Adding guesses for phase {phase}")
            except FileNotFoundError:
                print(f"Could not find file for phase {phase}")
                continue

            for index, row in phase_df.iterrows():
                name = row["Vad heter du? (För- och efternamn)"].strip()
                if name in exclude_players:
                    continue

                player = self.get_player(name)

                if player is None:
                    warnings.warn(f"Could not find player {name}, so cannot add guesses for {phase}")
                else:
                    try:
                        player.games[phase] = self.get_games(row, phase = phase, start_event_index = event_index)
                    except Exception as e:
                        raise ValueError(f"problem for player {player.name}")

            phase_facit_df = pd.read_csv(f'tips/data/{phase}_RESULTS.csv')
            phase_facit_df.fillna("", inplace=True)
            self.facit.games[phase] = self.get_games(phase_facit_df.iloc[0], phase = phase, start_event_index = event_index, facit = True)
            
            event_index = self.players[0].highest_event_index + 1

            if phase == 'group_stage':
                for index, row in phase_df.iterrows():
                    name = row["Vad heter du? (För- och efternamn)"].strip()
                    if name in exclude_players:
                        continue
                    player = self.get_player(name)
                    player.group_tables = self.get_group_tables(row, start_event_index = event_index)


                self.facit.group_tables = self.get_group_tables(phase_facit_df.iloc[0], start_event_index = event_index, facit = True)

                event_index = self.players[0].highest_event_index + 1

        # Add bonus
        bonus_df = pd.read_csv('tips/data/bonus_ANSWERS.csv')
        for index, row in bonus_df.iterrows():
            name = row["Vad heter du? (För- och efternamn)"].strip()
            if name in exclude_players:
                continue
            player = self.get_player(name)

            if player is None:
                warnings.warn(f"Could not find player {name}, so cannot add bonus guesses")
            else:
                player.bonus_questions = self.get_bonus(row, start_event_index = event_index)
        
        self.facit.bonus_questions = self.get_bonus(phase_facit_df.iloc[0], start_event_index = event_index, facit = True)


    def get_games(self, row, phase, start_event_index, facit = False):
        games = []
        event_index = start_event_index
        if phase == 'group_stage':
            for i in range(4, 75, 2):
                score = []
                if teams_match := re.search(r' ([A-Za-zÅåÄäÖö]+) +- +([A-Za-zÅåÄäÖö]+)', row.index[i]):
                    teams = teams_match.groups()
                else:
                    raise ValueError(f"Could not find teams in {row.index[i]}")
                
                for j in range(2):
                    score.append(row.iloc[i+j])
                    if team_match := re.search(r'\[(.*)\]', row.index[i+j]):
                        team = team_match.group(1)
                    else:
                        raise ValueError(f"Could not find team in {row.index[i+j]}")
                    assert team == teams[j], f"Teams do not match: {team} != {teams[j]}"
                
                # Player guesses must have all scores, but facit can be empty
                if "" in score:
                    if not facit:
                        raise ValueError(f"Empty guess for {teams}")
                    else:
                        if not all([s == "" for s in score]):
                            raise ValueError(f"Facit has only partial score for game: {teams}")
                        break
                # print(type(score[0]))

                games.append(Game(
                    teams = teams,
                    score = score,
                    event_index = i,
                    phase = phase,
                    facit = facit
                ))
                event_index += 1
                
        elif phase in ("last_16", "quarter_finals", "semi_finals"):
            for i in range(2, 34, 4):
                score = []
                if teams_match := re.search(r' ([A-Za-zÅåÄäÖö]+) *- *([A-Za-zÅåÄäÖö]+)', row.index[i]):
                    teams = teams_match.groups()
                else:
                    raise ValueError(f"Could not find teams in {row.index[i]}")
                
                for j in range(2):
                    score.append(row.iloc[i+j+2])
                    if team_match := re.search(r'\[(.*)\]', row.index[i+j+2]):
                        team = team_match.group(1)
                    else:
                        raise ValueError(f"Could not find team in {row.index[i+j+2]}")
                    assert team == teams[j], f"Teams do not match: {team} != {teams[j]}"
                
                winner = row.iloc[i]
                endtime_form = row.iloc[i+1]
                
                # Player guesses must have all scores, but facit can be empty
                if "" in score or "" in (endtime_form, winner):
                    if not facit:
                        raise ValueError(f"Empty guess for {teams}")
                    else:
                        if not all([s == "" for s in score]):
                            raise ValueError(f"Facit has only partial score for game: {teams}")
                        break
                # print(type(score[0]))
                endtime = endtime_dict[endtime_form]
                try:
                    games.append(Game(
                    teams = teams,
                    score = score,
                    event_index = i,
                    phase = phase,
                    facit = facit,
                    winner = winner,
                    endtime = endtime

                ))
                except Exception as e:
                    raise ValueError(f"bad data {teams},{score},{phase},{winner},{endtime},")
                event_index += 1

        else:
            raise ValueError(f"Unknown phase {phase}")

        return games
    

    def get_group_tables(self, row, start_event_index, facit = False):
        group_tables = []
        event_index = start_event_index
        for i in range(76, 99, 4):
            team_positions = []
            # print(row.index[i])
            group = re.search(r'grupp ([ABCDEF])', row.index[i]).group(1)
            for j in range(4):
                team = re.search(r'\[([A-Za-zÅåÄäÖö]+)\]', row.index[i+j]).group(1)
                team_positions.append((team, row.iloc[i+j]))
            
            if "" in [pos for _, pos in team_positions]:
                if not facit:
                    raise ValueError(f"Empty guess for group {group}")
                else:
                    if not all([pos == "" for _, pos in team_positions]):
                        raise ValueError(f"Facit has only partial positions for group {group}")
                    break

            teams_in_order = [team for team, _ in sorted(team_positions, key = lambda x: x[1])]
            group_tables.append(GroupTable(
                teams_in_order = teams_in_order,
                group = group,
                event_index = event_index,
                facit = facit
            ))
            event_index += 1
                
        return group_tables

    def get_bonus(self, row, start_event_index, facit = False):
        bonus = []
        event_index = start_event_index
        for i in range(2, len(row)):
            bonus.append(Bonus(
                question = row.index[i],
                answer = str(row.iloc[i]),
                event_index = event_index,
                facit = facit
            ))
            event_index += 1
        
        return bonus
    
    def compute_points(self):
        for player in self.players:
            player.compute_points(self.facit)

        self.facit.compute_points(self.facit)
        self.max_points = self.facit.total_points
   
    def build_player_guesses_rst(self, directory = "webpage/source", include:Optional[List[str]] = None):
        
        if include is None:
            include = []
        
        all_phases = ["group_stage", "last_16", "quarter_finals", "semi_finals", "final", "bonus"]

        if not all([phase in all_phases for phase in include]):
            invalid_phases = set(include) - set(all_phases)
            raise ValueError(f"Found invalid phases: {invalid_phases}")
        
        
        root_index_rst_string = textwrap.dedent(
        f"""        Deltagare
        ==========

        Här kan du se alla deltagare i tävlingen. Du kan även se vad de har tippat
        efter att alla tips har kommit in.
        """)

        player_toctree_files = []

        for player in self.players:
            player.build_guess_rst(directory = os.path.join(directory, "content/players"), include = include)
            
            player_toctree_files.append(f"{player.nick}/index")
            # root_index_rst_string += f"    {player.nick}/index\n"
        
        root_index_rst_string += rst_toctree(player_toctree_files,
                                             directives={"maxdepth": 1}
                                             )

        with open(os.path.join(directory, "content/players/index.rst"), "w") as f:
            f.write(root_index_rst_string)

    def build_rst_home_page_and_leaderboard(self, directory = "webpage/source", is_github_action:bool = False):
        
        players_sorted = sorted(self.players, key = lambda player: (-player.total_points, player.nick.lower()), reverse = False)
        
        now = datetime.now()
        if is_github_action:
            now += timedelta(hours=2)
        
        now_string = now.strftime("%d %B %H:%M")

        home_page_text = textwrap.dedent(
        f"""        
        Välkomna till EM-Tipset 2024!
        ==================================

        .. *(For English, go to the bottom of the page.)*
        """)

        home_page_text += rst_csv_table("content/leaderboard.csv", 
                    title = f"Poängställning (Uppdaterad {now_string})",
                    directives={"widths": "70, 30", "header-rows": 1}
                    ) + "\n"

        home_page_text += rst_toctree(files=["content/rules", "content/forms", "content/players/index"],
                                        directives={"hidden": "", "maxdepth": 1})


        with open(f"{directory}/index.rst", "w") as f:
            f.write(home_page_text)
                
        
        with open(f"{directory}/content/leaderboard.csv", "w") as f:
            f.write(f"Namn, Poäng (Max {self.max_points})")
            for player in players_sorted:
                f.write(f"\n{player.nick}, {player.total_points}")

def parse_data(directory = "webpage/source", exclude_players: Optional[List[str]] = None):
    t = Tournament()
    t.build_players(exclude_players=exclude_players)

    t.add_guesses(exclude_players=exclude_players)

    t.compute_points()

    return t


# if __name__ == "__main__":
#     import time
#     # parse_data()
#     now = datetime.now()
#     print(now)
#     print(dir(now))
#     # time.sleep(5)
#     print(now.time())
#     print(now.hour)
#     print(now.minute)
#     print(now.second)
#     print(now.day)
#     print(now.month)    