import torch
from transformers import BertTokenizer, BertModel

# 检查是否有可用的GPU设备
if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    print("没有找到GPU设备，将在CPU上运行.")
    device = torch.device("cpu")

# 初始化tokenizer和model，并将其放在GPU上（如果可用）
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertModel.from_pretrained('bert-base-chinese').to(device)


def compare_sentence(sentence1, sentence2):
    # 分词
    tokens1 = tokenizer.tokenize(sentence1)
    tokens2 = tokenizer.tokenize(sentence2)
    # 添加特殊标记 [CLS] 和 [SEP]
    tokens1 = ['[CLS]'] + tokens1 + ['[SEP]']
    tokens2 = ['[CLS]'] + tokens2 + ['[SEP]']
    # 将分词转换为对应的词表中的索引
    input_ids1 = tokenizer.convert_tokens_to_ids(tokens1)
    input_ids2 = tokenizer.convert_tokens_to_ids(tokens2)

    # 将输入_ids转换为在device上的张量
    input_ids1 = torch.tensor([input_ids1]).to(device)
    input_ids2 = torch.tensor([input_ids2]).to(device)

    # 获取词向量，在GPU上运行模型
    outputs1 = model(input_ids1.to(device))
    outputs2 = model(input_ids2.to(device))

    # 提取句子
    sentence_embedding1 = outputs1[0][:, 0, :]
    sentence_embedding2 = outputs2[0][:, 0, :]

    # 计算余弦相似度，相似度任务中单个句子两两比较 dim 设置为 1，批次间比较设置为 0
    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6).to(device)
    similarity = cos(sentence_embedding1, sentence_embedding2)

    # 如果需要在CPU上打印结果，可以将相似度转到CPU
    similarity_cpu = similarity.detach().cpu()

    print("句1: ", sentence1)
    print("句2: ", sentence2)
    print("相似度: ", similarity_cpu.item())


compare_sentence("黄河南大街70号8门", "皇姑区黄河南大街70号8门")