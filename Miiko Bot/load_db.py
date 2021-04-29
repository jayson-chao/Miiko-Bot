# load_db.py
# for db load/refresh purposes

import json
import models

DBS = {'OtherArtist': 'name', 'D4DJEvent': 'id', 'D4DJStaff': 'name', 'D4DJAlbum': 'id', 'D4DJSong': 'id'}

M_TO_MS = {
    'D4DJSong': [('D4DJStaff', 'lyricist_rel'), ('D4DJStaff', 'composer_rel'), ('D4DJStaff', 'arranger_rel')]
}

# load db func to load/reload json data (might need to clear db here as extra preventative measure)
async def load_db():
    for m in DBS: # dict order preserved in 3.8
        mtype = getattr(models, m)
        await mtype.all().delete()
        with open(f'Master/{m}Master.json') as f:
            data = json.load(f)

        fields = M_TO_MS[m] if m in M_TO_MS else []

        for item in data:
            model = await mtype.update_or_create(**{DBS[m]: item, 'defaults':data[item]})
            for c, f in fields:
                ctype = getattr(models, c)
                attr = getattr(model[0], f[:-4])
                if f in data[item]:
                    for i in data[item][f]:
                        g = await ctype.get_or_none(**{DBS[c]: i})
                        await attr.add(g)

    # manually load setlists since it doesn't play nice with the current structure i have 
    with open(f'Master/D4DJSetlistMaster.json') as f:
            data = json.load(f)
    for item in data:
        for pos, song in enumerate(data[item]['setlist']):
            await models.D4DJSetlist.update_or_create(event_id=item, song_id=song, position=pos+1)
