from tips.structures import (Game, GroupTable, Player, TextQuestion, MultiChoiceQuestion, KnockoutQuestion, 
                             SingleChoiceQuestion, Phase, all_team_characters, groups, QUESTION_TYPE_DICT)
from pydantic import BaseModel
import pandas as pd
import re
import textwrap
import os
from tips import config 
from tips.util import rst_toctree, rst_csv_table
from typing import Optional, List
from datetime import datetime, timedelta
import warnings


class Tournament(BaseModel):
    players: List[Player] = []
    facit: Player = None
    max_points: int = 0
    
    def build_players(self, exclude_players: Optional[List[str]] = None):
        
        print(f"EXCLUDING PLAYERS: {exclude_players}")

        group_stage_df = pd.read_csv(f'{config.DATA_DIR}/group_stage_ANSWERS.csv')
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
        
        
        facit_data_df = pd.read_csv(f'{config.DATA_DIR}/group_stage_RESULTS.csv')
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
        
        if name in config.spelling_dict:
            print(f"Found spelling mistake for {name}, using correct spelling {config.spelling_dict[name]} instead.")
            return self.get_player(config.spelling_dict[name])

        return None   

    def add_guesses(self, exclude_players: Optional[List[str]] = None):
        
        if exclude_players is None:
            exclude_players = []

        event_index = 0

        for phase, question_types in config.PHASE_STRUCTURE.items():
            start_column = config.PHASE_STARTING_COLUMN[phase]
            
            try:
                phase_df = pd.read_csv(f'{config.DATA_DIR}/{phase}_ANSWERS.csv')
            except FileNotFoundError:
                print(f"Could not find file for phase {phase}")
                continue
            
            n_players = 0
            for index, row in phase_df.iterrows():
                # Get the player from the name column in the row
                try:
                    name = row["Vad heter du? (För- och efternamn)"].strip()
                except KeyError:
                    name = row["Vad heter du? (Förnamn + efternamn)"].strip()
                if name in exclude_players:
                    continue

                player = self.get_player(name)

                if player is None:
                    warnings.warn(f"Could not find player {name}, so cannot add guesses for {phase}")
                else:
                    try:
                        player.questions[phase] = self.get_questions(row, question_types, start_column = start_column, 
                                                                     start_event_index = event_index, phase = phase, is_facit = False)
                        n_players += 1
                    except Exception as e:
                        raise ValueError(f"problem for player {player.name}")


            print(f"Processed {n_players} players for phase {phase}: {[player.name for player in self.players if phase in player.questions]}")

            try:
                phase_facit_df = pd.read_csv(f'{config.DATA_DIR}/{phase}_RESULTS.csv')
                self.facit.questions[phase] = self.get_questions(phase_facit_df.iloc[0], question_types, start_column = start_column, 
                                                                start_event_index = event_index, phase = phase, is_facit = True)
            except FileNotFoundError:
                print(f"Could not find facit file for phase {phase}")
                # if phase == "bonus":
                #     print(f"No facit file for phase {phase}, but this is expected for bonus phase.")
                #     self.facit.questions[phase] = [None] * len(question_types)
                # else:
                #     raise ValueError(f"Could not find facit file for phase {phase}")

            
            event_index = self.players[0].highest_event_index + 1


    def get_questions(self, row, question_types, start_column, start_event_index, phase, is_facit = False):
        questions = []
        event_index = start_event_index
        
        # if phase == 'group_stage':
        col_i = start_column
        for question_type in question_types:
            question_class, n_columns = QUESTION_TYPE_DICT[question_type]
            if question_type in ( 'group_game', 'knockout_game'):
                knockout_game = (question_type == 'knockout_game')
                
                question = self.get_game(row = row, first_column = col_i, knockout_game = knockout_game,
                                                         event_index = event_index, is_facit = is_facit,
                                                         skip_teams_check = (phase == 'final')
                                                         )
                
            
            elif question_type == 'group_table':
                
                question = self.get_group_table(row = row, first_column = col_i,
                                                    event_index = event_index, is_facit = is_facit)
                

            elif question_type == 'text':
                # print(row.iloc[col_i+1])
                points = '-' if pd.isna(row.iloc[col_i+1]) else row.iloc[col_i+1]
                question = TextQuestion(
                    question = row.index[col_i],
                    answer = row.iloc[col_i],
                    points = points,
                    event_index = event_index,
                    is_facit = is_facit
                )
                
            
            elif question_type == 'multi_choice':
                if (match := re.search(r"Välj (\d+)", row.index[col_i])):
                    n_choices_allowed = int(match.group(1))
                else:
                    raise ValueError(f"Could not find number of choices allowed in question: {row.index[col_i]}")
                
                is_complete = True
                if row.iloc[col_i] == "" or pd.isna(row.iloc[col_i]):
                    if not is_facit:
                        raise ValueError(f"Empty guess for multi-choice question: {row.index[col_i]}")
                    is_complete = False
                    answer = []
                else:
                    answer = row.iloc[col_i].split(", ")
                
                #print(row.index[col_i], row.iloc[col_i])

                question = MultiChoiceQuestion(
                    question = row.index[col_i],
                    answer = answer,
                    number_of_choices_allowed = n_choices_allowed,
                    event_index = event_index,
                    is_facit = is_facit,
                    is_complete = is_complete
                )
            
            elif question_type == 'single_choice':

                is_complete = True
                if row.iloc[col_i] == "" or pd.isna(row.iloc[col_i]):
                    if not is_facit:
                        raise ValueError(f"Empty guess for single-choice question: {row.index[col_i]}")
                    is_complete = False
                    answer = None
                else:
                    answer = row.iloc[col_i]

                #print(f"Creating SingleChoiceQuestion for {row.index[col_i]} with answer {row.iloc[col_i]} and is_facit={is_facit} and is_complete={is_complete}")

                question = SingleChoiceQuestion(
                    question = row.index[col_i],
                    answer = answer,
                    event_index = event_index,
                    is_facit = is_facit,
                    is_complete = is_complete
                )

            elif question_type == 'knockout_question':
                is_complete = True
                if row.iloc[col_i] == "" or pd.isna(row.iloc[col_i]):
                    if not is_facit:
                        raise ValueError(f"Empty guess for knockout question: {row.index[col_i]}")
                    is_complete = False
                    answer = -1
                else:
                    answer = int(re.search(r"(\d+)", row.iloc[col_i]).group(1))

                question = KnockoutQuestion(
                    question = row.index[col_i],
                    answer = answer,
                    event_index = event_index,
                    is_facit = is_facit,
                    is_complete = is_complete)
            
            # print(question)

            questions.append(question)
            
            event_index += 1
            col_i += n_columns

        return questions
    
    def get_game(self, row, first_column, knockout_game, event_index, is_facit, skip_teams_check = False):
        
        score, teams_from_options = [], [] 
        offset = 2 if knockout_game else 0
        for j in range(offset, offset + 2):
            score.append(row.iloc[first_column+j])
            if team_match := re.search(r'\[(.*)\]', row.index[first_column+j]):
                teams_from_options.append(team_match.group(1))
            else:
                raise ValueError(f"Could not find team in {row.index[first_column+j]}")
        
        if not skip_teams_check:
            regex_pattern_question = fr'Hur slutar ([{all_team_characters}]+) +- +([{all_team_characters}]+)\?' if not knockout_game else fr'Vilka vinner mellan ([{all_team_characters}]+) +- +([{all_team_characters}]+)\?'
            if teams_match := re.search(regex_pattern_question, row.index[first_column]):
                teams_from_question = teams_match.groups()
            else:
                raise ValueError(f"Could not find teams in {row.index[first_column]}")
            
            assert all(t_o == t_q for t_o, t_q in zip(teams_from_options, teams_from_question)), f"Teams from options {teams_from_options} do not match teams from question {teams_from_question}"
            # assert team == teams[j-offset], f"Teams do not match: {team} != {teams[j-offset]}"
        
        teams = teams_from_options


        is_complete = True
        # Player guesses must have all scores, but facit can be empty
        if "" in score or any(pd.isna(s) for s in score):
            if not is_facit:
                raise ValueError(f"Empty guess for {teams_from_question}")
            else:
                if not all([(s == "" or pd.isna(s)) for s in score]):
                    raise ValueError(f"Facit has only partial score for game: {teams_from_question}")
                is_complete = False
                score = [-1, -1]

        if knockout_game:
            winner = row.iloc[first_column]
            endtime_form = row.iloc[first_column+1]
            if "" in (endtime_form, winner) or any(pd.isna(s) for s in (endtime_form, winner)):
                if not is_facit:
                    raise ValueError(f"Empty guess for {teams}")
                else:
                    if not all([(s == "" or pd.isna(s)) for s in (endtime_form, winner)]):
                        raise ValueError(f"Facit has only partial answers for game: {teams}")
                    is_complete = False
                    
                    winner, endtime = None, 'invalid'
            # if winner not in teams:
            #     raise ValueError(f"Winner {winner} is not in teams {teams}")
            else:
                endtime = config.endtime_dict[endtime_form]
        else:
            winner = None
            endtime = '90'

        try:
            game = Game(
                teams = teams,
                score = score,
                event_index = event_index,
                knockout_game = knockout_game,
                is_facit = is_facit,
                winner = winner,
                endtime = endtime,
                is_complete = is_complete
            )
        except Exception as e:
            raise ValueError(f"bad data {teams=},{score=},{knockout_game=},{winner=},{endtime=},{is_complete=}")

        return game


    def get_group_table(self, row, first_column, event_index, is_facit = False):
        
        team_positions = []
        
        group = re.search(r'grupp ([ABCDEFGHIJKL])', row.index[first_column]).group(1)
        for j in range(4):
            team = re.search(fr'\[([{all_team_characters}]+)\]', row.index[first_column+j]).group(1)
            team_positions.append((team, row.iloc[first_column+j]))
            
        is_finished, is_valid = True, True
        if "" in [pos for _, pos in team_positions] or any(pd.isna(pos) for _, pos in team_positions):
            if not is_facit:
                raise ValueError(f"Empty guess for group {group}")
            else:
                if not all([((pos == "") or pd.isna(pos)) for _, pos in team_positions]):
                    raise ValueError(f"Facit has only partial positions for group {group}")
                is_finished = False
                    

        if not set([pos for _, pos in team_positions]) == set([1,2,3,4]):
            is_valid = False

        teams_in_order = [team for team, _ in sorted(team_positions, key = lambda x: x[1])]
        return GroupTable(
            teams_in_order = teams_in_order,
            group = group,
            event_index = event_index,
            is_facit = is_facit,
            is_finished = is_finished,
            is_valid = is_valid
        )
        
    
    def compute_points(self, include_phases):
        for player in self.players:
            player.compute_points(self.facit, include_phases)

        self.facit.compute_points(self.facit, include_phases)
        self.max_points = self.facit.total_points
   
    def build_player_guesses_rst(self, directory = "webpage/source", include:Optional[List[Phase]] = None):
        
        if include is None:
            include = []
        
        all_phases = ["group_stage", "last_32", "last_16", "quarter_finals", "semi_finals", "final", "bonus"]

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
        
        player_tuples = []

        for player in self.players:
            score = player.total_points
            nick = player.nick
            if config.TOTAL_GOALS_IN_TOURNAMENT is None:
                knockout_question_diff = None
            else:
                if player.bonus_questions:
                    try:
                        knockout_question_answer = int(re.search(r"(\d+)", player.bonus_questions[-1].answer).group(1))
                    except Exception as e:
                        knockout_question_answer = 0
                else:
                    knockout_question_answer = 0
                knockout_question_diff = abs(knockout_question_answer - config.TOTAL_GOALS_IN_TOURNAMENT)

            player_tuples.append((score, knockout_question_diff, nick))

        players_tuples_sorted = sorted(player_tuples, key = lambda player_tuple: (-player_tuple[0], player_tuple[1],  player_tuple[2].lower()), reverse = False)
        
        now = datetime.now()
        if is_github_action:
            now += timedelta(hours=2)
        
        now_string = now.strftime("%d %B %H:%M")

        home_page_text = textwrap.dedent(
        f"""        
        Välkomna till VM-Tipset 2026!
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
            for player_tuple in players_tuples_sorted:
                f.write(f"\n{player_tuple[2]}, {player_tuple[0]}")

    # def build_rst_stats_page(self, directory = "webpage/source", is_github_action:bool = False):
        
    #     stats_page_text = textwrap.dedent(
    #     f"""        
    #     Statistik
    #     ==================================

    #     Här kan du se lite statistik över tippningen.

    #     .. *(For English, go to the bottom of the page.)*
    #     """)

    #     stats_page_text += rst_toctree(files=["content/stats/accuracy", "content/stats/most_common_guesses"],
    #                                     directives={"hidden": "", "maxdepth": 1})

    #     with open(f"{directory}/content/stats/index.rst", "w") as f:
    #         f.write(stats_page_text)


def parse_data(directory = "webpage/source", exclude_players: Optional[List[str]] = None):


    t = Tournament()
    t.build_players(exclude_players=exclude_players)

    t.add_guesses(exclude_players=exclude_players)

    t.compute_points(config.INCLUDE_PHASES)

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