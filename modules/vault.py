import json

def get_token(type):
    with open("../config/settings.json", "r") as loaded_json:
        return json.load(loaded_json)["type"]