import json

codenet_path = "./data/icd10/icd10_codenet.json"
synonymStatistic_path = "./data/statistic/synonym_statistic.json"
with open(codenet_path, 'r') as f:
    codenet_json = json.loads(f.read())
with open(synonymStatistic_path, 'r') as f:
    synonymStatistic_json = json.loads(f.read())

def findRank(input_str):
    input_words = input_str.split(" ", -1)
    word_rank = {}
    for word in input_words:
        if word in synonymStatistic_json:
            word_rank[word] = synonymStatistic_json[word]

    return word_rank

def findSense(synonyms):
    synonyms_set = set(synonyms.keys())
    sense_rank = {}
    for code, codeInfo in codenet_json.items():
        for sense, synonym_arr in codeInfo['sense'].items():
            if sense not in sense_rank:
                count = len(synonyms_set.intersection(set(synonym_arr)))
                if count > 0:
                    sense_rank[sense] = {}
                    sense_rank[sense]['f'] = count

    return sense_rank

def findCode(senses):
    senses_set = set(senses.keys())
    code_rank = {}
    for code, codeInfo in codenet_json.items():
        if code not in code_rank:
            count = len(senses_set.intersection(codeInfo['sense']))
            if count > 0:
                code_rank[code] = {}
                code_rank[code]['f'] = count
    
    return code_rank
            


input_str = input("輸入病摘：")
print()
#get rank of all words
candidate = findRank(input_str)
#select senses base on rank
candidate = findSense(candidate)
#select code base on senses
candidate = findCode(candidate)


for k,v in candidate.items():
    print(k, v)