import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(__file__))

from tips.config import EXCLUDE_PLAYERS

bonus_question_form_df = pd.read_csv(
    "tips/data/bonus_ANSWERS.csv"
)


with pd.ExcelWriter('tips/data/bonus_correction_form.xlsx') as writer:  # doctest: +SKIP
    
    for index, row in bonus_question_form_df.iterrows():

        player_name = row["Vad heter du? (För- och efternamn)"].strip()

        if player_name in EXCLUDE_PLAYERS:
            continue

        df_dict = {"Question":[], "Answer":[], "Points": []}

        for i in range(2, len(row)):
            df_dict["Question"].append(row.index[i])
            df_dict["Answer"].append(str(row.iloc[i]))
            df_dict["Points"].append("")
        
        df_dict["Points"][-1] = "-"
        df_dict["Points"][-2] = "-"
        
        player_bonus_df = pd.DataFrame.from_dict(df_dict)

        player_bonus_df.to_excel(writer, sheet_name=player_name)
