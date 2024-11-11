# -*- coding: utf-8 -*-
"""
@Time ： 2024/11/6 11:04
@Auth ： Andong
@File ：test_wiki.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
# API 接入点	Wiki
# https://www.mediawiki.org/w/api.php	    MediaWiki API
# https://meta.wikimedia.org/w/api.php	    Meta-Wiki API
# https://en.wikipedia.org/w/api.php	    English Wikipedia API
# https://nl.wikipedia.org/w/api.php	    Dutch Wikipedia API
# https://commons.wikimedia.org/w/api.php	Wikimedia Commons API
# https://test.wikipedia.org/w/api.php	    Test Wiki API



import requests

S = requests.Session()

URL = "https://en.wikipedia.org/w/api.php"
SEARCHPAGE = "Beyonce"

PARAMS = {
    "action": "query",
    "format": "json",
    "list": "search",
    "srsearch": SEARCHPAGE
}

R = S.get(url=URL, params=PARAMS)
DATA = R.json()
print(DATA)
if DATA['query']['search'][0]['title'] == SEARCHPAGE:
    print("Your search page '" + SEARCHPAGE + "' exists on English Wikipedia")
