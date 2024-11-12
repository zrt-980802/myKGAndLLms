# -*- coding: utf-8 -*-
"""
@Time ： 2024/11/10 21:16
@Auth ： Andong
@File ：get-wikidataProps.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import warnings
from math import ceil

from tqdm import tqdm

from operator import itemgetter
import requests, json, pdb, jinja2, os

TYPES = {
    "Q15720608": "Wikidata qualifier",
    "Q18608359": "to indicate a source",
    "Q18608871": "for items about people",
    "Q18608993": "for items about organizations",
    "Q18609040": "for a taxon",
    "Q18610173": "for Commons",
    "Q18615010": "for use as qualifier",
    "Q18615777": "to indicate a location",
    "Q18616084": "for language",
    "Q18618644": "for items about works",
    "Q18644427": "obsolete Wikidata property",
    "Q18647515": "transitive property",
    "Q18647518": "symmetric property",
    "Q18647519": "asymmetric property",
    "Q18667213": "about Wikimedia categories",
    "Q18668171": "orderable Wikidata property",
    "Q18720640": "Wikidata sandbox property",
    "Q19643892": "Wikidata name property",
    "Q19820110": "for property documentation",
    "Q19829914": "for places",
    "Q19847637": "representing a unique identifier",
    "Q19887775": "related to medicine",
    "Q20085670": "for romanization system",
    "Q20824104": "for items about languages",
    "Q21077852": "for physical quantities",
    "Q21099935": "with datatype string that is not an external identifier",
    "Q21126229": "for software",
    "Q21264328": "multi-source external identifier",
    "Q21294996": "related to chemistry",
    "Q21451142": "for astronomical objects",
    "Q21451178": "related to economics",
    "Q21504947": "to indicate a constraint",
    "Q21818626": "related to sport",
    "Q22582645": "metaproperty"
}


class DictQuery(dict):
    def get(self, path, default=None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break;

        return val


ENDPOINT = "https://www.wikidata.org/w/api.php"
PROP_NAMESPACE = 120
QUERY_LIMIT = 50
PATH = os.path.dirname(os.path.realpath(__file__))
SAVE_DIRECTORY = PATH + "\\"
FILE_NAME = "props.json"
ABS_PATH = SAVE_DIRECTORY + FILE_NAME


def parseprop(item):
    prop = DictQuery(item)

    data = {
        "datatype": prop.get("datatype"),
        "id": prop["id"],
        "label": prop.get("labels/en/value"),
        "description": prop.get("descriptions/en/value"),
        "aliases": [a["value"] for a in prop.get("aliases/en")]
    }

    example = prop.get("claims/P1855/mainsnak/datavalue/value/numeric-id")

    if isinstance(example, list) and example[0] != None:
        data["example"] = example

    types = prop.get("claims/P31/mainsnak/datavalue/value/numeric-id")

    if isinstance(types, list):
        data["types"] = [_f for _f in [TYPES.get("Q%s" % qid) for qid in types] if _f]

    return data


def get_prop_info(ids):
    # print("get_prop_info %s" % ",".join(ids))

    params = {
        "action": "wbgetentities",
        "ids": "|".join(ids),
        "languages": "en",
        "format": "json",
        "props": "info|aliases|labels|descriptions|claims|datatype",
        "languagefallback": 1
    }

    r = requests.get(ENDPOINT, params=params)
    return list(r.json()["entities"].values())


def get_prop_ids(cont=None):
    # print("get_prop_ids %s" % cont)

    params = {
        "action": "query",
        "list": "allpages",
        "apnamespace": PROP_NAMESPACE,
        "aplimit": 500,
        "format": "json"
    }

    if cont:
        params["apcontinue"] = cont

    r = requests.get(ENDPOINT, params=params)
    return r.json()


def get_all_prop_ids():
    allprops = []

    cont = None

    while True:
        data = get_prop_ids(cont)

        for page in data["query"]["allpages"]:
            allprops.append(page["title"].replace("Property:", ""))

        if "continue" in data:
            cont = data["continue"]["apcontinue"]
        else:
            break

    return allprops


def main():
    if not os.path.exists(SAVE_DIRECTORY):
        print(f'save path is not exist!!\n{SAVE_DIRECTORY}')
        return
    props = []

    print("Getting all property ids")
    propids = get_all_prop_ids()

    maxrange = ceil(len(propids) / float(QUERY_LIMIT))

    # tdqm pls
    for index in tqdm(range(0, int(maxrange))):
        realindex = index * QUERY_LIMIT
        ids = propids[realindex:realindex + QUERY_LIMIT]

        for p in get_prop_info(ids):
            props.append(parseprop(p))

    # Sort by label
    props = sorted(props, key=itemgetter("label"))
    jsonpath = ABS_PATH
    print(("Saving to " + jsonpath))

    with open(jsonpath, "w") as jsonprops:
        jsonprops.write(json.dumps(props))


def main_from_json():
    with open(ABS_PATH) as f:
        props = json.loads(f.read())
        rel = {"props": props}
        print(rel)


import ahocorasick


class AutomatonTree:
    def __init__(self, props):
        self.fileCacheAliasesDict = {}
        self.ACTree = ahocorasick.Automaton()
        self.buildFileCache(props)

    def buildFileCache(self, props):

        # props = json.loads(f.read())
        print(f'\"buildFileCache\" function beging. There are {len(props)} rel labels.')
        for data in props:
            def add_tmp(container, key_tmp, data_tmp):
                if container.get(key_tmp) is None:
                    container[key_tmp] = [data_tmp]
                else:
                    container[key_tmp].append(data_tmp)

            for aliases in data['aliases']:
                add_tmp(self.fileCacheAliasesDict, aliases, data)
            label = data['label']
            add_tmp(self.fileCacheAliasesDict, label, data)

        for key in self.fileCacheAliasesDict.keys():
            self.ACTree.add_word(key, self.fileCacheAliasesDict[key])
        self.ACTree.make_automaton()

    def search(self, target: str):
        iters = self.ACTree.iter(target)
        result = []
        for it in iters:
            print(it)
            result.append(it[1])
        return result


if os.path.exists(ABS_PATH) is False:
    print(f"The {FILE_NAME} is not existed!, build now....")
    main()

with open(ABS_PATH) as f:
    props = json.loads(f.read())

acTree = AutomatonTree(props)


def searchAllWithName(name):
    if len(name) < 3:
        warnings.warn('Too short for Relation-name!!! At least three characters')
        return None
    result = acTree.search(name)
    print(acTree.search(name))
    return result


if __name__ == "__main__":
    searchAllWithName('son')
