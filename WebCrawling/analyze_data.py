import os

path = 'data/'
file_list = os.listdir(path)
for i in range(len(file_list)):
    filename = file_list[i]
    print(f"current file : {filename}")
    with open("data/" + filename, "r", encoding="utf-8") as infile:
       print(f"currently analyzing " + filename)
