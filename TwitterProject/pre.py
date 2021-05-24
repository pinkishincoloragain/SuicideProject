import re
import csv
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
import nltk
from collections import Counter
import os

power_words_set = []
with open("power_words.csv", "r", encoding="utf-8-sig", errors='ignore') as infile:
    power_csv = csv.reader(infile)
    for words in power_csv:
        power_words_set.extend(words)

counter_not_suicide = Counter()
counter_suicide = Counter()
# 형식 변환
pattern_text = re.compile(pattern="text")
# 숫자 제거
pattern_num = re.compile(r'[1-9]\d*')
# retweet 제거
pattern_rt = re.compile(r'@RT[\S\s]+')
# 특수문자 제거
pattern_special = re.compile(r'[-=+,#/:^$.*\"※~&%ㆍ!』\\‘|\[\]`…》]')
# email 제거
pattern_email = re.compile(r"\S*@\S*\s?")
# link 제거
pattern_link = re.compile(r'http\S+')
# 문자 0개이상, 좌우 공백 시 문자3개이상
pattern_so_short = re.compile(r'\W*\b\w{1,2}\b')

path = '/data/'
file_list = os.listdir(path)
for i in range(len(file_list)):
    filename = file_list[i]
    print(filename)

def test_line():
    return ["I can't think of any reason to stay. I have no sense of stability in any area of life and I'm fucking "
            "terrified. Narcissistic parents that didn't want me. No friends. I've experienced how wonderful life can "
            "be, just for marvelling at existence itself and appreciating its divinity - appreciating my senses etc. "
            "It's not enough though. My basic human needs aren't being met and I've tried everything. I can't seem to "
            "play the character that I need to in order to move through the world. I'm tired. Nothing's getting "
            "better, it's getting worse and I'm not a teenager anymore - I'm a woman in my late twenties. I want out. "
            "I'm done being alone and being in these terrifying situations. I'm ready to die.",

            "Hi, it's my first post here, I'm new in this community. So... I've been struggling with suicidal "
            "thoughts for at "
            "least 8 years now. Today is my 25th birthday. Things have been extremely bad lately. I lost my job that "
            "I adored and "
            "I feel useless because of unemployment, I live in a country where unemployment rates are extremely high "
            "and my field "
            "of work doesn't have many opportunities. Even outside of it, it's hard to find work. I feel hopeless and "
            "it has made "
            "my suicidal thoughts much worse. "
            ,
            "I actually plan to do it tonight. I had a shitty birthday and I really don't need to live a day more. "
            "Leading up to "
            "today, I've broken up with my girlfriend and pushed my family members away from me as much as possible, "
            "so it will "
            "lessen their pain. It hurts a lot, but it's for their own good. "
            ]

def analyze(in_line,cnt):
    # 0: power word 없음, 1~: power word 있음
    case = 0
    # lanc = LancasterStemmer()

    # 외국어, 단수명사, 고유명사, 복수명사, 동사, 동명사, 과거형, 과거분사, 3인칭아님(현재), 3인칭동사(현재), 형용사, 비교급, 최상급
    pos_list = ['FW', 'NN', 'NNP', 'NNS', 'VB', 'VBG', 'VBD', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS']

    # 소문자 변환, 좌우개행제거
    in_line = str(in_line).lower().strip()
    rem_short = re.sub(pattern=pattern_so_short,repl='',string=in_line)
    rem_text = re.sub(pattern=pattern_text,repl='',string=rem_short)
    rem_num = re.sub(pattern=pattern_num,repl='',string=rem_text)
    rem_rt = re.sub(pattern=pattern_rt,repl='',string=rem_num)
    rem_email = re.sub(pattern=pattern_email,repl='',string=rem_rt)
    rem_url = re.sub(pattern=pattern_link,repl='',string=rem_email)
    in_text = re.sub(pattern=pattern_special, repl="", string=rem_url)

    original = "".join(in_text)

    # 무조건 반환
    appeared = []
    for i in range(len(power_words_set)):
        if str(power_words_set[i]) in in_text:
            appeared.append(power_words_set[i])

    with open("data/result/"+filename +' suicide_detected.txt', mode='a+', encoding='utf-8') as outfile_1:
        with open("data/result/"+filename +' suicide_not_detected.txt', mode='a+', encoding='utf-8') as outfile_2:
            writing_counter = 0
            print(f"making files for {filename} ..")
            tokenizer = nltk.tokenize.RegexpTokenizer('[\w]+')
            tokens = tokenizer.tokenize(in_text)
            tagged = nltk.pos_tag(tokens)

            res = list(word for word, pos in tagged if pos in pos_list)
            stop_words = set(stopwords.words('english'))
            for word in tokens:
                if word not in stop_words:
                    res.append(word)

            # stemmed = [lanc.stem(w) for w in res]

            if len(appeared) > 0:
                case = len(appeared)
                outfile_1.write(f"{cnt} case: {case}\nPower words: {appeared}\noriginal: {original}\n")
                # outfile_2.write(f"{cnt} case: {case}\noriginal: {original}\nresult: {result}\n")

                # counter.update(iter(appeared))
                counter_suicide.update(in_text.split())

            # ------------------------------------------power word 없음. 분석------------------------------------------

            if case == 0:
                counter_not_suicide.update(iter(res))
                original_str = "".join(original)
                outfile_2.write(f"{cnt} case: {case}\nresult: {res}\noriginal: {original_str}\n")

    return counter_suicide,counter_not_suicide

if __name__ =='__main__':
    temp = test_line()
    cnt = 0

    # with open("test.csv", "r", encoding="utf-8-sig", errors='ignore') as infile:
    #     tester = csv.reader(infile)
    #     for line in tester:
    #         analyze(line,cnt)
    #         cnt+=1

    with open("data/"+filename,"r",encoding="utf-8") as infile:
        while True:
            line = infile.readline()
            if not line:
                break
            if "text" in line:
                analyze(line,cnt)
                cnt+=1

    print(f"Total number of datas detected: {cnt}\n")
    print("Most common 30 words in suicide detected data")
    for key, value in counter_suicide.most_common(30):
        print(f"{key}: {value}")

    print("Most common 30 words not in suicide detected data")
    for key, value in counter_not_suicide.most_common(30):
        print(f"{key}: {value}")

    total_counter = Counter()

    total_counter = counter_suicide + counter_not_suicide

    print("Total common 100 words not in suicide detected data")
    for key, value in total_counter.most_common(100):
        print(f"{key}: {value}")
