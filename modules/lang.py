"""
Language stuff.
"""

import json
from os import listdir
from typing import Callable

from modules.database import get_user_lang

lang_packs: dict = {}
lang_list = ["vi-vn", "en-us", "ja-jp"]


def load() -> None:
    """
    Return all language pack
    """

    if lang_packs != {}:
        lang_packs.clear()

    for lang in lang_list:
        options = listdir(f"lang/{lang}/")
        full_lang = {}

        for option in options:
            with open(f"lang/{lang}/{option}", "r", encoding="utf8") as file:
                full_lang.update({option.replace(".json", ""): json.load(file)})

        lang_packs.update({lang: full_lang})


async def get_lang(user_id: int) -> Callable[[str], str]:
    """
    Return a language pack based on user's language
    """

    user_lang_pack = lang_packs[await get_user_lang(user_id)]

    def get_lang_by_address(address: str) -> str:
        """
        Return a language string or a list of language strings

        Address format: "child.child"
        """

        result_lang = user_lang_pack
        for child in address.split("."):
            try:
                child = int(child)  # type: ignore
            except:
                pass
            result_lang = result_lang[child]

        return result_lang

    return get_lang_by_address


Lang = Callable[[str], str]
