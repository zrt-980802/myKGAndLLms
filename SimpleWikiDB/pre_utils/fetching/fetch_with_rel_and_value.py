# -*- coding: utf-8 -*-
"""
@Time ： 2024/11/9 19:37
@Auth ： Andong
@File ：fetch_with_rel_and_value.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
"""
This script fetches all QIDs which have a relationship with a specific value. 

For example: all entities which played 'quarterback' on a football team (corresponding to P413 and a value of Q622747)

to run: 
python3.6 fetch_with_rel_and_value.py --data $DATA --out_dir $OUT
"""

import argparse
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial

from SimpleWikiDB.pre_utils.fetching.utils import jsonl_generator, get_batch_files


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='E:\\data\\output\\entity_rels', help='path to output directory')
    parser.add_argument('--rel', type=str, default='P413', help='relationship')
    parser.add_argument('--entity', type=str, default='Q622747', help='entity value')
    parser.add_argument('--num_procs', type=int, default=10, help='Number of processes')
    return parser


def filtering_func(rel, entity, filename):
    filtered = []
    for item in jsonl_generator(filename):
        if item['property_id'] == rel and item['value'] == entity:
            filtered.append(item)
    return filtered


def main():
    args = get_arg_parser().parse_args()

    table_files = get_batch_files(args.data)
    pool = Pool(processes=args.num_procs)
    filtered = []
    for output in tqdm(
            pool.imap_unordered(
                partial(filtering_func, args.rel, args.entity), table_files, chunksize=1),
            total=len(table_files)
    ):
        filtered.extend(output)

    print(f"Extracted {len(filtered)} rows:")
    for i, item in enumerate(filtered):
        print(f"Row {i}: {item}")


if __name__ == "__main__":
    main()
