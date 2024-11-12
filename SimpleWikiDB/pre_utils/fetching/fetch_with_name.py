# -*- coding: utf-8 -*-
"""
@Time ： 2024/11/9 19:37
@Auth ： Andong
@File ：fetch_with_name.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
from datetime import datetime

import SimpleWikiDB.pre_utils.fetching.fetch_with_name

"""
This script fetches all QIDs which are associated with a particular name/alias (i.e. "Victoria")

to run: 
python3.6 fetch_aliases.py --data $DATA --out_dir $OUT --qid Q30
"""

import argparse
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial

from SimpleWikiDB.pre_utils.fetching.utils import jsonl_generator, get_batch_files


def filtering_func(target_name, filename):
    filtered = []
    for item in jsonl_generator(filename):
        if item['alias'] == target_name:
            filtered.append(item)
    return filtered


def main(args):
    table_files = get_batch_files(args['input_file'])
    pool = Pool(processes=args['processes'])
    filtered = []
    for output in tqdm(
            pool.imap_unordered(
                partial(filtering_func, args['name']), table_files, chunksize=1),
            total=len(table_files)
    ):
        filtered.extend(output)

    print(f"Extracted {len(filtered)} rows:")
    for i, item in enumerate(filtered):
        print(f"Row {i}: {item}")



def load_files(filename):
    """ Load JSONL files and aggregate data by alias """
    name2alias = {}
    for item in jsonl_generator(filename):
        alias = item['alias']
        if alias not in name2alias:
            name2alias[alias] = [item['qid']]
        else:
            name2alias[alias].append(item['qid'])
    return name2alias

def load(args):
    """ Load data from files in parallel """
    table_files = get_batch_files(args['input_file'])
    with Pool(processes=args['processes']) as pool:
        results = list(tqdm(pool.imap_unordered(load_files, table_files), total=len(table_files)))
    return results


def search(data, name):
    """ Search for a name in the loaded data """
    result = []
    for list_dict in data:
        if name in list_dict:
            result.append(list_dict[name])
    return result


def timeStamp(content):
    """ Print timestamped messages """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{content}, The current time is: {now}")


if __name__ == "__main__":
    while True:
        timeStamp('Start')
        name = input('Search Name = ')
        file_path = 'params.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            args = json.load(file)
        args['name'] = name
        data = load(args) if not globals().get('data', False) else data
        print(search(data, args['name']))
        timeStamp('End')
