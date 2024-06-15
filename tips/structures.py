from pydantic import BaseModel, field_validator, model_validator, Field, ConfigDict
from typing import Literal, Optional
import os
import textwrap
from tips.util import rst_toctree, rst_csv_table

# Define the groups
groups = {
    "A" : ("Tyskland", "Skottland", "Ungern", "Schweiz"),
    "B" : ("Spanien", "Kroatien", "Italien", "Albanien"),
    "C" : ("Slovenien", "Danmark", "Serbien", "England"),
    "D" : ("Polen", "Nederländerna", "Österrike", "Frankrike"),
    "E" : ("Belgien", "Slovakien", "Rumänien", "Ukraina"),
    "F" : ("Turkiet", "Georgien", "Portugal", "Tjeckien"),
}
all_teams = [team for teams in groups.values() for team in teams]
Team = Literal["Tyskland", "Skottland", "Ungern", "Schweiz", 
             "Spanien", "Kroatien", "Italien", "Albanien",
             "Slovenien", "Danmark", "Serbien", "England", 
             "Polen", "Nederländerna", "Österrike", "Frankrike", 
             "Belgien", "Slovakien", "Rumänien", "Ukraina",
             "Turkiet", "Georgien", "Portugal", "Tjeckien"]
Group = Literal["A", "B", "C", "D", "E", "F"]
Phase = Literal['group_stage', 'last_16', 'quarter_finals', 'semi_finals', 'final']
Endtime = Literal['90', '120', 'penalties']

class Game(BaseModel):
    teams: tuple[Team, Team]
    score : tuple[int, int]
    event_index : int
    group : Optional[Group] = None
    phase : Phase
    endtime : Endtime = '90'
    winner : Literal[Team, 'draw', None] = None
    points : Optional[int] = None
    facit : bool = False

    @model_validator(mode='after')
    def get_group(self):
        
        if self.phase == 'group_stage':
            found_group = False
            for group, teams in groups.items():
                if self.teams[0] in teams and self.teams[1] in teams:
                    self.group = group
                    found_group = True
                    break
                    
            if not found_group:
                raise ValueError(f"Can't find group for teams {self.teams}")

        else:
            self.group = None
        
        return self
    
    @model_validator(mode='after')
    def get_winner(self):
        
        if self.phase == 'group_stage':
            
            if self.winner is not None:
                raise ValueError("Input for 'winner' must be None for group stage games")

            if self.score[0] > self.score[1]:
                self.winner = self.teams[0]
            elif self.score[0] < self.score[1]:
                self.winner = self.teams[1]
            else:
                self.winner = 'draw'
        
        else:
            if self.winner in (None, 'draw'):
                raise ValueError('Winner must be set for knockout games (cannot be None or draw)')

            if self.winner not in self.teams:
                raise ValueError('Winner must be one of the teams in the game')

            if (self.winner == self.teams[0] and self.score[0] < self.score[1]) or (self.winner == self.teams[1] and self.score[0] > self.score[1]):
                raise ValueError('Winner cannot be the team with the lower score')

        return self

    @model_validator(mode='after')
    def check_endtime(self):
        
        if self.phase == 'group_stage':
            if self.endtime != '90':
                raise ValueError('Group stage games are 90 minutes long')

        else:
            if self.score[0] == self.score[1] and self.endtime != 'penalties':
                raise ValueError('If a game is not in the group stage, endtime must be penalties if the score is a draw')

        return self

    def set_points(self, facit_game: 'Game'):
        points = 0

        if self.winner == facit_game.winner:
            points += 1
        if self.score == facit_game.score:
            points += 1
        
        if self.phase != 'group_stage' and self.endtime == facit_game.endtime:
            points += 1
           
        self.points = points

class GroupTable(BaseModel):
    teams_in_order : tuple[Team, Team, Team, Team]
    group: Optional[Literal['A', 'B', 'C', 'D', 'E', 'F']] = None
    points: Optional[int] = None
    event_index: int

    @model_validator(mode='after')
    def get_group(self):
        
        assert len(self.teams_in_order) == 4, 'There must be 4 teams in the group table'
        assert len(set(self.teams_in_order)) == 4, 'Teams must be unique'

        for group, teams in groups.items():
            if all(team in self.teams_in_order for team in teams):
                self.group = group
                break
        
        if self.group is None:
            raise ValueError(f'Could not find group for teams in group table: {self.teams_in_order}')

        return self

    def set_points(self, facit_table: 'GroupTable'):
        correct_places = sum([int(team == facit_team) for team, facit_team in zip(self.teams_in_order, facit_table.teams_in_order)])
        self.points = min(correct_places, 3)

class Bonus(BaseModel):
    question: str
    answer: Optional[str] = None
    event_index: int
    points : Optional[int] = None
    facit : bool = False
    
        


