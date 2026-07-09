import os

DOWNLOAD_DATA = os.getenv("DOWNLOAD_DATA", "false")
EXCLUDE_PLAYERS = ["Test1",  "Test 1", "Test2", "Test 2", "Test3", "Test 3", "Test 17"
                   ]

INCLUDE_PHASES = ["group_stage", 'bonus', "last_32", "last_16", "quarter_finals", 
                  #"semi_finals", "final", "bonus"
                  ]

GAMES_PER_PHASE = {
    "group_stage": 72,
    "last_32": 16,
    "last_16": 8,
    "quarter_finals": 4,
    # "semi_finals": 2,
    # "final": 1,
}

IS_GITHUB_ACTION = os.getenv("IS_GITHUB_ACTION", "false")


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")

# Dictionary of spelling mistakes from participants
# should be on form
# spelling_dict = { 
#     "wrongg spellink 1": "correct spelling 1",
#     "wtong speeling 2": "correct spelling 2",
# }
spelling_dict = {

    'David Oredsson  (Oreda)': 'David Oredsson',
    'Gustav wickström': 'Gustav Wickström',
    'Inga Tumimnaite': 'Inga Tuminaite',
    'Isac Ekblom  (EM2026)': 'Isac Ekblom',
    'Lucas Fernandez (Lucho)': 'Lucas Fernandez',
    'Lucas fernandez (lucho)': 'Lucas Fernandez',
    'Lucas fernandez': 'Lucas Fernandez',
    'Maxime clauzier': 'Maxime Clauzier',
    'Viggo': 'Viggo Nathorst-Böös',
    'ChefTony': 'Antoine',
    'Maz': 'Madeleine Möller',
    'Wayne Rooney': 'Kenji Capannelli',
    'Anaastasis': 'Anastasis Dimitriadis',
    'Isac ekblom': 'Isac Ekblom',
    'Varm tårta': 'Maelys Lomenech',
    'Sara': 'Sara Whittaker',
    'Martin Pehrsson ( Killer Joe )': 'Martin Pehrsson',
}

endtime_dict = {
    "Efter 90 minuter": "90",
    "Efter 120 minuter": "120",
    "Efter straffar": "penalties"
}

endtime_dict_inv = {val: key for key, val in endtime_dict.items()}

TOTAL_GOALS_IN_TOURNAMENT = None
