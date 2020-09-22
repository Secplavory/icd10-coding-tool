import json
import nltk
from nltk.tokenize.api import TokenizerI
tokenizer = nltk.RegexpTokenizer(r"\w+")
lemmatizer = nltk.stem.WordNetLemmatizer()
stopwords = nltk.corpus.stopwords.words("english")

with open("../data/icd10/icd10_codenet.json", 'r') as f:
    codenet_dict = json.loads(f.read())
synonyms = set()
for codeInfo in codenet_dict.values():
    for word in codeInfo['title'].split(" ", -1):
        synonyms.add(word)
    for word in codeInfo['synonyms']:
        synonyms.add(word)

def findRank(input_str):
    words = [lemmatizer.lemmatize(word) for word in tokenizer.tokenize(input_str.lower()) if word not in stopwords]
    word_dict = {}
    for word in words:
        if word in synonyms and word not in word_dict:
            word_dict[word] = {}
            word_dict[word]['f'] = words.count(word)

    max_f = 0
    for v in word_dict.values():
        if max_f < v['f']:
            max_f = v['f']
    for v in word_dict.values():
        v['p'] = v['f'] / max_f

    return word_dict

def findCode(synonym_dict):
    code_dict = {}
    for word, word_v in synonym_dict.items():
        for code, code_v in codenet_dict.items():
            if word in code_v['title'].split(" ", -1) or word in code_v['synonyms']:
                if code not in code_dict:
                    code_dict[code] = {}
                    code_dict[code]['f'] = 0
                    code_dict[code]['max_p'] = 0
                if code_dict[code]['max_p'] < word_v['p']:
                    code_dict[code]['max_p'] = word_v['p']
                code_dict[code]['f'] += 1
    
    max_f = 0
    for code_v in code_dict.values():
        if max_f < code_v['f']:
            max_f = code_v['f']
    for code_v in code_dict.values():
        code_v['w'] = code_v['f'] / max_f
        code_v['p'] = code_v['max_p'] * code_v['w']

    return code_dict

    


if __name__ == "__main__":
    input_str = input("輸入病摘：")
    print()
    synonym_dict = findRank(input_str)
    candidate = findCode(synonym_dict)
    
    for k,v in sorted(candidate.items(), key=lambda x:x[1]['p'], reverse=True):
        print(k, v)