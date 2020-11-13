from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import json
import re

#輸入整篇病摘，輸出dict。key為section name, value為section以下的內容
def getDiagSection(diagnose):
    pattern = re.compile(r'[a-z]+')
    sectionContent_dict = {}
    #whether this should check new section
    section_handler = True
    #Get every line of the diagnose
    diagnose = diagnose.lower()
    sections = diagnose.split("\n", -1)
    #The title of sentence. this will be changed when new title determine
    title = ""
    #traversal all diagnose
    for sentence in sections:
        #to next sentence if sentence is null string
        if sentence == "":
            section_handler = True
        #don't need to check section title. it's still in section
        elif section_handler == False:
            if title not in sectionContent_dict:
                sectionContent_dict[title] = sentence
            else:
                sectionContent_dict[title] +=sentence
        #if sentence not null string and need to check title
        else:
            tmp = sentence.split(":",1)
            #check if the sentence is a title
            if len(tmp) == 1:
                if title not in sectionContent_dict:
                    sectionContent_dict[title] = sentence
                else:
                    sectionContent_dict[title] +=" "+sentence
            else:
                #check if the title is valid
                result = pattern.match(tmp[0])
                #if title is not a new section. append into a section.
                if result == None:
                    if title not in sectionContent_dict:
                        sectionContent_dict[title] = sentence
                    else:
                        sectionContent_dict[title] +=" "+sentence
                else:
                    #the next sentence don't need to check
                    section_handler = False
                    title = tmp[0]
                    content = tmp[1]
                    #to next sentence if content is null string
                    if content == "":
                        pass
                    #check if the title is in dict.
                    elif title not in sectionContent_dict:
                        sectionContent_dict[title] = content
                    else:
                        sectionContent_dict[title] += " " + content
    for k in sectionContent_dict.keys():
        while len(sectionContent_dict[k]) > 0:
            if sectionContent_dict[k][0] == " ":
                sectionContent_dict[k] = sectionContent_dict[k][1:]
            else:
                break
    return sectionContent_dict

"""
#輸入整篇病摘，輸出dict。key為section name, value為section以下的內容
def getDiagSection(diagnose):
    sectionContent_dict = {}
    #Whether the sentance is content or not
    section_handler = False
    #Get every line of the diagnose
    sections = diagnose.split("\n", -1)
    #the title of sentence. this will change when new title determine
    title = ""
    for section in sections:
        #If the sentence is null string
        if section == "":
            #Next sentence may be a new title
            section_handler = False
        #If the sentence is under section title
        elif section_handler == True:
            #append all sentence into the title of sectionContent_dict
            sectionContent_dict[title] += " " + section
        #If the sentence isn't under section title
        else:
            #determine the title of content
            title_tmp = section.split(':', 1)
            #next sentence will directly append into sectionContent_dict
            section_handler = True
            #If the first sentence doesn't have title
            if len(title_tmp)==1:
                title = "no_section_name"
                #append this sentence into sectionContent_dict
                if title not in sectionContent_dict:
                    sectionContent_dict[title] = section
                else:
                    sectionContent_dict[title] +=" " + section
            #If the first sentence have title
            else:
                title = title_tmp[0]
                content = title_tmp[1]
                #append this sentence into sectionContent_dict
                if title not in sectionContent_dict:
                    sectionContent_dict[title] = content
                else:
                    sectionContent_dict[title] +=" " + content
    for k in sectionContent_dict.keys():
        if len(sectionContent_dict[k]) >= 1:
            if sectionContent_dict[k][0] == " ":
                sectionContent_dict[k] = sectionContent_dict[k][1:]
    return sectionContent_dict
"""

#輸入一段文字，輸出一段文字。去除整段話的stopword並轉換為stemword
def getCleanSentence(sentence):
    #get stopWord_list
    stopWord_list = stopwords.words('english')
    
    #regular expression to get pure alphabets
    pattern = r'^[a-z]+$'
    pattern = re.compile(pattern)
    #use to stemming words
    lemmatizer = WordNetLemmatizer()
    #get all word in sentence
    words = sentence.split(" ", -1)
    #contain filted words
    filted_wordList = []
    for word in words:
        #result is pure alphabets
        result = pattern.match(word)
        if result != None:
            #Stemming word
            result = result.group(0)
            result = lemmatizer.lemmatize(result)
            #append if the word is not stopword
            if result not in stopWord_list:
                filted_wordList.append(result)
    return " ".join(filted_wordList)

#輸入一段文字與代碼陣列，輸出配對數量。統計每個句子與icd9正確代碼title(同義字)的比對次數。
def section_statistic(sentence, correct_codeList):
    #regular expression to get pure alphabets
    pattern = r'^[a-z]+$'
    pattern = re.compile(pattern)
    #use to stemming words
    lemmatizer = WordNetLemmatizer()
    #get stopWord list
    with open("./cleaner/data/stopword/stopWord_list.txt", 'r') as f:
        stopWord_list = eval(f.read())
    #get icd9 code titles
    with open("./cleaner/data/icd9_code/icd9_title.json", 'r') as f:
        icd9_title_dict = json.loads(f.read())
    #get all word of title of code
    all_title_word = []
    for code in correct_codeList:
        if code in icd9_title_dict:
            for word in icd9_title_dict[code]:
                result = pattern.match(word.lower())
                if result != None:
                    result = result.group(0)
                    result = lemmatizer.lemmatize(result)
                    if result not in stopWord_list:
                        senses = wn.synsets(result)
                        for sense in senses:
                            synonyms = sense.lemma_names()
                            all_title_word.extend(synonyms)
                            list(set(all_title_word))
                        if result not in all_title_word:
                            all_title_word.append(result)
    #count how many word of sentence matched word of title of code
    count = 0
    sentence_words = sentence.split(" ", -1)
    for word in sentence_words:
        if word in all_title_word:
            count += 1
    return count

