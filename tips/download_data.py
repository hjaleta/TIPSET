import requests
import os
import json

from tips.config import REPO_ROOT, DATA_DIR


def get_link_dict():
    return {
        "bonus_ANSWERS": "https://docs.google.com/spreadsheets/d/1WjUqj1Aw-dVt3Q0zXu2fBu-SBzih-D0fu3MdRb7-aWY/export?format=csv",
        "bonus_RESULTS": "https://docs.google.com/spreadsheets/d/1OyH9dMZel4cp3aTcnUX3HKrn1cBQJnlEQbSpbv-0T-8/export?format=csv",
        "group_stage_ANSWERS": "https://docs.google.com/spreadsheets/d/1UydotLnGOnBp3_lr7ZwBuErq6zA5ULuC5ayGXf0iwfA/export?format=csv",
        "group_stage_RESULTS": "https://docs.google.com/spreadsheets/d/1cD-n8ZPWb3OxuOOi14MCRsq47WGtTYS2_w46BASwoMA/export?format=csv",
        "last_32_ANSWERS": "https://docs.google.com/spreadsheets/d/1T78t8ImneCVAjGrTceh0XKGWp6Jzhm_nqE0lKM4KEl0/export?format=csv",
        "last_32_RESULTS": "https://docs.google.com/spreadsheets/d/19C2r3UGyXUvXrb7dygP6Rcg6GAnEzfSrLkr6o2vJWZg/export?format=csv",
        "last_16_ANSWERS": "https://docs.google.com/spreadsheets/d/1HgnFAb9RfOk5fAvTnYOtykNOIEHm8yiC2FtN2qi0Xb0/export?format=csv",
        "last_16_RESULTS": "https://docs.google.com/spreadsheets/d/1zQptnJhXePtWUuzmF-g7Y0Kk-Qv8bBKv2ZaLy9Kkhrc/export?format=csv",
        "quarter_finals_ANSWERS": "https://docs.google.com/spreadsheets/d/11gNxWWfgNcOQ8xOJDCVqnXsfl2P_9CBN_VqdUKXjoMU/export?format=csv",
        "quarter_finals_RESULTS": "https://docs.google.com/spreadsheets/d/1t6ij7w_EUj8CHdww4XIzjZz1xiljL_Ni7YSbpirZ-xI/export?format=csv",
        "semi_finals_ANSWERS": "https://docs.google.com/spreadsheets/d/18ycCDt3vb1uHnB960drX1-Z6M7qKICErHaTs2HlniWY/export?format=csv",
        "semi_finals_RESULTS": "https://docs.google.com/spreadsheets/d/1r8ho9b0Zwy0ohBBhpJ0UOsgH5wGD_S0khIx1_fp94f4/export?format=csv", 
        "final_ANSWERS": "https://docs.google.com/spreadsheets/d/1v3MzRYGEl6cQ_6yx1_40-iZNytwsKoK68Ch_ENHYAhs/export?format=csv",
        "final_RESULTS": "https://docs.google.com/spreadsheets/d/14MC3PIDjHLk-gT_k77G8H4ej9uyBUy2fuHIg_xPYLXA/export?format=csv"
    }

def download_data():

    os.makedirs(DATA_DIR, exist_ok=True)

    link_dict = get_link_dict()

    for form_id, link in link_dict.items():
        
        try:
            response = requests.get(link)
            if (status_code := response.status_code) != 200:
                raise ValueError(f'Wrong status code: {status_code}')
            file_ext = link.split("=")[-1]
            if file_ext == "csv":
                with open(f'{DATA_DIR}/{form_id}.{file_ext}', 'w') as f:
                    f.write(response.content.decode('utf-8'))
            elif file_ext == "xlsx":
                with open(f"{DATA_DIR}/{form_id}.{file_ext}", "wb") as f:
                    f.write(response.content)
            print(f"Downloaded {form_id} successfully")
        except Exception as e:
            print(f"Error downloading {form_id}: {e}")


if __name__ == "__main__":
    download_data()
    # print(get_link_dict())
