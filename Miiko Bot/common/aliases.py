# aliases.py
# common aliases for arg parsing and more

from enum import IntEnum

artists = ["Happy Around!", "Peaky P-key", "Photon Maiden", "Merm4id", "RONDO", "Lyrical Lily"]
art_colors = [0xff6e00, 0xc90000, 0x16ffeb, 0xffff00, 0x5755e5, 0xffa8f7, 0x222222, 0x222222, 0x222222, 0x222222]

unit_aliases = {
    'happy_around!': 0,
    'ha': 0,
    'hapiara': 0,
    'happy_around': 0,
    'happyaround': 0,

    'peaky_p-key': 1,
    'pk': 1,
    'pkey': 1,
    'peaky': 1,
    'peakypkey': 1,
    'pkpk': 1,
    'p-key': 1,

    'photon_maiden': 2,
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

    'lyrical_lily': 5,
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

def process_artist(a: str, lang: LangPref) -> str:
    perf_a = []
    for i in a:
        try:
            if int(i) == 4 and lang == LangPref.JP:
                perf_a.append('燐舞曲')
            else:
                perf_a.append(artists[int(i)])
        except: # in place in the event that code with a 9 artist for some reason tries to access this
            pass
    return ', '.join(perf_a)

async def media_name(m, langpref: LangPref): # album & song have same name fields in model
    try:
        if langpref == LangPref.JP and m.jpname:
            return m.jpname
        elif langpref == LangPref.RO and m.roname:
            return m.roname
    except: # has try-except to catch passed object not having jp/ro name field (i.e. OtherArtist)
        pass    
    return m.name

