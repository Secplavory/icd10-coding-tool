import json
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
with open("./data/icd10/icd10_codenet.json", 'r') as f:
    codenet = json.loads(f.read())

#text_sim
def text_sim(word1, word2):
    # sim = model.similarity(word1, word2)
    sim = 1
    return sim

#text_semantic
def text_semantic(diagnose, word):
    sim = 1
    return sim

def layer_00(diagnose):
    diagnose = diagnose.split(" ", -1)
    l0 = {}
    max_f = 0
    for word in diagnose:
        #建構layer 0
        if word not in l0:
            l0[word] = {}
            l0[word]['f'] = 1
            l0[word]['p'] = 1
        else:
            l0[word]['f'] +=1
            #取得單字出現的最多次數
        if max_f < l0[word]['f']:
            max_f = l0[word]['f']
    #計算每個單字的權重
    for v in l0.values():
        v['w'] = v['f'] / max_f
    return l0

def layer_01(layer00):
    l1 = {}
    synonym_list = []
    for code_k, code_v in codenet.items():
        for sense, synonyms in code_v['sense'].items():
            for synonym in synonyms:
                synonym_list.append(synonym)
    max_f = 0
    for l0_k, l0_v in layer00.items():
        if l0_k in synonym_list:
            l1[l0_k] = {}
            l1[l0_k]['f'] = synonym_list.count(l0_k)
            if max_f < l1[l0_k]['f']:
                max_f = l1[l0_k]['f']
    for k, v in l1.items():
        v['w'] = v['f'] / max_f
        v['p'] = 0
        for l0_k, l0_v in layer00.items():
            p = l0_v['p'] * l0_v['w'] * v['w'] * text_sim(l0_k, k)
            if v['p'] < p:
                v['p'] = p

    return l1
    
def layer_02(layer01, diagnose):
    l2 = {}
    max_f = 0
    for code, code_v in codenet.items():
        for sense, synonyms in code_v['sense'].items():
            for synonym in synonyms:
                if synonym in layer01:
                    if sense not in l2:
                        l2[sense] = {}
                        l2[sense]['f'] = 1
                        l2[sense]['max_p'] = layer01[synonym]['p']
                    else:
                        l2[sense]['f'] +=1
                    if max_f < l2[sense]['f']:
                        max_f = l2[sense]['f']
                    if l2[sense]['max_p'] < layer01[synonym]['p']:
                        l2[sense]['max_p'] = layer01[synonym]['p']
    for k,v in l2.items():
        v['w'] = v['f'] / max_f
        v['p'] = v['max_p'] * v['w'] * text_semantic(diagnose, wn.synset(k).definition())
    
    return l2

def layer_03(layer02, diagnose):
    l3 = {}
    max_f = 0
    for code, code_v in codenet.items():
        for sense in code_v['sense'].keys():
            if sense in layer02:
                if code not in l3:
                    l3[code] = {}
                    l3[code]['f'] = 1
                    l3[code]['max_p'] = layer02[sense]['p']
                else:
                    l3[code]['f'] +=1
                if l3[code]['max_p'] < layer02[sense]['p']:
                    l3[code]['max_p'] = layer02[sense]['p']
                if max_f < l3[code]['f']:
                    max_f = l3[code]['f']
    for k,v in l3.items():
        v['w'] = v['f'] / max_f
        v['p'] = v['max_p'] * v['w'] * text_semantic(diagnose, codenet[k]['title'])
    
    return l3

#輸入純文字，輸出dict。
def extracting_code(diagnose):
    l0 = layer_00(diagnose)
    l1 = layer_01(l0)
    l2 = layer_02(l1, diagnose)
    l3 = layer_03(l2, diagnose)
    return l3