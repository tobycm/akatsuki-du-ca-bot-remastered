"""
Language stuff.
"""

import json
from os import listdir
from typing import Union

from aioredis import Redis

from modules.database_utils import get_user_lang

lang_pack = {}
lang_list = ["vi-vn", "en-us", "ja-jp"]
global redis_ins


def load_lang(redis: Redis) -> dict:
    """
    Return all language pack
    """

    global redis_ins
    redis_ins = redis

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


async def lang(address: str, user_id: int) -> Union[str, list, dict]:
    """
    Return a language string or a list of language strings

    Address format: "child.child"
    """

    lang_option = await get_user_lang(redis_ins, user_id)

    result_lang = lang_pack[lang_option]
    for child in address.split("."):
        result_lang = result_lang[child]

    return result_lang
