"""
Language stuff.
"""

import json
from os import listdir
from typing import Union

from discord import Interaction

from modules.database_utils import get_user_lang

# from modules.checks_and_utils import return_user_lang

lang_pack = {}
lang_list = ["vi-vn", "en-us", "ja-jp"]


def load_lang() -> dict:
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


def get_lang_with_address(address: str, lang_option: str) -> Union[str, list, dict]:
    """
    Return a language string or a list of language strings

    Address format: "child.child"
    """

    result_lang = lang_pack[lang_option]
    for child in address.split("."):
        result_lang = result_lang[child]

    return result_lang


def lang(command_function):
    async def wrapper(interaction: Interaction, *args, **kwargs) -> bool:
        return await command_function(
            interaction,
            *args,
            **kwargs,
            lang=lang_pack[await get_user_lang(interaction.user.id)],
        )

    return wrapper
