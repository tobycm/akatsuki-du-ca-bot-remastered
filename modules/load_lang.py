"""
Language loader.
"""

import json
from os import listdir

lang_pack = {}
lang_list = ["vi-vn", "en-us", "ja-jp"]


def get_lang() -> dict:
    """
    Return all language pack
    """

    for lang in lang_list:
        options = [file for file in listdir(f"lang/{lang}/")]
        full_lang = {}

        for option in options:
            with open(f"lang/{lang}/{option}", "r", encoding="utf8") as file:
                loaded_lang = json.load(file)
                temp = {option.replace(".json", ""): loaded_lang}
                full_lang.update(temp)

        lang_pack.update({lang: full_lang})
    return lang_pack
