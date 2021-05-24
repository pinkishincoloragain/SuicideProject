import os
from langdetect import detect
from collections import Counter

# input = sys.stdin.readline()
# detected = detect('안녕하세요')

# print(detected)

temp = []

file_list = os.listdir("/Users/sonmyeongbin/PycharmProjects/TwitterProject/data")

for i in range(1):
    print(f"Start detecting: {file_list[i]}")
    with open(str("data/"+file_list[i]), "r", encoding="utf-8") as infile:
        while True:
            line = infile.readline()
            if not line:
                break
            if "text" in line:
                line.replace("text","")
                print(f"text:{line}\nlang={detect(line)}\n")
                temp.append(detect(line))

    print(f"Ended detecting: {file_list[i]}")

lang_counter = Counter(temp)
print(lang_counter.most_common(len(lang_counter)))

