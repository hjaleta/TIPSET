import requests
import os
import json


def get_link_dict():
    return {
        "bonus_ANSWERS": "https://docs.google.com/spreadsheets/d/1QnszQtyJOWW0uiRDPNFLXDPsS72fY5tsGR_cLSUpr6g/export?format=csv",
        "group_stage_ANSWERS": "https://docs.google.com/spreadsheets/d/1ZNJvad7mPzcBF-RrYZeQ5XqtOqWco7fNKjbgQJRES2w/export?format=csv",
        "group_stage_RESULTS": "https://docs.google.com/spreadsheets/d/1Vc16Px85krZsPlBvbKRLnj4ucKT-jBsxUopydWeBTjM/export?format=csv",
        "last_16_ANSWERS": "https://docs.google.com/spreadsheets/d/1DfnkRl8koShZ1XwlQz9Amo0C0KvGbMklsX1nrhojSMg/export?format=csv",
        "last_16_RESULTS": "https://docs.google.com/spreadsheets/d/1M4XKFPGWqaZ4wCwBh7xpRZHk61X8mx6eOdzwE0hsdA0/export?format=csv",
    }
    return json.loads(os.getenv("LINK_DICT"))

def download_data():

    os.makedirs('tips/data', exist_ok=True)

    link_dict = get_link_dict()

    for key, value in link_dict.items():
        
        try:
            response = requests.get(value)
            assert response.status_code == 200, 'Wrong status code'
            with open(f'tips/data/{key}.csv', 'w') as f:
                f.write(response.content.decode('utf-8'))
            print(f"Downloaded {key} successfully")
        except Exception as e:
            print(f"Error downloading {key}: {e}")


if __name__ == "__main__":
    download_data()
    # print(get_link_dict())