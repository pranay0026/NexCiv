import urllib.request
import urllib.parse
import json
import os
import shutil

headers = {'User-Agent': 'NexCivAcademicResearch/1.0 (contact@nexciv.org)'}

def search_commons(query, limit=5):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers=headers)
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            for pid, pinfo in data.get('query', {}).get('pages', {}).items():
                title = pinfo.get('title')
                iinfo = pinfo.get('imageinfo', [{}])[0]
                mime = iinfo.get('mime', '')
                url_val = iinfo.get('url')
                if mime.startswith('image/jpeg') or mime.startswith('image/png'):
                    results.append((title, url_val))
    except Exception as e:
        print(f"Error searching '{query}':", e)
    return results

queries = {
    'road': ['Potholes on road in India', 'Roads deformed Bengaluru', 'Potholed road India', 'Potholes on road.jpg'],
    'drainage': ['Open Sewer Bangalore India', 'open sewer drain India', 'Sewer drains. Ajmer. india.jpg', 'open storm drain India'],
    'water': ['burst water main street', 'leaking water pipe street', 'water pipeline leak street', 'broken water pipe street'],
    'lights': ['Varanasi wired electric pole', 'electric pole wires India', 'street light pole street India'],
    'sanitation': ['Garbage Disposal Hyderabad 2005', 'Garbage heap New Delhi', 'garbage dump India street', 'waste pile street India']
}

for cat, qlist in queries.items():
    print(f"\n=================== CATEGORY: {cat} ===================")
    found = False
    for q in qlist:
        res = search_commons(q, limit=4)
        if res:
            for t, u in res:
                print(f"[{cat}] {t} -> {u}")
            found = True
            break
