import json
from os import listdir

lang_pack = {}
lang_list = ["vi-vn", "en-us", "ja-jp"]

def get_lang() -> dict:
    for lang in lang_list:
        options = [f for f in listdir(f"lang/{lang}/")]
        full_lang = {}
        
        for option in options:
            with open(f"lang/{lang}/{option}", "r") as f:
                loaded_lang = json.load(f)
                temp = {option.replace(".json", ""): loaded_lang}
                full_lang.update(temp)
                
        lang_pack.update({lang: full_lang})
    return lang_pack
