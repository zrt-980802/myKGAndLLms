import tools.LLmApi as la

with open('prompt.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()
    # print(prompt)
print('------------------------------------')
content = 'When did Beyonce start becoming popular?'
answer = la.chat_with_prompt(content, prompt)
print(answer)

