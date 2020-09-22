import json
import codecs
import nltk
from nltk.corpus import wordnet as wn
tokenizer = nltk.RegexpTokenizer(r"\w+")
lemmatization = nltk.stem.WordNetLemmatizer()
stopwords = nltk.corpus.stopwords.words("english")

with codecs.open("../data/icd10/icd10cm_2020.json", 'r', 'utf_8_sig') as f:
    icd10_json = json.loads(f.read())

icd10_codenet = {}
for chapter in icd10_json['icd10cm.tabular']['chapter']:
    for section in chapter["section"]:
        if "diag" in section:
            if type(section['diag']) is list:
                for diag in section['diag']:
                    # print(diag['name'])
                    title_words = [lemmatization.lemmatize(word) for word in tokenizer.tokenize(diag['desc'].lower()) if word not in stopwords]
                    synonyms = []
                    for word in title_words:
                        for sense in wn.synsets(word):
                            for word in sense.lemma_names():
                                if word not in synonyms:
                                    synonyms.append(word)
                    icd10_codenet[diag['name']] = {}
                    icd10_codenet[diag['name']]['title'] = " ".join(title_words)
                    icd10_codenet[diag['name']]['synonyms'] = synonyms
                    
            else:
                # print(section['diag']['name'])
                title_words = [lemmatization.lemmatize(word) for word in tokenizer.tokenize(section['diag']['desc'].lower()) if word not in stopwords]
                senses = [wn.synsets(word) for word in title_words]
                synonyms = []
                for word in title_words:
                    for sense in wn.synsets(word):
                        for word in sense.lemma_names():
                            if word not in synonyms:
                                synonyms.append(word)
                icd10_codenet[section['diag']['name']] = {}
                icd10_codenet[section['diag']['name']]['title'] = " ".join(title_words)
                icd10_codenet[section['diag']['name']]['synonyms'] = synonyms


for k,v in icd10_codenet.items():
    print(k,v)

with open("../data/icd10/icd10_codenet.json", 'w') as f:
    f.write(json.dumps(icd10_codenet))