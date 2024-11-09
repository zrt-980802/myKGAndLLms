# -*- coding: utf-8 -*-
"""
@Time ： 2024/11/8 13:46
@Auth ： Andong
@File ：preprocess_dump.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import argparse
import multiprocessing
import warnings
from multiprocessing import Queue, Process
from pathlib import Path
import time

from preprocess_utils.reader_process import count_lines, read_data
from preprocess_utils.worker_process import process_data
from preprocess_utils.writer_process import write_data

warnings.simplefilter(action='ignore', category=SyntaxWarning)

def main(paras):
    start = time.time()

    out_dir = Path(paras['out_dir'])
    out_dir.mkdir(exist_ok=True, parents=True)

    input_file = Path(paras['input_file'])
    assert input_file.exists(), f"Input file {input_file} does not exist"

    max_lines_to_read = paras['num_lines_read']

    print("Starting processes")
    maxsize = 10 * paras['processes']

    # Queues for inputs/outputs
    output_queue = Queue(maxsize=maxsize)
    work_queue = Queue(maxsize=maxsize)

    # Processes for reading/processing/writing
    num_lines_read = multiprocessing.Value("i", 0)
    read_process = Process(
        target=read_data,
        args=(input_file, num_lines_read, max_lines_to_read, work_queue)
    )

    read_process.start()

    write_process = Process(
        target=write_data,
        args=(out_dir, paras['batch_size'], output_queue)
    )
    write_process.start()

    work_processes = []
    for _ in range(max(1, paras['processes'] - 2)):
        work_process = Process(
            target=process_data,
            args=(paras['language_id'], work_queue, output_queue)
        )
        work_process.daemon = True
        work_process.start()
        work_processes.append(work_process)

    read_process.join()
    print(f"Done! Read {num_lines_read.value} lines")
    # Cause all worker process to quit
    for work_process in work_processes:
        work_queue.put(None)
    # Now join the work processes
    for work_process in work_processes:
        work_process.join()
    output_queue.put(None)
    write_process.join()

    print(f"Finished processing {num_lines_read.value} in {time.time() - start}s")


if __name__ == "__main__":
    import json
    file_path = 'params.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        args = json.load(file)
    main(args)