#輸入dict，輸出dict。去除黑名單
def blackSection_filter(sections):
    #get statistic_section
    with open("./cleaner/data/section_dict.json", 'r') as f:
        statistic_section = json.loads(f.read())
    #find black list from statistic_section
    black_list = []
    for k,v in statistic_section.items():
        p = v['word_f'] / v['section_f']
        if p < 0.3:
            black_list.append(k)
    #remove sections which in black list
    for black_section in black_list:
        while black_section in sections:
            sections.pop(black_section)
    return sections

#輸入dict，輸出dict。只留白名單
def whiteSection_filter(sections):
    #get statistic_section
    with open("./cleaner/data/section_dict.json", 'r') as f:
        statistic_section = json.loads(f.read())
    #find white list from statistic_section
    white_list = []
    for k,v in statistic_section.items():
        p = v['word_f'] / v['section_f']
        if p > 0.5:
            white_list.append(k)
    #keep sections which in white list
    white_sections = {}
    for white_section in white_list:
        if white_section in sections:
            white_sections[white_section] = sections[white_section]
    return white_sections

#輸入dict，輸出dict。只留discharge .*
def dischargeSection_filter(sections):
    white_list = {}
    pattern = re.compile(r'^discharge diag.*$')
    for k,v in sections.items():
        if pattern.match(k) != None:
            white_list[k] = v
    return white_list

#輸入dict，輸出dict。統計每個section內容的單字統計數量
def diagWord_statistic(sections):
    word_statistic = {}
    for k,v in sections.items():
        if k not in word_statistic:
            word_statistic[k] = {}
        words = v.split(" ", -1)
        for word in words:
            if word not in word_statistic[k]:
                word_statistic[k][word] = 1
            else:
                word_statistic[k][word] +=1
    return word_statistic

#輸入dict，輸出dict。依照單字統計的頻率清除文字
def diagWord_filter(sections):
    with open('./cleaner/data/diagWord_statistic.json', 'r') as f:
        diagWord_dict = json.loads(f.read())
        
    for k,v in sections.items():
        if k in diagWord_dict:
            content = v.split(" ", -1)
            for black_word, frequency in diagWord_dict[k]['words'].items():
                if frequency/diagWord_dict[k]['f'] > 0.5:
                    while black_word in content:
                        content.remove(black_word)
            content = " ".join(content)
            sections[k] = content
    return sections

#輸入dict，輸出dict。去除沒有sense的單字
def sense_filter(sections):
    for k,v in sections.items():
        content = []
        for word in v.split(" ", -1):
            senses = wn.synsets(word, lang="eng")
            if len(senses) != 0:
                content.append(word)
        sections[k] = " ".join(content)
    return sections

#輸入文字，輸出dict。自動化清理整篇病摘(使用上述function)
def cleaner_call(diagnose):
    diag = getDiagSection(diagnose)
    for section_title, section_content in diag.items():
        diag[section_title] = getCleanSentence(section_content)
    diag = diagWord_filter(diag)
    # diag = blackSection_filter(diag)  較不建議使用黑名單模式
    diag = whiteSection_filter(diag)
    diag = sense_filter(diag)
    return diag


#輸入整份病摘，輸出dict或純文字。
#stemming_stopword：是否做stemming與stopword
#section_filter：1使用白名單, 0使用黑名單, 2使用測試名單
#wordFilter：是否清除統計的單字
#senseFilter：是否清除無sense的單字
#pureText：是否將dict轉為純字串輸出
def call_custom_api(diagnose, stemming_stopword=False, section_filter=0 , wordFilter=False, senseFilter=False, pureText=False):
    diagnose_dict = getDiagSection(diagnose)
    if stemming_stopword == True:
        for k,v in diagnose_dict.items():
            diagnose_dict[k] = getCleanSentence(v)
    if section_filter == 1:
        diagnose_filted = whiteSection_filter(diagnose_dict)
    elif section_filter == 0:
        diagnose_filted = blackSection_filter(diagnose_dict)
    else:
        diagnose_filted = dischargeSection_filter(diagnose_dict)
    if wordFilter == True:
        diagnose_filted = diagWord_filter(diagnose_filted)
    if senseFilter == True:
        diagnose_filted = sense_filter(diagnose_filted)
    if pureText == True:
        result = ""
        first_line = True
        for k,v in diagnose_filted.items():
            if first_line:
                first_line = False
            else:
                result += " "
            result += v
        return result
    else:
        return diagnose_filted


