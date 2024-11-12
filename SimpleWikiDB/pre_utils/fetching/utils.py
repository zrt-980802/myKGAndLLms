# -*- coding: utf-8 -*-
"""
@Time ： 2024/11/9 19:37
@Auth ： Andong
@File ：utils.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

import os
import ujson as json


def jsonl_generator(fname):
    """ Returns generator for jsonl file """
    with open(fname, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                # 直接加载JSON，避免处理末尾逗号的情况
                yield json.loads(line)


def get_batch_files(fdir):
    """ Returns paths to files in fdir """
    filenames = [os.path.join(fdir, f) for f in os.listdir(fdir)]
    print(f"Fetched {len(filenames)} files from {fdir}")
    return filenames