class Player(BaseModel):

    model_config = ConfigDict(validate_assignment=True)

    name: str
    nick: str
    email: str
    games : dict[Phase, list[Game]] = Field(default = {})
    group_tables : list[GroupTable] = []
    bonus_questions : list[Bonus] = []
    point_list: list = []
    total_points: Optional[int] = None
    is_facit : bool = False

    def compute_points(self, facit_player: 'Player'):

        assert facit_player.is_facit

        point_and_event_index = []

        for phase, games in self.games.items():
            for game, facit_game in zip(games, facit_player.games[phase]):
                game.set_points(facit_game)
                point_and_event_index.append((game.event_index, game.points))
        
        for table, facit_table in zip(self.group_tables, facit_player.group_tables):
            table.set_points(facit_table)
            self.point_list.append((table.event_index, table.points))
            point_and_event_index.append((table.event_index, table.points))
        
        self.total_points = sum([points for _, points in point_and_event_index])

        

    def build_guess_rst(self, directory: str = "webpage/source/content/players", include = None):

        if include is None:
            include = []
        else:
            assert isinstance(include, list) and all([inc in ( 'bonus', 'group_stage', 'last_16', 'quarter_finals', 'semi_finals', 'final') for inc in include])

        player_dir = os.path.join(directory, self.nick)
        os.makedirs(player_dir, exist_ok=True)

        rst_files_to_include = []

        if self.bonus_questions and 'bonus' in include:
            with open(os.path.join(player_dir, 'bonus_table.csv'), 'w') as f:
                f.write("Fråga,Svar\n")
                for bonus in self.bonus_questions:
                    f.write(f'"{bonus.question}","{bonus.answer}"\n')
                
            with open(os.path.join(player_dir, 'bonus.rst'), 'w') as f:
                f.write(textwrap.dedent(
                f"""
                Bonusfrågor
                -----------

                """) + rst_csv_table(
                    "bonus_table.csv",
                    directives = {"widths": "70, 30", "header-rows": 1}
                )
                )
            
            rst_files_to_include.append('bonus')
        
        if self.group_tables and 'group_stage' in include:
            group_table_rst_string = textwrap.dedent("""
            Gruppspel - Tabeller
            --------------------
            """)
            for group_table in self.group_tables:
                file_path = os.path.join(player_dir, f"table_{group_table.group}.csv")
                with open(file_path, 'w') as f:
                    f.write("Placering,Lag\n")
                    for i, team in enumerate(group_table.teams_in_order, start=1):
                        f.write(f"{i},{team}\n")
                
                points = '?' if group_table.points is None else group_table.points
                
                group_table_rst_string += rst_csv_table(
                    file_path=f"table_{group_table.group}.csv",
                    title = f"Grupp {group_table.group}  -  Tjänade poäng: {points}",
                    directives={"widths": "10, 90"}

                )
                
                # textwrap.dedent(f"""
                # .. csv-table:: Grupp {group_table.group}  -  Tjänade poäng: {points}
                #     :file: table_{group_table.group}.csv
                #     :widths: 10,90
                # """)
            
            with open(os.path.join(player_dir, 'group_tables.rst'), 'w') as f:
                f.write(group_table_rst_string)
            
            rst_files_to_include.append('group_tables')
            

        rst_metadata = {
            'group_stage': ('Gruppspel - Matcher', (70, 20, 10)),
            'last_16': ('Åttondelsfinaler', (60, 10, 10, 10, 10)),
            'quarter_finals': ('Kvartsfinaler', (60, 10, 10, 10, 10)),
            'semi_finals': ('Semifinaler', (60, 10, 10, 10, 10)),
            'final': ('Final', (60, 10, 10, 10, 10))
        }

        for phase, games in self.games.items():
            if len(games) == 0 or phase not in include:
                continue
            table_file_path = os.path.join(player_dir, f"{phase}_table.csv")
            phase_rst_file_path = os.path.join(player_dir, f"{phase}.rst")
            rst_files_to_include.append(f"{phase}")

            phase_rst_string = textwrap.dedent(
            f"""
            {rst_metadata[phase][0]}
            {"-"*len(rst_metadata[phase][0])}
            """
            )

            phase_rst_string += rst_csv_table(
                file_path=f"{phase}_table.csv",
                directives={"header-rows":1, "widths": ",".join([str(width) for width in rst_metadata[phase][1]])}
            )

            

            with open(phase_rst_file_path, 'w') as f:
                f.write(phase_rst_string)
            
            if phase == 'group_stage':
                with open(table_file_path, 'w') as f:
                    f.write("Match,Tippat resultat,Tjänade poäng\n")
                    for game in games:
                        points = '?' if game.points is None else game.points
                        f.write(f"{game.teams[0]} - {game.teams[1]},{game.score[0]} - {game.score[1]},{points}\n")

            elif phase in ('last_16', 'quarter_finals', 'semi_finals'):
                with open(file_path, 'w') as f:
                    f.write("Match,Tippat resultat,Tippad sluttid,Vinnare,Tjänade poäng\n")
                    for game in games:
                        points = '?' if game.points is None else game.points
                        endtime = "Straffar" if game.endtime == 'penalties' else f"{game.endtime} min"
                        f.write(f"{game.teams[0]} - {game.teams[1]},{game.score[0]} - {game.score[1]},{endtime},{game.winner},{points}\n")

        player_index_rst_string = textwrap.dedent(
        f"""
        {self.nick}
        {"="*len(self.nick)}
        
        """
        )

        player_index_rst_string += rst_toctree(
            files = rst_files_to_include,
            directives={"maxdepth":1}
        )

        with open(os.path.join(player_dir, 'index.rst'), 'w') as f:
            f.write(player_index_rst_string)

    @property
    def highest_event_index(self):
        max_game_event_index = max([game.event_index for phase, games in self.games.items() for game in games])
        max_table_event_index = max([table.event_index for table in self.group_tables]) if self.group_tables else 0
        bonus_event_index = max([bonus.event_index for bonus in self.bonus_questions]) if self.bonus_questions else 0
        return max(max_game_event_index, max_table_event_index, bonus_event_index)


if __name__ == "__main__":
    g = Game(teams=('Tyskland', 'Skottland'), score=(2, 1), phase='group_stage')
    print(g)
    print(g.group)