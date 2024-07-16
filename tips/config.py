import os

DOWNLOAD_DATA = os.getenv("DOWNLOAD_DATA", "false")
EXCLUDE_PLAYERS = ["Test1", "Test 1", "Test2", "Test 2", "Test3", "Test 3", "Test 17"]
INCLUDE_PHASES = ["group_stage", "last_16", "quarter_finals", "semi_finals", "final", "bonus"]
IS_GITHUB_ACTION = os.getenv("IS_GITHUB_ACTION", "false")

# Dictionary of spelling mistakes from participants
# should be on form
# spelling_dict = { 
#     "wrongg spellink 1": "correct spelling 1",
#     "wtong speeling 2": "correct spelling 2",
# }
spelling_dict = {
    "Test 1": "Test1",
    "Antoine Pomari": "Antoine",
    "Jo då så att": "Erik Hallin",
    "Ali": "Ali Sentissi",
    "ThomasB": "Thomas Berg",
    "Arthur Cherry (Awaken Beerus)": "Arthur Cherry",
    "Arvid Thomasson, Arre": "Arvid Thomasson",
    "Isac Korduner": "Isac korduner",
    "Christian Möller": "Christian möller",
    "Isaac Ekblom": "Isac ekblom",
    "Cristiano Ronaldinho": "Kenji Capannelli",
    "Waldemar Hj Blomster": "Waldemar Blomster",
    "sara": "Sara Whittaker",
    "Tomas Tisberger": "Tomás Tisberger",
    "Anastasis": "Anastasis Dimitriadis",
    "Isac": "Isac ekblom",
    "Yuexin": "Yuexin Zhou",
    "saz sara": "Sara Whittaker",
    "Erik hallin": "Erik Hallin",
    "Isac Ekblom": "Isac ekblom",
    "Thomas Å": "Thomas Berg",
    "Saz": "Sara Whittaker",
}

endtime_dict = {
    "Efter 90 minuter": "90",
    "Efter 120 minuter": "120",
    "Efter straffar": "penalties"
}

endtime_dict_inv = {val: key for key, val in endtime_dict.items()}

TOTAL_GOALS_IN_TOURNAMENT = 117