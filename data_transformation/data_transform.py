import os
import re

if __name__ == '__main__':
    path = 'data/'
    file_list = os.listdir(path)
    for i in range(len(file_list)):
        filename = file_list[i]
        print(f"current file : {filename}")
        with open("data/"+filename,"r",encoding="utf-8") as infile:
            with open('data_transformed/'+filename,"w+",encoding='utf-8') as outfile:
                temp = infile.read()
                temp = temp.replace("\n\n\n","\n\n")
                outfile.write(temp)