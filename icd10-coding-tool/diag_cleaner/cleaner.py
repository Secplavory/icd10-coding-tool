import re
from nltk.stem import WordNetLemmatizer
import json

def getSections(diagnose):
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

def getCleanSentence(sentence):
	with open('../data/stopword/stopword_list.txt', 'r') as f:
		stopWord_list = eval(f.read())
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

def diagWord_filter(sections):
	with open('../data/statistic/diagWord_statistic.json', 'r') as f:
		diagWord_dict = json.loads(f.read())
	for k,v in sections.items():
		if k in diagWord_dict:
			content = v.split(" ", -1)
			for black_word, frequency in diagWord_dict[k]['words'].items():
				if frequency/diagWord_dict[k]['f'] > 0.8:
					while black_word in content:
						content.remove(black_word)
			content = " ".join(content)
			sections[k] = content
	return sections

def section_filter(sections):
	with open('../data/statistic/section_dict.json', 'r') as f:
		section_dict = json.loads(f.read())
	white_list = []
	for k,v in section_dict.items():
		p = v['word_f'] / v['section_f']
		if p > 0.5:
			white_list.append(k)
	white_sections = {}
	for white_key in white_list:
		if white_key in sections:
			white_sections[white_key] = sections[white_key]
	return white_sections

def cleaner_api(diagnose):
	diag_dict = getSections(diagnose)
	cleaned_dict = {}
	for title, sent in diag_dict.items():
		cleaned_dict[title] = getCleanSentence(sent)
	diag_dict = cleaned_dict
	diag_dict = section_filter(diag_dict)
	diag_dict = diagWord_filter(diag_dict)
	return diag_dict