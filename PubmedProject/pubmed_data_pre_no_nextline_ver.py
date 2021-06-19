import os
import re

start = re.compile(r"^\d*[.]")
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
year = re.compile(r"20\d\d")
n = re.compile(r"\n")

year_pattern = re.compile
if __name__ == '__main__':
    path = 'data_transformed/'
    file_list = os.listdir(path)
    for i in range(len(file_list)):
        filename = file_list[i]
        print(f"current file : {filename}")
        with open("data/"+filename,"r",encoding="utf-8") as infile:
            with open('result2/'+filename +' result.txt',"w+",encoding='utf-8') as outfile:
                temp = infile.read()
                splitted = list(temp.split("\n\n"))
                for i in range(len(splitted)):
                    splitted[i] = splitted[i].strip()
                for item in splitted:
                    item.strip()
                    print(item[0])
                    if year.search(item) and start.match(item):
                        item = re.sub(pattern=n,repl='',string=item)
                        outfile.write(item)
                        outfile.write('\n\n')
                    if len(item) > 200:
                        if "Author information:" in item or "Collaborators:" in item:
                            continue
                        # outfile.write(item)
                        item = re.sub(pattern=n,repl='',string=item)
                        dotsplit = list(item.split("."))
                        # print(dotsplit)
                        for i in range(len(dotsplit)):
                            if len(dotsplit[i]) > 0:
                                outfile.write(str(dotsplit[i].lstrip()) + ". ")
                        outfile.write('\n\n')
