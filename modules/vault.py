import json

def get_config_value(type):
    with open("config/settings.json", "r") as loaded_json:
        return json.load(loaded_json)[type]