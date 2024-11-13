# -*- coding: utf-8 -*-
"""
@Time ： 2024/10/30 21:28
@Auth ： Andong
@File ：LLmApi.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import os

import httpx
from openai import OpenAI

# read apikey from .key file
with open('.key') as f:
    MOONSHOT_API_KEY = f.readline()

temperature = 0.3
max_tokens = 2048
model = "moonshot-v1-auto"
client = OpenAI(
    api_key=MOONSHOT_API_KEY,
    # api_key=MOONSHOT_API_KEY,
    base_url="https://api.moonshot.cn/v1",
)

history = [
    {"role": "system",
     "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"}
]


def chat_with_history(query, history):
    history.append({
        "role": "user",
        "content": query
    })
    completion = client.chat.completions.create(
        model=model,
        messages=history,
        temperature=temperature,
    )
    result = completion.choices[0].message.content
    history.append({
        "role": "assistant",
        "content": result
    })
    return result


def chat_with_prompt(content, prompt):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ],
        temperature=temperature,
    )
    return completion.choices[0].message.content


def chat(content):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": content}
        ],
        temperature=temperature,
    )
    return completion.choices[0].message.content


def streaming_chat(content):
    stream = completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": content}
        ],
        temperature=temperature,
        stream=True
    )
    return stream


def streaming_print(stream):
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="")


if __name__ == "__main__":
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()
    question = '什么民族最能吃辣'
    print(chat_with_prompt(question, prompt))
