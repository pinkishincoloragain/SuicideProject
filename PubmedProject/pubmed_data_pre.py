import os
import re

start = re.compile(r"^\d*[.]")
year = re.compile(r"20\d\d")
n = re.compile(r"\n")

year_pattern = re.compile
if __name__ == '__main__':
    path = 'data/'
    file_list = os.listdir(path)
    for i in range(len(file_list)):
        filename = file_list[i]
        print(f"current file : {filename}")
        with open("data/"+filename,"r",encoding="utf-8") as infile:
            with open('result/'+filename +' result.txt',"w+",encoding='utf-8') as outfile:
                temp = infile.read()
                splitted = list(temp.split("\n\n"))
                for item in splitted:
                    item.strip()
                    if 'doi' in item and year.search(item):
                        item = re.sub(pattern=n,repl='',string=item)
                        outfile.write(item)
                        outfile.write('\n\n')
                    # else: print("not!!!!!: ",item)

                    if len(item) > 200:
                        if "Author information:" in item:
                            continue
                        # outfile.write(item)
                        item = re.sub(pattern=n,repl='',string=item)
                        dotsplit = list(item.split("."))
                        # print(dotsplit)
                        for i in range(len(dotsplit)):
                            if len(dotsplit[i]) > 0:
                                outfile.write(str(dotsplit[i].lstrip()) + ".\n")
                        outfile.write('\n')
