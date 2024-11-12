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
    table_files = get_batch_files(args['input_file_aliases'])
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


def load_files1(filename):
    """ Load JSONL files and aggregate data by alias """
    name2alias = {}
    for item in jsonl_generator(filename):
        alias = item['alias']
        if alias not in name2alias:
            name2alias[alias] = [item['qid']]
        else:
            name2alias[alias].append(item['qid'])
    return name2alias


def load_files2(filename):
    """ Load JSONL files and aggregate data by alias """
    name2label = {}
    for item in jsonl_generator(filename):
        label = item['label']
        if label not in name2label:
            name2label[label] = [item['qid']]
        else:
            name2label[label].append(item['qid'])
    return name2label


def load(args):
    """ Load data from files in parallel """
    # table_files = get_batch_files(args['input_file'])
    table_files_aliases = get_batch_files(args['input_file_aliases'])
    table_files_labels = get_batch_files(args['input_file_labels'])
    with Pool(processes=args['processes']) as pool:
        results1 = list(tqdm(pool.imap_unordered(load_files1, table_files_aliases), total=len(table_files_aliases)))
    with Pool(processes=args['processes']) as pool:
        results2 = list(tqdm(pool.imap_unordered(load_files2, table_files_labels), total=len(table_files_labels)))
    return results1 + results2


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
