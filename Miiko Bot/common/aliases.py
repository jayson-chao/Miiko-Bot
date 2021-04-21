# aliases.py
# common aliases for arg parsing and more

from enum import IntEnum

artists = ["Happy Around!", "Peaky P-key", "Photon Maiden", "Merm4id", "RONDO", "Lyrical Lily"]

unit_aliases = {
    'happy around!': 0,
    'ha': 0,
    'hapiara': 0,
    'happy around': 0,
    'happyaround': 0,

    'peaky p-key': 1,
    'pk': 1,
    'pkey': 1,
    'peaky': 1,
    'peakypkey': 1,
    'pkpk': 1,
    'p-key': 1,

    'photon maiden': 2,
    'pm': 2,
    'photon': 2,
    'maiden': 2,
    'pmaiden': 2,
    'photome': 2,
    'photonmaiden': 2,

    'merm4id': 3,
    'm4': 3,
    'mermaid': 3,
    'm4id': 3,
    'maid': 3,

    'rondo': 4,
    '燐舞曲': 4,

    'lyrical lily': 5,
    'riri': 5,
    'lili': 5,
    'ri4': 5,
    'li4': 5,
    'riririri': 5,
    'lily': 5,
    'lyricallily': 5
}

pref_aliases = {
    'langpref': 'langpref',
    'language': 'langpref',
    'lang': 'langpref'   
}

class LangPref(IntEnum):
    EN = 1
    JP = 2
    RO = 3

_lang_aliases = {
    'en': LangPref.EN,
    'english': LangPref.EN,

    'jp': LangPref.JP,
    'japanese': LangPref.JP,
    '日本語': LangPref.JP,
    'default': LangPref.JP,

    'ro': LangPref.RO,
    'romanized': LangPref.RO,
    'romanize': LangPref.RO
}

pref_settings = {
    'langpref': _lang_aliases
}

def process_artist(a: str) -> str:
    perf_a = []
    for i in a:
        try:
            perf_a.append(artists[int(i)])
        except: # in place in the event that code with a 9 artist for some reason tries to access this
            pass
    return ', '.join(perf_a)

