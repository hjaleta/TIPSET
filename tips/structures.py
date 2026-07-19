from pydantic import BaseModel, field_validator, model_validator, Field, ConfigDict
from typing import Literal, Optional, Tuple, Dict, List
import os
import textwrap
from tips.util import rst_toctree, rst_csv_table
from tips.config import endtime_dict_inv

# Define the groups
# Change to world cup 2026 groups 
groups = {
    "A": ('Mexiko', 'Sydafrika', 'Sydkorea', 'Tjeckien'),
    "B": ('Kanada', 'Bosnien & Hercegovina', 'Qatar', 'Schweiz'),
    "C": ('Brasilien', 'Marocko', 'Haiti', 'Skottland'),
    "D": ('USA', 'Paraguay', 'Australien', 'Turkiet'),
    "E": ('Tyskland', 'Curaçao', 'Elfenbenskusten', 'Ecuador'),
    "F": ('Nederländerna', 'Japan', 'Sverige', 'Tunisien'),
    "G": ('Belgien', 'Egypten', 'Iran', 'Nya Zeeland'),
    "H": ('Spanien', 'Kap Verde', 'Saudi Arabien', 'Uruguay'),
    "I": ('Frankrike', 'Senegal', 'Irak', 'Norge'),
    "J": ('Argentina', 'Algeriet', 'Österrike', 'Jordanien'),
    "K": ('Portugal', 'Kongo DR', 'Uzbekistan', 'Colombia'),
    "L": ('England', 'Kroatien', 'Ghana', 'Panama'),
}
all_teams = [team for teams in groups.values() for team in teams]
all_team_characters = "".join(set("".join(all_teams)))
all_team_characters = all_team_characters.replace('&', '\&')

