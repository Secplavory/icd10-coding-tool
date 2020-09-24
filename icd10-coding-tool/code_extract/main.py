import json
import nltk
from nltk.tokenize.api import TokenizerI
tokenizer = nltk.RegexpTokenizer(r"\w+")
lemmatizer = nltk.stem.WordNetLemmatizer()
stopwords = nltk.corpus.stopwords.words("english")

def findRank(input_str):
    words = [lemmatizer.lemmatize(word) for word in tokenizer.tokenize(input_str.lower()) if word not in stopwords]
    word_dict = {}
    for word in words:
        if word not in word_dict:
            word_dict[word] = {}
            word_dict[word]['f'] = words.count(word)

    max_f = 0
    for v in word_dict.values():
        if max_f < v['f']:
            max_f = v['f']
    for v in word_dict.values():
        v['p'] = v['f'] / max_f

    return word_dict

def findCode(codenet_dict, input_str):
    word_rank = findRank(input_str)
    code_dict = {}
    removed_word = {}
    for code, code_info in codenet_dict.items():
        hasWord = code_info['title'].split(" ", -1)
        hasWord.extend(code_info['synonyms'])
        for word in set(hasWord):
            if code not in code_dict:
                code_dict[code] = {}
                code_dict[code]['f'] = 0
                code_dict[code]['max_p'] = 0
            if word in word_rank:
                if code_dict[code]['max_p'] < word_rank[word]['p']:
                    code_dict[code]['max_p'] = word_rank[word]['p']
                code_dict[code]['f'] +=1
                if code not in removed_word:
                    removed_word[code] = set()
                removed_word[code].add(word)
                
            
    max_f = 0
    for code_v in code_dict.values():
        if max_f < code_v['f']:
            max_f = code_v['f']
    for code, code_info in codenet_dict.items():
        next_total_p = 0
        if 'child' in codenet_dict[code]:
            if code in removed_word:
                tmp_removed = removed_word[code]
            else:
                tmp_removed = set()
            nextCode_dict = findCode(codenet_dict[code]['child'], " ".join(set(word_rank).difference(tmp_removed)))
            code_dict[code]['child'] = nextCode_dict
            for next_code_info in nextCode_dict.values():
                if next_code_info['p'] > 0:
                    next_total_p += next_code_info['p']
            
        if max_f != 0:
            code_dict[code]['w'] = code_dict[code]['f'] / max_f
            code_dict[code]['p'] = code_dict[code]['max_p'] * code_dict[code]['w']
            code_dict[code]['p'] = code_dict[code]['p'] + next_total_p
        else:
            code_dict[code]['w'] = 0
            code_dict[code]['p'] = 0 + next_total_p

    return code_dict


if __name__ == "__main__":
    with open("../data/icd10/icd10_codenet.json", 'r') as f:
        codenet_dict = json.loads(f.read())
    input_str = input("輸入病摘：")
    print()
    candidate = findCode(codenet_dict, input_str)
    
    
    for k,v in sorted(candidate.items(), key=lambda x:x[1]['p'], reverse=True):
        if v['p'] > 0 :
            print(k, v['p'])