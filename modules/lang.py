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
redis_ins: Redis


def load_lang(redis: Redis) -> dict:
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


async def lang(address: str, user_id: str) -> Union[str, list[str]]:
    """
    Return a language string or a list of language strings

    Address format: "child.child"
    """

    lang_option = await get_user_lang(redis_ins, user_id)

    lang = lang_pack[lang_option]
    for child in address.split("."):
        lang = lang[child]

    return lang
