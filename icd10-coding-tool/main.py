import json

def findCode(input_str):
    codenet_path = "./data/icd10/icd10_codenet.json"
    synonymStatistic_path = "./data/statistic/synonym_statistic.json"
    with open(codenet_path, 'r') as f:
        codenet_json = json.loads(f.read())
    with open(synonymStatistic_path, 'r') as f:
        synonymStatistic_json = json.loads(f.read())
    
    input_words = input_str.split(" ", -1)
    word_rank = {}
    for word in input_words:
        if word in synonymStatistic_json:
            word_rank[word] = synonymStatistic_json[word]
    
    return word_rank

input_str = input("輸入病摘：")
print()
candidate = findCode(input_str)
for k,v in candidate.items():
    print(k, v)