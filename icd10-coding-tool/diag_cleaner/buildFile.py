import os
import re
import json
from cleaner import getSections, getCleanSentence, diagWord_filter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

def get_section_words(sections):
	tmp_dict = {}
	for k,v in sections.items():
		if k not in tmp_dict:
			tmp_dict[k] = []
		words = v.split(" ", -1)
		for word in words:
			if word not in tmp_dict[k]:
				if word != "":
					tmp_dict[k].append(word)
	return tmp_dict

def build_diagWord_statistic():
	diagnose_note_path = "../data/diagnose/note/"
	word_statistic_dict = {}
	note_count = 0
	for note in os.listdir(diagnose_note_path)[0:10000]:
		note_path = os.path.join(diagnose_note_path, note)
		with open(note_path, 'r') as f:
			diagnose = f.read().lower()
		diagnose_sections = getSections(diagnose)
		for section_title, section_content in diagnose_sections.items():
			diagnose_sections[section_title] = getCleanSentence(section_content)
		tmp_dict = get_section_words(diagnose_sections)
		for k, words in tmp_dict.items():
			if k not in word_statistic_dict:
				word_statistic_dict[k] = {}
				word_statistic_dict[k]['f'] = 0
				word_statistic_dict[k]['words'] = {}

			word_statistic_dict[k]['f'] += 1
			for word in words:
				if word not in word_statistic_dict[k]['words']:
					word_statistic_dict[k]['words'][word] = 0
				word_statistic_dict[k]['words'][word] += 1

		note_count+=1
		if note_count%100==0:
			print(note)
			remove_key_tmp = []
			for k, v in word_statistic_dict.items():
				if v['f'] < note_count*0.01:
					remove_key_tmp.append(k)
				remove_word_tmp = []
				for word, frequency in v['words'].items():
					if frequency/v['f'] < 0.01:
						remove_word_tmp.append(word)
				for word in remove_word_tmp:
					word_statistic_dict[k]['words'].pop(word)
			for key in remove_key_tmp:
				word_statistic_dict.pop(key)

	with open("../data/statistic/diagWord_statistic.json", 'w') as f:
		f.write(json.dumps(word_statistic_dict))

def count_section_statistic(sentence, correct_codeList):
	pattern = r'^[a-z]+$'
	pattern = re.compile(pattern)
	lemmatizer = WordNetLemmatizer()
	with open("../data/stopword/stopWord_list.txt", 'r') as f:
		stopWord_list = eval(f.read())
	with open('../data/icd9_codeTitle/icd9_title.json', 'r') as f:
		icd9_title_dict = json.loads(f.read())
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
							for synonym in synonyms:
								synonym = synonym.split("_", -1)
								for synonym_w in synonym:
									if synonym_w not in all_title_word:
										all_title_word.extend(synonym_w)
						if result not in all_title_word:
							all_title_word.append(result)

	sentence_words = sentence.split(" ", -1)
	for word in sentence_words:
		if word in all_title_word:
			return 1
	return 0

def build_section_statistic():
	diagnose_note_path = "../data/diagnose/note/"
	diagnose_code_path = "../data/diagnose/code/"
	section_statistic_dict = {}
	note_count = 0
	for note in os.listdir(diagnose_note_path)[0:10000]:
		note_path = os.path.join(diagnose_note_path, note)
		with open(note_path, 'r') as f:
			diagnose = f.read().lower()
		code_path = os.path.join(diagnose_code_path, "code"+note[4:])
		with open(code_path, 'r') as f:
			code_list = f.read().split(',', -1)
		diagnose_sections = getSections(diagnose)
		for section_title, section_content in diagnose_sections.items():
			diagnose_sections[section_title] = getCleanSentence(section_content)
		diagnose_sections = diagWord_filter(diagnose_sections)
		for section_title, section_content in diagnose_sections.items():
			if section_title not in section_statistic_dict:
				section_statistic_dict[section_title] = {}
				section_statistic_dict[section_title]['section_f'] = 0
				section_statistic_dict[section_title]['word_f'] = 0

			section_statistic_dict[section_title]['section_f'] +=1
			count = count_section_statistic(section_content, code_list)
			section_statistic_dict[section_title]['word_f'] += count

		note_count += 1
		if note_count%100 == 0:
			print(note)

	with open("../data/statistic/section_dict.json", 'w') as f:
		f.write(json.dumps(section_statistic_dict))