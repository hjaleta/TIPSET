import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

# Teams in World Cup 2022

ROOTDIR = "tips/"



if True:
    grupper = {
        "A": {"QAT": "Qatar", "ECU":"Ecuador", "SEN": "Senegal", "HOL":"Nederländerna"},
        "B": {"ENG": "England", "IRA": "Iran", "USA": "USA", "WAL": "Wales"},
        "C": {"ARG": "Argentina", "SDA": "Saudiarabien", "MEX": "Mexiko", "POL": "Polen"},
        "D": {"FRA": "Frankrike", "AUS": "Australien", "DAN": "Danmark", "TUN": "Tunisien"},
        "E": {"SPA": "Spanien", "CTR": "Costa Rica", "TYS": "Tyskland", "JAP": "Japan"},
        "F": {"BEL": "Belgien", "KAN": "Kanada", "MAR": "Marocko", "KRO": "Kroatien"},
        "G": {"BRA": "Brasilien", "SER": "Serbien", "SUI": "Schweiz", "KAM": "Kamerun"},
        "H": {"POR": "Portugal", "GHA": "Ghana", "URU": "Uruguay", "SDK": "Sydkorea"}
    }

    landskod_land_dict = {}
    land_landskod_dict = {}
    landskod_grupp_dict = {}

    for grupp_bokstav, lag_dict in grupper.items():
        for landskod, land in lag_dict.items():
            landskod_land_dict[landskod] = land
            land_landskod_dict[land] = landskod
            landskod_grupp_dict[landskod] = grupp_bokstav
# from Data.VM2022.teams import *

class Game:
    def __init__(self, teams, result, phase, endtime = None, winner=None, invalid = False):
        self.teams = teams
        self.group = self.get_group()
        self.result = result
        self.phase = phase
        self.invalid = invalid
        if not invalid:
            assert endtime in (None, "Efter 90 minuter", "Efter 120 minuter", "Efter straffar"), f"Invalid endtime: {endtime} for game {self.teams}"
        self.endtime = endtime
        self.winner = self.get_winner(winner)

        self.points = None

    def get_group(self):
        return landskod_grupp_dict[land_landskod_dict[self.teams[0]]]
        
    def get_winner(self, winner):

        if isinstance(winner, str):
            if winner == self.teams[0]:
                return '1'
            elif winner == self.teams[1]:
                return '2'
            else:
                raise ValueError("Winner not in teams")
            

        elif (winner is None):
            if None in self.result:
                return None
            if self.result[0] > self.result[1]:
                return '1'
            elif self.result[0] == self.result[1]:
                return 'X'
            elif self.result[0] < self.result[1]:
                return '2'
        else:
            raise ValueError("Winner is neither string nor None")
    
    def set_points(self, facit_game):
        points = 0
        
        if not self.invalid:
            if not (self.endtime is None) and self.endtime == facit_game.endtime:
                points += 1
            if self.winner == facit_game.winner:
                points += 1
            if self.result == facit_game.result:
                points += 1
        
        self.points = points
        
    # def __str__(self):
    #     s = f'{country_codes_inv[self.teams[0]]} - {country_codes_inv[self.teams[1]]}: {self.result[0]} - {self.result[1]}'
    #     if self.endtime in ("90", "120"):
    #         s += f' efter {self.endtime} minuter'
    #     elif self.endtime == "straffar":
    #         if self.winner  == '1':
    #             winner_index = 0
    #         elif self.winner == '2':
    #             winner_index = 1
    #         s +=  f'efter 120 minuter, {country_codes_inv[self.teams[winner_index]]} vinner på sraffar'
    #     return s

class GroupTable:
    def __init__(self, teams_in_order, group_letter, invalid = False):
        self.teams_in_order = teams_in_order
        self.group_letter = group_letter
        self.invalid = invalid
        self.points = None

    def set_points(self, facit):
        if not self.invalid:
            correct_teams = 0
            for team, facit_team in zip(self.teams_in_order, facit.teams_in_order):
                if team == facit_team:
                    correct_teams += 1
            
            if correct_teams == 4:
                self.points = 3
            else:
                self.points = correct_teams


