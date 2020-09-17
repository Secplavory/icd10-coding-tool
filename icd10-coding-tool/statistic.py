import json

def build_synonymStatistic():
    codenet_path = "./data/icd10/icd10_codenet.json"
    with open(codenet_path, 'r') as f:
        codenet_json = json.loads(f.read())

    synonym_statistic = {}
    for code, codeInfo in codenet_json.items():
        synonym_set = set()
        for sense, synonyms in codeInfo['sense'].items():
            for synonym in synonyms:
                synonym_set.add(synonym)
        for synonym in synonym_set:
            if synonym not in synonym_statistic:
                synonym_statistic[synonym] = {}
                synonym_statistic[synonym]['f'] = 0
            synonym_statistic[synonym]['f'] += 1

    with open("./data/statistic/synonym_statistic.json", 'w') as f:
        f.write(json.dumps(synonym_statistic))

# build_synonymStatistic()