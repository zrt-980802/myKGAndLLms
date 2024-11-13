from tools.WebQSPTools import getQAPairList

QAPairList = getQAPairList()

with open('prompt.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()
# chat_with_prompt
