# -*- coding: utf-8 -*-
"""
@Time ： 2024/11/13 20:56
@Auth ： Andong
@File ：WebQSPTools.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
import os

from PIL.Image import enum

with open('Params.json', 'r', encoding='utf-8') as f:
    params = json.loads(f.read())

trainSetPath = params['WebQSP_data_path']


def getQAPairList():
    with open(trainSetPath, 'r', encoding='utf-8') as f:
        TrainJSON = json.loads(f.read())
    QuestionList = TrainJSON['Questions']
    QAlist = []
    cnt = 0
    for tmp in QuestionList:
        question = tmp['ProcessedQuestion']
        Parses = tmp['Parses'][0]
        Answers = Parses['Answers']
        QAlist.append((question, Answers))
        # cnt += 1
        # if cnt > 10:
        #     break
    return QAlist


if __name__ == "__main__":
    print(getQAPairList())
