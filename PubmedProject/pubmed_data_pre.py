import os

if __name__ == '__main__':
    path = 'data/'
    file_list = os.listdir(path)
    for i in range(len(file_list)):
        filename = file_list[i]
        print(f"current file : {filename}")
        with open("data/"+filename,"r",encoding="utf-8") as infile:
            with open ('result/'+filename +' result.csv',"w+",encoding='utf-8') as outfile:
                temp = infile.read()
                splitted = list(temp.split("\n\n"))
                for item in splitted:
                    if len(item) > 200:
                        if "Author information:" in item:
                            continue
                        # outfile.write(item)
                        item.replace("\n"," ")
                        item.replace("\r\n", " ")
                        item.replace("\r", " ")
                        dotsplit = list(item.split("."))
                        for sen in dotsplit:
                            outfile.write(sen)
                            # outfile.write('.')
                            # outfile.write("\n")
                        outfile.write('\n\n')
