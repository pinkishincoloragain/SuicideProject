import os
import csv

if __name__ == '__main__':
    path = 'result2/'
    file_list = os.listdir(path)
    for i in range(len(file_list)):
        filename = file_list[i]
        print(f"current file : {filename}")
        with open("result2/"+filename,"r",encoding="utf-8") as infile:
            with open('csv_transformed/'+filename +'.csv',"w+",encoding='utf-8') as outfile:
                wr = csv.writer(outfile)
                temp = infile.read()
                splitted = list(temp.split("\n\n"))
                idx = 0
                abstract=""
                subject=""
                for k in range(0,len(splitted)-1):
                    # print(splitted[k])
                    if splitted[k][0].isdigit():
                        # print("!!!!!!!!!!!!!!!")
                        wr.writerow([idx, subject, abstract])
                        idx += 1
                        abstract = ""
                        subject = ""
                        subject = splitted[k]
                    else:
                        abstract = abstract + splitted[k]
                        # print(abstract)
                    # if idx > 10:
                    #     break