# class Group:
#     def __init__(self, games, group_key):
#         if len(games) != 6:
#             raise(ValueError('Blurg'))
#         self.group_key = group_key
#         self.table = self.extract_table(games)
#         self.order = self.get_order()
#         for team in self.table:
#             print(team, self.table[team])
#         print(self.order)

#     def extract_table(self, games):
#         table = {team:{'points':0, 'pointd':0, 'conceded':0, 'won':0, 'tie':0, 'lost':0} for team in grupper[self.group_key]}
    
#         for game in games:
#             team1, team2 = game.teams
#             table[team1]['pointd'] += game.result[0]
#             table[team2]['conceded'] += game.result[0]
#             table[team1]['conceded'] += game.result[1]
#             table[team2]['pointd'] += game.result[1]
#             if game.winner == '1':
#                 table[team1]['points'] += 3
#                 table[team1]['won'] += 1
#                 table[team2]['lost'] += 1
#             elif game.winner == 'X':
#                 table[team1]['points'] += 1
#                 table[team2]['points'] += 1
#                 table[team1]['tie'] += 1
#                 table[team2]['tie'] += 1
#             elif game.winner == '2':
#                 table[team2]['points'] += 3
#                 table[team2]['won'] += 1
#                 table[team1]['lost'] += 1
#         return table
    
#     def get_order(self):

#         prios = [(team, self.table[team]['points'], self.table[team]['pointd'] - self.table[team]['conceded'], self.table[team]['pointd']) for team in self.table]
#         prios.sort(reverse = True, key = lambda t: t[1] * 10000 + t[2]*100 + t[3])
#         order = [prio[0] for prio in prios]
#         return order

class Gambler:
    def __init__(self, name,  nick):
        self.name = name
        self.nick = nick
        self.bets = {}
        self.total_points = 0
        self.all_points_list = []
        

    def compute_points(self, facit):
        
        # self.compute_bonus_points(facit)
        
        self.compute_group_table_points(facit)
        self.knockout_game_points = {"8-delsfinaler":0,
                                     "Kvartsfinaler": 0,
                                     "Semifinaler": 0}
        for knockout_phase in ("8-delsfinaler", "Kvartsfinaler", "Semifinaler"):
            self.compute_knockout_game_points(facit, knockout_phase)
            
        self.compute_final_bronze_game_points(facit)
        self.compute_group_game_points(facit)

        assert self.total_points == sum(self.all_points_list), f"Player {self.name} has {self.total_points} points, but the sum of self.all_points_list is {sum(self.all_points_list)}"

        
    
    def compute_group_game_points(self, facit):
        self.group_game_points = 0
        for gambler_game, facit_game in zip(self.bets['Gruppspel - Matcher'], facit.bets['Gruppspel - Matcher']):
            if not facit_game.invalid:
                # gambler_game = self.bets['Gruppspel - Matcher'][g_i]
                gambler_game.set_points(facit_game)
                self.group_game_points += gambler_game.points
                self.all_points_list.append(gambler_game.points)
        
        self.total_points += self.group_game_points

    def compute_group_table_points(self, facit):
        self.group_table_points = 0
        for gambler_table, facit_table in zip(self.bets['Gruppspel - Tabeller'], facit.bets['Gruppspel - Tabeller']):
            if not facit_table.invalid:
                gambler_table.set_points(facit_table)
                self.group_table_points += gambler_table.points
                self.all_points_list.append(gambler_table.points)
            else:
                pass
        
        self.total_points += self.group_table_points

    def compute_knockout_game_points(self, facit, knockout_phase):
        self.knockout_game_points[knockout_phase] = 0
        if self.bets.get(knockout_phase) != None:
            for gambler_game, facit_game in zip(self.bets[knockout_phase], facit.bets[knockout_phase]):
                if not facit_game.invalid:
                    # gambler_game = self.bets['Gruppspel - Matcher'][g_i]
                    gambler_game.set_points(facit_game)
                    self.knockout_game_points[knockout_phase] += gambler_game.points
                    self.all_points_list.append(gambler_game.points)
                else:
                    print(f'Invalid facit for game {facit_game.teams}')
        else:
            print(f'No bets from {self.name} for {knockout_phase}')
            for _ in range(len(facit.bets[knockout_phase])):
                self.all_points_list.append(0)
        self.total_points += self.knockout_game_points[knockout_phase]

    def compute_final_bronze_game_points(self, facit):
        self.final_bronze_game_points = 0
        if self.bets.get("Final + Brons") != None:
            for gambler_game, facit_game in zip(self.bets["Final + Brons"][0], facit.bets["Final + Brons"][0]):
                if not facit_game.invalid:
                    # gambler_game = self.bets['Gruppspel - Matcher'][g_i]
                    gambler_game.set_points(facit_game)
                    self.final_bronze_game_points += gambler_game.points
                else:
                    print(f'Invalid facit for game {facit_game.teams}')
            if self.bets["Final + Brons"][1] == facit.bets["Final + Brons"][1]:
                self.final_bronze_game_points += 1
            if self.bets["Final + Brons"][2] == facit.bets["Final + Brons"][2]:
                self.final_bronze_game_points += 1
            self.final_bronze_game_points += int(self.bets["Final + Brons"][3])
        else:
            print(f'No bets from {self.name} for Final + Brons')
        self.all_points_list.append(self.final_bronze_game_points)
        self.total_points += self.final_bronze_game_points

    def print_bets(self):

        for phase in self.bets:
            if self.bets[phase] != None:
                print(phase,'\n')
                if phase == 'gruppspel':
                    for i, game in enumerate(self.bets[phase]):
                        if i % 3 == 2:
                            print(game)
                        else:
                            print(game, end = '\t')
                else:
                    for game in self.bets[phase]:
                        print(game)
                print('\n')

    def print_point(self):
        s = ''
        for phase in self.bets:
            if self.bets[phase] != None:
                if phase == 'gruppspel':
                    s += f'{phase}:\tSubmitted\tpoint:\t{self.points[phase]}\n'
                else:
                    s += f'{phase}:\t\tSubmitted\tpoint:\t{self.points[phase]}\n'
            else:
                s += f'{phase}:\t\tNot submitted\tpoint:\t{self.points[phase]}\n'

        print(s)
        
