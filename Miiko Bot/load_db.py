# load_db.py
# for db load/refresh purposes

import json
import models

DBS = [('D4DJEvent', 'id'), ('OtherArtist', 'name'), ('D4DJAlbum', 'id'), ('D4DJSong', 'id')]

# load db func to load/reload json data (might need to clear db here as extra preventative measure)
async def load_db():
    for m, pk in DBS:
        mtype = getattr(models, m)
        await mtype.all().delete()
        with open(f'Master/{m}Master.json') as f:
            data = json.load(f)
        for item in data:
            await mtype.update_or_create(**{pk: item, 'defaults':data[item]})