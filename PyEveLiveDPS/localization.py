"""
Localization for PELD GUI strings.
"""
from json import loads
import os

__all__ = ["TLocalization", "tr", "current_lang", "search_path_list"]


class TLocalization:
    """
    The main localization class.
    Provide info for tr() to select from.
    """
    def __init__(self, data: dict = {}):
        self.__localization = {}
        self.__localization.update(data)

    def __getitem__(self, item=None):
        return self.__localization.get(item, str(item))

    def LoadFromFile(self, path: str = ""):
        """
        Load a translation file.
        """
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                c = f.readlines()
            # make compatible for .jsonc
            c = [i for i in c if not i.lstrip(" ").startswith("//")]
            self.__localization = loads("\n".join(c))
            return 0
        else:
            return 1


#%%
# load
path = ""
s_ = os.sep
current_lang = TLocalization()

# define where to search for language files.
# the order matters.
search_path_list = [
    "lang.json", "lang.jsonc", f".{s_}lang{s_}lang.json",
    f".{s_}lang{s_}lang.jsonc"
]

# and search them.
for path in search_path_list:
    if os.path.exists(path):
        current_lang.LoadFromFile(path)
        break


def tr(s: str = ""):
    """
    Translate string "s" to "current_lang[s]".
    A simple interface for current_lang.__getitem__().
    """
    global current_lang
    return current_lang[s]
