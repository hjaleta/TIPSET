import pandas as pd 


bonus_path = "tips/data/bonus_Q_AND_A.xlsx"

bonus_df = pd.read_excel(bonus_path, sheet_name=None)

print(bonus_df)

df_player = list(bonus_df.values())[0]
df_player.fillna("", inplace=True)

for index, row in df_player.iterrows():
    question = row["Question"]
    answer = row["Answer"]
    points = row["Points"]

    print(question)
    print(answer)
    print(points)