Team = Literal[
    "Mexiko", "Sydafrika", "Sydkorea", "Tjeckien",
    "Kanada", "Bosnien & Hercegovina", "Qatar", "Schweiz",
    "Brasilien", "Marocko", "Haiti", "Skottland",
    "USA", "Paraguay", "Australien", "Turkiet",
    "Tyskland", "Curaçao", "Elfenbenskusten", "Ecuador",
    "Nederländerna", "Japan", "Sverige", "Tunisien",
    "Belgien", "Egypten", "Iran", "Nya Zeeland",
    "Spanien", "Kap Verde", "Saudi Arabien", "Uruguay",
    "Frankrike", "Senegal", "Irak", "Norge",
    "Argentina", "Algeriet", "Österrike", "Jordanien",
    "Portugal", "Kongo DR", "Uzbekistan", "Colombia",
    "England", "Kroatien", "Ghana", "Panama"
]
Group = Literal["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
Phase = Literal['group_stage', 'last_32', 'last_16', 'quarter_finals', 'semi_finals', 'final']
Endtime = Literal['90', '120', 'penalties', 'invalid']

class Game(BaseModel):
    teams: Tuple[Team, Team]
    score : Tuple[int, int]
    event_index : int
    group : Optional[Group] = None
    knockout_game: bool
    endtime : Endtime = '90'
    winner : Literal[Team, 'draw', None] = None
    points : Optional[int] = None
    is_facit : bool = False
    is_complete : bool = True

    @model_validator(mode='after')
    def get_group(self):
        
        if not self.knockout_game:
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
        
        if self.score[0] == self.score[1] == -1:
            self.winner = None
            assert not self.is_complete, "If score is (-1, -1), is_complete must be False"

        elif not self.knockout_game:
            
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

            # if (self.winner == self.teams[0] and self.score[0] < self.score[1]) or (self.winner == self.teams[1] and self.score[0] > self.score[1]):
            #     raise ValueError('Winner cannot be the team with the lower score')

        return self

    @model_validator(mode='after')
    def check_endtime(self):
        
        if not self.knockout_game and self.endtime != '90':
            raise ValueError('Group stage games are 90 minutes long')
        
        # else:
        #     if self.score[0] == self.score[1] and self.endtime != 'penalties':
        #         raise ValueError('If a game is not in the group stage, endtime must be penalties if the score is a draw')

        return self

    def set_points(self, facit_game: 'Game'):
        points = 0

        if self.winner == facit_game.winner:
            points += 1
        if self.score == facit_game.score:
            points += 1
        
        if self.knockout_game and self.endtime == facit_game.endtime:
            points += 1
           
        self.points = points



class GroupTable(BaseModel):
    teams_in_order : Tuple[Team, Team, Team, Team]
    group: Optional[Group] = None
    points: Optional[int] = None
    is_facit : bool = False
    is_complete : bool = True
    is_valid : bool = True
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
        if self.is_valid:
            correct_places = sum([int(team == facit_team) for team, facit_team in zip(self.teams_in_order, facit_table.teams_in_order)])
            self.points = min(correct_places, 3)
        else:
            self.points = 0

class TextQuestion(BaseModel):
    question: str
    answer: Optional[str] = None
    event_index: int
    points : Optional[int] | Literal["-"]
    is_facit : bool = False

class SingleChoiceQuestion(BaseModel):
    question: str
    answer: Optional[str] = None
    event_index: int
    points : Optional[int] = None
    is_facit : bool = False
    is_complete : bool = True

    def set_points(self, facit_question: 'SingleChoiceQuestion'):
        if self.answer == facit_question.answer:
            self.points = 1
        else:
            self.points = 0


class MultiChoiceQuestion(BaseModel):
    question: str
    answer: Optional[list[str]] = None
    number_of_choices_allowed: int
    event_index: int
    points : Optional[int] = None
    is_facit : bool = False
    is_complete : bool = True

    def set_points(self, facit_question: 'MultiChoiceQuestion'):
        if self.answer is None or len(self.answer) > self.number_of_choices_allowed:
            self.points = 0
        else:
            correct_choices = set(self.answer).intersection(set(facit_question.answer))
            self.points = len(correct_choices)

class KnockoutQuestion(BaseModel):
    question: str
    answer: int
    event_index: int
    is_facit : bool = False
    is_complete : bool = True

RST_HEADERS = {
    'bonus': 'Bonusfrågor',
    'group_stage': 'Gruppspel',
    'last_32': 'Sextondelsfinaler',
    'last_16': 'Åttondelsfinaler',
    'quarter_finals': 'Kvartsfinaler',
    'semi_finals': 'Semifinaler',
    'final': 'Final'
}

class Player(BaseModel):

    model_config = ConfigDict(validate_assignment=True)

    name: str
    nick: str
    email: str
    questions : Dict[Phase, list] = Field(default = {})
    event_index_and_point_list: List = []
    total_points: Optional[int] = None
    is_facit : bool = False

    def compute_points(self, facit_player: 'Player', include_phases):

        assert facit_player.is_facit

        for phase, questions in self.questions.items():
            
            if phase in include_phases:

                for question, facit_question in zip(questions, facit_player.questions[phase]):
                    
                    if isinstance(question, TextQuestion):
                        self.event_index_and_point_list.append((question.event_index, question.points if isinstance(question.points, int) else 0))
                    elif isinstance(question, KnockoutQuestion):
                        self.event_index_and_point_list.append((question.event_index, 0))
                    else:
                        
                        if facit_question.is_complete:
                            
                            question.set_points(facit_question)
                            self.event_index_and_point_list.append((question.event_index, question.points))

 
        self.total_points = sum([point for _, point in self.event_index_and_point_list])

    def get_question_type_string(self, question):
        if isinstance(question, TextQuestion):
            return 'text'
        elif isinstance(question, SingleChoiceQuestion):
            return 'single_choice'
        elif isinstance(question, MultiChoiceQuestion):
            return 'multi_choice'
        elif isinstance(question, KnockoutQuestion):
            return 'knockout_question'
        elif isinstance(question, Game):
            return 'group_game' if not question.knockout_game else 'knockout_game'
        elif isinstance(question, GroupTable):
            return 'group_table'
        else:
            raise ValueError(f"Unknown question type: {type(question)}")

    def build_guess_rst(self, directory: str = "webpage/source/content/players", include = None):

        if include is None:
            include = []
        else:
            assert isinstance(include, list) and all([inc in ( 'bonus', 'group_stage', 'last_32', 'last_16', 'quarter_finals', 'semi_finals', 'final') for inc in include])

        player_dir = os.path.join(directory, self.nick)
        os.makedirs(player_dir, exist_ok=True)

        rst_files_to_include = []

        CSV_TABLE_GROUPS = {
            ('group_game', ): {'n_cols': 3, 'widths': '70, 20, 10', 'header_row': '"Match","Tippat resultat","Tjänade poäng"'},
            ('knockout_game', ): {'n_cols': 5, 'widths': '60, 10, 10, 10, 10', 'header_row': '"Match","Tippat resultat","Tippad sluttid","Vinnare","Tjänade poäng"'},
            ('group_table', ): {'n_cols': 2, 'widths': '10, 90', 'header_row': '"Placering","Lag"'},
            ('single_choice', 'multi_choice', 'text'): {'n_cols': 3, 'widths': '65, 30, 5', 'header_row': '"Fråga","Svar","Poäng"'},
            ('knockout_question', ): {'n_cols': 2, 'widths': '80, 20', 'header_row': '"Fråga","Svar"'},
            
            # ('knockout_question', ): {'n_cols': 3, 'widths': '70, 20, 10'},
        }

        for phase, questions_phase in self.questions.items():
            if phase not in include:
                continue

            # question_type_string = 
            
            header = RST_HEADERS[phase]
            section_string = textwrap.dedent(
            f"""
            {header}
            {"-"*len(header)}
            """
            )

            questions_split_by_group = []
            previous_question_type_group = tuple([])
            for question in questions_phase:
                question_type_string = self.get_question_type_string(question)
                question_type_group = [group for group in CSV_TABLE_GROUPS.keys() if question_type_string in group][0]
                
                if question_type_group != previous_question_type_group:
                    questions_split_by_group.append([question])
                    previous_question_type_group = question_type_group
                else:
                    questions_split_by_group[-1].append(question)
            
            
            for q_i, questions_group in enumerate(questions_split_by_group):
                questions_type_group = [group for group in CSV_TABLE_GROUPS.keys() if self.get_question_type_string(questions_group[0]) in group][0]
                width_string = CSV_TABLE_GROUPS[questions_type_group]['widths']
                header_row = CSV_TABLE_GROUPS[questions_type_group]['header_row']
                # For group_table questions, we need to create a separate CSV file for each question

                if self.get_question_type_string(questions_group[0]) == 'group_table':
                    section_string += textwrap.dedent("""
                        Gruppspel - Tabeller
                        --------------------
                        """)
                    for group_table in questions_group:

                        group_table_filename = f"group_table_{group_table.group}.csv"
                        points = '?' if group_table.points is None else group_table.points

                        section_string += rst_csv_table(
                                        file_path=group_table_filename,
                                        title = f"Grupp {group_table.group}  -  Tjänade poäng: {points}",
                                        directives={"widths": width_string, 'header-rows': 1}
                                    )
                        
                        table_file_path = os.path.join(player_dir, group_table_filename)
                        with open(table_file_path, 'w') as f:
                            f.write(header_row + "\n")
                            for i, team in enumerate(group_table.teams_in_order, start=1):
                                if group_table.is_valid:
                                    f.write(f'"{i}","{team}"\n')
                                else:
                                    f.write(f'"{i}","-"\n')
            
                else:
                    question_table_filename = f"{phase}_table_{q_i}.csv"
                    table_file_path = os.path.join(player_dir, question_table_filename)
                    
                    section_string += rst_csv_table(
                        file_path=question_table_filename,
                        directives={"widths": width_string, "header-rows": 1}
                    )
                    with open(table_file_path, 'w') as f:
                        f.write(header_row + "\n")
                        for question in questions_group:
                            if isinstance(question, (TextQuestion, SingleChoiceQuestion, MultiChoiceQuestion, Game)):
                                points = '?' if question.points is None else question.points
                                if isinstance(question, (TextQuestion, SingleChoiceQuestion, MultiChoiceQuestion)):
                                    question_str = question.question.replace('"', "'")
                                    if isinstance(question, (TextQuestion, SingleChoiceQuestion)):
                                        answer_str = question.answer.replace('"', "'")
                                    elif isinstance(question, MultiChoiceQuestion):
                                        answer_str = ', '.join(question.answer).replace('"', "'")
                                    
                                    # points = '?' if question.points is None else question.points
                                    f.write(f'"{question_str}","{answer_str}","{points}"\n')
                                elif isinstance(question, Game):
                                    if question.knockout_game:
                                        endtime = "Straffar" if question.endtime == 'penalties' else f"{question.endtime} min"
                                        f.write(f'"{question.teams[0]} - {question.teams[1]}","{question.score[0]} - {question.score[1]}","{endtime}","{question.winner}","{points}"\n')
                                    else:
                                        f.write(f'"{question.teams[0]} - {question.teams[1]}","{question.score[0]} - {question.score[1]}","{points}"\n')
                        
                            
                            elif isinstance(question, KnockoutQuestion):
                                f.write(f'"{question.question.replace('"', "'")}","{question.answer}"\n')
                            else:
                                raise ValueError(f"Unknown question type: {type(question)}")

            with open(os.path.join(player_dir, f"{phase}.rst"), 'w') as f:
                f.write(section_string)
            rst_files_to_include.append(f"{phase}")

           

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
        
        return max([q.event_index for phase, questions in self.questions.items() for q in questions])
        

QUESTION_TYPE_DICT = {
    "text": (TextQuestion, 2),
    "single_choice": (SingleChoiceQuestion, 1),
    "multi_choice": (MultiChoiceQuestion, 1),
    'group_game': (Game, 2),
    'group_table': (GroupTable, 4),
    'knockout_game': (Game, 4),
    "knockout_question": (KnockoutQuestion, 1)
}

if __name__ == "__main__":
    g = Game(teams=('Tyskland', 'Skottland'), score=(2, 1), phase='group_stage')
    print(g)
    print(g.group)