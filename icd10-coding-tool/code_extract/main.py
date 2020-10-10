import json
import nltk
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
        titles = set(code_info['title'].split(" ", -1))
        synonyms = set(code_info['synonyms']).difference(titles)
        if code not in code_dict:
            code_dict[code] = {}
            code_dict[code]['f'] = 0
            code_dict[code]['max_p'] = 0
        if code not in removed_word:
            removed_word[code] = set()

        for word in titles:
            if word in word_rank:
                if code_dict[code]['max_p'] < word_rank[word]['p']:
                    code_dict[code]['max_p'] = word_rank[word]['p']
                code_dict[code]['f'] += 1
                removed_word[code].add(word)

        for word in synonyms:
            if word in word_rank:
                if code_dict[code]['max_p'] < word_rank[word]['p']:
                    code_dict[code]['max_p'] = word_rank[word]['p']
                code_dict[code]['f'] += 1
                removed_word[code].add(word)

    for code, code_info in codenet_dict.items():
        if 'child' in codenet_dict[code]:
            nextCode_dict = findCode(codenet_dict[code]['child'], " ".join([word for word in word_rank.keys() if word not in removed_word[code]]))
            code_dict[code]['child'] = nextCode_dict
            code_dict[code]['all_f'] = code_dict[code]['f'] + calculate_all_f(nextCode_dict)
        else:
            code_dict[code]['all_f'] = code_dict[code]['f']
    return code_dict

def calculate_all_f(candidate):
    count = 0
    for code_info in candidate.values():
        if count < code_info['all_f']:
            count = code_info['all_f']

    return count

def printCandidate(candidate, count=0):
    for k,v in sorted(candidate.items(), key=lambda x:x[1]['all_f'], reverse=True):
        if v['all_f'] > 0 :
            for i in range(0, count):
                print("\t", end="")
            print(k, "：", v['all_f'])
            if "child" in v:
                printCandidate(v['child'], count+1)

def call_extract(input_str):
    with open("../data/icd10/icd10_codenet.json", 'r') as f:
        codenet_dict = json.loads(f.read())
    
    candidate = findCode(codenet_dict, input_str)
    printCandidate(candidate)


if __name__ == "__main__":
    with open("../data/icd10/icd10_codenet.json", 'r') as f:
        codenet_dict = json.loads(f.read())
    input_str = input("輸入病摘：")
    print()
    candidate = findCode(codenet_dict, input_str)
    printCandidate(candidate)
