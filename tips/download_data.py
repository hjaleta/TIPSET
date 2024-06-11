import requests
import os
import json


def get_link_dict():
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
        
        except Exception as e:
            print(f"Error downloading {key}: {e}")


if __name__ == "__main__":
    download_data()
    # print(get_link_dict())