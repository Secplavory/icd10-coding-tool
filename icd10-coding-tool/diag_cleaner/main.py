from buildFile import build_diagWord_statistic, build_section_statistic
import json

# build_diagWord_statistic()
# build_section_statistic()

with open("../data/statistic/section_dict.json", 'r') as f:
    section_dict = json.loads(f.read())

for k,v in sorted(section_dict.items(), key=lambda x:x[1]['section_f'], reverse=True):
    if v['section_f'] > 1000 and v['word_f'] / v['section_f'] > 0.3:
        print(k, v)