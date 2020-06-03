import json

from youtube_search import YoutubeSearch


def get(req):
    songs = get_links(req)
    if songs != 0:
        return songs[0]
    else:
        return 0

class Song:
    def __init__(self, link, name):
        self.name = name
        self.link = 'https://www.youtube.com/' + link


def get_links(req):
    res = []
    result = json.loads(YoutubeSearch(req,max_results=3).to_json())
    for video in result["videos"]:
        res.append((Song(video["link"], video["title"])))
        return res
    return 0