class Tournament():
    path_dict = {
        "Gruppspel - Matcher":              ROOTDIR + "Data/VM2022/Gruppspelet_matcher.csv",
        "Gruppspel - Matcher - Facit":      ROOTDIR + "Data/VM2022/Gruppspelet_matcher_facit.csv",
        "Gruppspel - Tabeller":             ROOTDIR + "Data/VM2022/Gruppspelet_tabeller.csv",
        "Gruppspel - Tabeller - Facit":     ROOTDIR + "Data/VM2022/Gruppspelet_tabeller_facit.csv",
        "8-delsfinaler":                    ROOTDIR + "Data/VM2022/L16-22.csv",
        "8-delsfinaler - Facit":            ROOTDIR + "Data/VM2022/L16-22_facit.csv",
        "Kvartsfinaler":                    ROOTDIR + "Data/VM2022/Kvartsfinaler.csv",
        "Kvartsfinaler - Facit":            ROOTDIR + "Data/VM2022/Kvartsfinaler_facit.csv",
        "Semifinaler":                      ROOTDIR + "Data/VM2022/Semifinaler.csv",
        "Semifinaler - Facit":              ROOTDIR + "Data/VM2022/Semifinaler_facit.csv",
        "Final + Brons":                    ROOTDIR + "Data/VM2022/Final_Brons.csv",
        "Final + Brons - Facit":            ROOTDIR + "Data/VM2022/Final_Brons_facit.csv",

        "Bonus":                            ROOTDIR + "Data/VM2022/Bonus_resultat.csv",
        "Bonus - Facit":                    None,
    }
    group_game_reg = r"Hur slutar (.*)\?"
    group_table_reg = r"Hur slutar grupp ([A-Z]) \(1-4\) \[(.*)\]"
    knockout_game_reg = r"\d[a-z]\."
    knockout_game_reg_2 = r"\d[a-z]\. Vilka vinner mellan (.*)\?"

    def __init__(self):
        
        self.df_dict = self.get_df_dict()
        self.gamblers, self.facit_gambler = self.init_gamblers_and_facit()
        self.get_bets_and_facit()
        self.compute_points()
    
    def compute_points(self):
        for gambler in self.gamblers:
            gambler.compute_points(self.facit_gambler)
        self.compute_bonus_points()
        for gambler in self.gamblers:
            gambler.point_evolution = np.cumsum(gambler.all_points_list)
        
    def get_df_dict(self):
        df_dict = {}
        for key, path in self.path_dict.items():
            if path != None:
                try:
                    df_dict[key] = pd.read_csv(path)
                except:
                    raise Exception(f'Could not read {path}')
                # df_dict[key] = pd.read_csv(path)
        return df_dict

    def init_gamblers_and_facit(self):
        gamblers = []
        
        starting_df = self.df_dict['Gruppspel - Matcher']
        namn_df = starting_df.filter(like="Vad")

        for row in namn_df.iterrows():
            name = row[1][0].strip()
            nick = row[1][1].strip()
            gamblers.append(Gambler(name, nick))
        
        facit_gambler = Gambler('Facit', 'FCT')
        return gamblers, facit_gambler

    def get_bets_and_facit(self):

        self.get_group_game_bets_and_facit()
        self.get_group_table_bets_and_facit()
        for knockout_phase in ("8-delsfinaler", "Kvartsfinaler", "Semifinaler"):
            self.get_knockout_game_bets_and_facit(knockout_phase)
        self.get_final_bronze_game_bets_and_facit()
        # self.get_bonus_points()
        

    def compute_bonus_points(self):
        bonus_df = self.df_dict['Bonus']

        for _, gambler_row in bonus_df.iterrows():
            gambler_name = gambler_row['Vad heter du? (För- och efternamn)'].strip()
            bonus_points = int(gambler_row['Bonuspoäng'][:-1])
            # games, gambler_name = self.get_group_games_from_row(gambler_row)            
                
            found_gambler = False
            for gambler in self.gamblers:
                if gambler.name.lower() == gambler_name.lower():
                    gambler.bonus_points = bonus_points
                    gambler.total_points += bonus_points
                    gambler.all_points_list.append(bonus_points)
                    found_gambler = True
                    break
            
            if not found_gambler:
                raise ValueError(f'Could not find gambler {gambler_name} in list of Gambler objects')
    

    def get_bonus_points_from_row(self, row):
        name = row['Vad heter du? (För- och efternamn)'].strip()
        bonus_points = row['Bonuspoäng']
        matcher = row.filter(like="Hur slutar")

        games = []
        for i, label in enumerate(matcher.index):
            
            if i % 2 == 0:
                try:
                    team1_point = int(matcher[label])
                except:
                    team1_point = None
            else:
                try:
                    team2_point = int(matcher[label])
                except:
                    team2_point = None
                try:
                    # print(label)
                    teams_string = re.match(self.group_game_reg, label).group(1) 
                except:
                    # print(label)
                    # print(name)
                    raise ValueError(f'Could not find team names in label {label}')
                team1, team2 = teams_string.split(" - ")
                
                if None in (team1_point, team2_point):
                    game = Game((team1, team2), (team1_point, team2_point), "gruppspel", invalid = True)
                    if name != "Facit":
                        print(f'Gambler {name} submitted an invalid answer for the game {teams_string}: {team1_point} - {team2_point}')
                else:
                    game = Game((team1, team2), (team1_point, team2_point), "gruppspel")
                games.append(game)
            
        return games, name 

    def get_group_game_bets_and_facit(self):

        grupp_match_df = self.df_dict['Gruppspel - Matcher']
        
        for _, gambler_row in grupp_match_df.iterrows():
            
            games, gambler_name = self.get_group_games_from_row(gambler_row)            
                
            found_gambler = False
            for gambler in self.gamblers:
                if gambler.name.lower() == gambler_name.lower():
                    gambler.bets['Gruppspel - Matcher'] = games
                    found_gambler = True
                    break
            
            if not found_gambler:
                raise ValueError(f'Could not find gambler {gambler_name} in list of Gambler objects')

        grupp_match_facit_df = self.df_dict['Gruppspel - Matcher - Facit']

        for i, facit_row in grupp_match_facit_df.iterrows():
            games, _ = self.get_group_games_from_row(facit_row)
            self.facit_gambler.bets['Gruppspel - Matcher'] = games

            if i != 0:
                raise ValueError('Facit df should only have one row')

    def get_group_games_from_row(self, row):
        name = row['Vad heter du? (För- och efternamn)'].strip()
        matcher = row.filter(like="Hur slutar")

        games = []
        for i, label in enumerate(matcher.index):
            
            if i % 2 == 0:
                try:
                    team1_point = int(matcher[label])
                except:
                    team1_point = None
            else:
                try:
                    team2_point = int(matcher[label])
                except:
                    team2_point = None
                try:
                    # print(label)
                    teams_string = re.match(self.group_game_reg, label).group(1) 
                except:
                    # print(label)
                    # print(name)
                    raise ValueError(f'Could not find team names in label {label}')
                team1, team2 = teams_string.split(" - ")
                
                if None in (team1_point, team2_point):
                    game = Game((team1, team2), (team1_point, team2_point), "gruppspel", invalid = True)
                    if name != "Facit":
                        print(f'Gambler {name} submitted an invalid answer for the game {teams_string}: {team1_point} - {team2_point}')
                else:
                    game = Game((team1, team2), (team1_point, team2_point), "gruppspel")
                games.append(game)
            
        return games, name
    
    def get_group_table_bets_and_facit(self):

        grupp_tabell_df = self.df_dict["Gruppspel - Tabeller"]
        
        for _, gambler_row in grupp_tabell_df.iterrows():
            
            tables, gambler_name = self.get_group_tables_from_row(gambler_row)            
                
            found_gambler = False
            for gambler in self.gamblers:
                if gambler.name.lower() == gambler_name.lower():
                    gambler.bets["Gruppspel - Tabeller"] = tables
                    found_gambler = True
                    break
            
            if not found_gambler:
                raise ValueError(f'Could not find gambler {gambler_name} in list of Gambler objects')

        grupp_tabell_facit_df = self.df_dict["Gruppspel - Tabeller - Facit"]

        for i, facit_row in grupp_tabell_facit_df.iterrows():
            tables, _ = self.get_group_tables_from_row(facit_row)
            self.facit_gambler.bets['Gruppspel - Tabeller'] = tables

            if i != 0:
                raise ValueError('Facit df should only have one row')

    def get_group_tables_from_row(self, row):
        name = row['Vad heter du? (För- och efternamn)'].strip()
        tabeller = row.filter(like="Hur slutar")

        if name=="Facit":
            # print("TABELLER",tabeller)
            pass

        group_tables = []
        for i, label in enumerate(tabeller.index):

            team_group_index = i %4
            table_match = re.match(self.group_table_reg, label)
            if team_group_index == 0:
                team_positions = [None]*4
                group_letter = table_match.group(1)

            team_name = re.match(self.group_table_reg, label).group(2)
            try:
                team_position = int(tabeller[label])
            except:
                team_position = None
            team_positions[team_group_index] = (team_name, team_position)

            if i%4 == 3:
                all_positions = [position for team, position in team_positions]
                # team_position.sort
                if None in all_positions or len(set(all_positions)) != 4:
                    table = GroupTable(group_letter, team_positions, invalid = True)
                    if name != "Facit":
                        print(f'Gambler {name} submitted an invalid answer for the table {group_letter}: {team_positions}')
                else:
                    team_positions.sort(key=lambda x: x[1])
                    teams_in_order = [team for team, position in team_positions]
                    table = GroupTable(teams_in_order, group_letter)
                group_tables.append(table)
        
        return group_tables, name

    def get_knockout_game_bets_and_facit(self, knockout_phase):
        slutspel_df = self.df_dict[knockout_phase]
        for _, gambler_row in slutspel_df.iterrows():
            
            games, gambler_name = self.get_knockout_games_from_row(gambler_row, knockout_phase)            
                
            found_gambler = False
            for gambler in self.gamblers:
                # print(gambler.name)
                
                if gambler.name.lower() == gambler_name.lower():
                    gambler.bets[knockout_phase] = games
                    found_gambler = True
                    break
            
            if not found_gambler:
                
                raise ValueError(f'Could not find gambler {gambler_name} in phase {knockout_phase} list of Gambler objects')

        slutspel_facit_df = self.df_dict[f'{knockout_phase} - Facit']

        for i, facit_row in slutspel_facit_df.iterrows():
            games, _ = self.get_knockout_games_from_row(facit_row, knockout_phase)
            self.facit_gambler.bets[knockout_phase] = games

            if i != 0:
                raise ValueError('Facit df should only have one row')

    def get_knockout_games_from_row(self, row, knockout_phase):
        name = row['Vad heter du? (För- och efternamn)'].strip()
        svar = row.filter(regex =self.knockout_game_reg)

        games = []
        for i, label in enumerate(svar.index):
            if i % 4 == 0:
                try:
                    teams_string = re.search(self.knockout_game_reg_2, label).group(1)
                except:
                    raise ValueError(f'Could not find team names in label {label}, {name}')
                team1, team2 = teams_string.split(" - ")
                try:
                    winner = svar[label]
                except:
                    winner = None
            elif i % 4 == 1:
                try:
                    endtime = svar[label]
                except:
                    endtime = None
            elif i % 4 == 2:
                try:
                    team1_point = int(svar[label])
                except:
                    team1_point = None
            elif i % 4 == 3:
                try:
                    team2_point = int(svar[label])
                except:
                    team2_point = None
                
                if None in (winner, endtime, team1_point, team2_point):
                    game = Game((team1, team2), (team1_point, team2_point), knockout_phase, winner, invalid = True)
                    if name != "Facit":
                        print(f'Gambler {name} submitted an invalid answer for the game {teams_string}: {team1_point} - {team2_point}')
                else:
                    game = Game((team1, team2), (team1_point, team2_point), knockout_phase, endtime, winner)
                games.append(game)
            
        return games, name

    def get_final_bronze_game_bets_and_facit(self):
        final_bronze_df = self.df_dict["Final + Brons"]
        for _, gambler_row in final_bronze_df.iterrows():
            
            games, corners, extra_time, goal_scorerer_points, gambler_name = self.get_final_bronze_from_row(gambler_row)            
                
            found_gambler = False
            for gambler in self.gamblers:
                # print(gambler.name)
                
                if gambler.name.lower() == gambler_name.lower():
                    gambler.bets["Final + Brons"] = (games, corners, extra_time, goal_scorerer_points)
                    found_gambler = True
                    break
            
            if not found_gambler:
                
                raise ValueError(f'Could not find gambler {gambler_name} in Final + Brons list of Gambler objects')

        slutspel_facit_df = self.df_dict['Final + Brons - Facit']

        for i, facit_row in slutspel_facit_df.iterrows():
            games, corners, extra_time, goal_scorerer_points, _ = self.get_final_bronze_from_row(facit_row)
            self.facit_gambler.bets["Final + Brons"] = (games, corners, extra_time, goal_scorerer_points)

            if i != 0:
                raise ValueError('Facit df should only have one row')

    def get_final_bronze_from_row(self, gambler_row):
        name = gambler_row['Vad heter du? (För- och efternamn)'].strip()
        corners = gambler_row["Hur många hörnor blir det totalt i matchen?"]
        extra_time = gambler_row["Hur många tilläggsminuter blir tillagda under matchen? (Skyltade, även in på eventuell förlängning.)"]
        goal_scorerer_points = gambler_row["Målskyttar"]


        games = []
        for i, label in enumerate(gambler_row.index):
            if 2 <= i <= 9:
                if (i - 2) % 4 == 0:
                    try:
                        teams_string = re.search(self.knockout_game_reg_2, label).group(1)
                    except:
                        raise ValueError(f'Could not find team names in label {label}, {name}')
                    team1, team2 = teams_string.split(" - ")
                    try:
                        winner = gambler_row[label]
                    except:
                        winner = None
                elif (i - 2) % 4 == 1:
                    try:
                        endtime = gambler_row[label]
                    except:
                        endtime = None
                elif (i - 2) % 4 == 2:
                    try:
                        team1_point = int(gambler_row[label])
                    except:
                        team1_point = None
                elif (i - 2) % 4 == 3:
                    try:
                        team2_point = int(gambler_row[label])
                    except:
                        team2_point = None
                    
                    if None in (winner, endtime, team1_point, team2_point):
                        game = Game((team1, team2), (team1_point, team2_point), "Final + Brons", winner, invalid = True)
                        if name != "Facit":
                            print(f'Gambler {name} submitted an invalid answer for the game {teams_string}: {team1_point} - {team2_point}')
                    else:
                        game = Game((team1, team2), (team1_point, team2_point), "Final + Brons", endtime, winner)
                    games.append(game)
            
            
        return games, corners, extra_time, goal_scorerer_points, name

        
    def export_leaderboard(self, path, mode = "excel"):

        all_gamblers = self.gamblers.copy()
        # all_gamblers.append(self.facit_gambler)
        all_gamblers.sort(key = lambda gambler: gambler.total_points, reverse = True)
        pd_dict = {"Spelare":[], 
                    "Gruppspelsmatcher":[],
                    "Gruppspelstabeller":[],
                    "8-delsfinaler":[],
                    "Kvartsfinaler":[],
                    "Semifinaler":[],
                    "Final + Brons":[],
                    "Bonus":[],
                    "Totalt antal poäng":[]}
        for gambler in all_gamblers:
            pd_dict["Spelare"].append(gambler.nick)
            pd_dict["Gruppspelsmatcher"].append(gambler.group_game_points)
            pd_dict["Gruppspelstabeller"].append(gambler.group_table_points)
            pd_dict["8-delsfinaler"].append(gambler.knockout_game_points["8-delsfinaler"])
            pd_dict["Kvartsfinaler"].append(gambler.knockout_game_points["Kvartsfinaler"])
            pd_dict["Semifinaler"].append(gambler.knockout_game_points["Semifinaler"])
            pd_dict["Final + Brons"].append(gambler.final_bronze_game_points)
            pd_dict["Bonus"].append(gambler.bonus_points)
            pd_dict["Totalt antal poäng"].append(gambler.total_points)


        df = pd.DataFrame(pd_dict) #columns = ["Spelare", "Gruppspelsmatcher", "Gruppspelstabeller", "Totalt antal poäng"])
        if mode == "excel":
            path = path + ".xlsx"
            df.to_excel(path, index = False)
        elif mode == "csv":
            path = path + ".csv"
            df.to_csv(path, index = False)
    
    def compute_leaderboard_evolution(self):
        nicks, point_evolutions = [],[]

        # point_evolutions = [[gambler.nick]+gambler.point_evolution for gambler in self.gamblers]


        for gambler in self.gamblers:
            nicks.append(gambler.nick)
            point_evolutions.append(gambler.point_evolution)
        point_evolutions = np.array(point_evolutions)

        rank_over_time = {nick:[] for nick in nicks}

        for i in range(point_evolutions.shape[1]):
            temp_points = point_evolutions[:,i].copy()
            point_nick_pairs = list(zip(temp_points, nicks))
            point_nick_pairs.sort(key = lambda x: x[0], reverse = True)

            for position, (points, nick) in enumerate(point_nick_pairs, start = 1):
                rank_over_time[nick].append(position)
        
        for gambler in rank_over_time:
            fig, ax = plt.subplots()
            ax.set_ylim(34, 0)
            ax.set_title(f'Rankning av spelare {gambler} under trurneringens gång')
            ax.set_xlabel('Bettingrunda')
            ax.set_ylabel('Rank')
            ax.plot(rank_over_time[gambler])
            ax.set_yticks(range(1,35, 5))
            fig.savefig(f'plots/VM2022_rank_over_time/rank_{gambler.replace("/", "_")}.png')

        
if __name__ == '__main__':
    import datetime
    t = Tournament()

    tid = str(datetime.datetime.now().strftime("%m-%d kl %H.%M"))
    # for group_table in t.facit_gambler.bets["Gruppspel - Tabeller"]:
    #     print(group_table.teams_in_order)
    t.export_leaderboard(f"Leaderboard {tid}")
    # t.compute_leaderboard_evolution()

    # print(len(t.gamblers))
    # print(t.gamblers[0].name)

    # for group_game in t.gamblers[0].bets['Gruppspel - Matcher']:
    #     print(group_game.teams, group_game.points)
    
    # print(t.gamblers[0].all_points_list)

