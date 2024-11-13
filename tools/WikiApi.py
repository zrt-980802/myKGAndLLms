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
from SPARQLWrapper import SPARQLWrapper, JSON

from SimpleWikiDB.wikidataProps.getWikidataProps import searchAllWithName

URL = "https://www.wikidata.org/w/api.php"


# https://www.wikidata.org/w/api.php?errorformat=plaintext&format=json&formatversion=2&origin=*&action=wbsearchentities&type=item&search=Australia&language=en&uselang=en
# https://www.wikidata.org/w/api.php?errorformat=plaintext&format=json&formatversion=2&origin=*&action=wbsearchentities&type=property&search=cap&language=en&uselang=en

def queryEntityIDByName(name):
    PARAMS = {
        "errorformat": "plaintext",
        "action": "wbsearchentities",
        "type": "item",
        "format": "json",
        "origin": "*",
        "formatversion": 2,
        "search": name,
        "language": "en",
        "uselang": "en"
    }

    R = requests.get(url=URL, params=PARAMS)
    DATA = R.json()
    result = []
    # print(DATA)
    for search in DATA['search']:
        result.append(search['id'])
    return result


def queryRelationIDByName(relName):
    PARAMS = {
        "errorformat": "plaintext",
        "action": "wbsearchentities",
        "type": "property",
        "format": "json",
        "origin": "*",
        "formatversion": 2,
        "search": relName,
        "language": "en",
        "uselang": "en"
    }

    R = requests.get(url=URL, params=PARAMS)
    DATA = R.json()
    result = []
    for search in DATA['search']:
        result.append((search['id'], search['display']['label']['value']))
    return result


def queryEntityByID(ID):
    PARAMS = {
        "action": "wbgetentities",
        "format": "json",
        "ids": ID,
        "language": "en"
    }

    R = requests.get(url=URL, params=PARAMS)
    DATA = R.json()
    return DATA


def queryEntityByEntityIDAndRelationID(entityID, relationID):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    query = """
    SELECT ?item ?itemLabel ?linkTo {
      wd:entityID wdt:relationID* ?item .
      OPTIONAL {
        ?item wdt:relationID ?linkTo .
      }
      SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en" .
      }
    }
    """
    query = query.replace('entityID', entityID)
    query = query.replace('relationID', relationID)
    # 设置查询
    sparql.setQuery(query)

    # 设置返回格式为JSON
    sparql.setReturnFormat(JSON)

    # 执行查询并获取结果
    results = sparql.query().convert()
    return results


def getRelationIDByRelName(relName):
    result = []
    for list1 in searchAllWithName(relName):
        for list2 in list1:
            result.append(list2['id'])
    return result


# 给定实体名字和变量,返回若干三元组
def getSubGraphByEntityNameAndRelation(entityName, relationName):
    # 只用匹配度最高的关系
    nameResults = queryEntityIDByName(entityName)
    relResults = queryRelationIDByName(relationName)
    json_graph = queryEntityByEntityIDAndRelationID(nameResults[0], relResults[0][0])
    relationName = relResults[0][1]
    ID2NodeName = {}
    Edges = []
    for tmp in json_graph['results']['bindings']:
        item = tmp['item']
        linkTo = tmp['linkTo']
        itemLabel = tmp['itemLabel']

        From_ID = item['value'].split('/')[-1]
        To_ID = linkTo['value'].split('/')[-1]
        Edges.append([From_ID, relationName, To_ID])
        NodeName = itemLabel['value']
        ID2NodeName[From_ID] = NodeName

    # 去重
    Deduplication_dict = set()
    respond = []
    for edge in Edges:
        # 限定返回数量
        if len(respond) > 10:
            break
        if str(edge) in Deduplication_dict:
            continue
        else:
            Deduplication_dict.add(str(edge))
            edge[0], edge[2] = edge[2], edge[0]
            Deduplication_dict.add(str(edge))
            edge[0], edge[2] = edge[2], edge[0]
        edge[0] = ID2NodeName[edge[0]]
        edge[2] = ID2NodeName[edge[2]]
        respond.append(edge)


    return respond


if __name__ == "__main__":
    print(getSubGraphByEntityNameAndRelation('justin bieber', 'brother'))
