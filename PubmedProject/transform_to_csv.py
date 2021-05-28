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
                cnt = 0
                for i in range(0,len(splitted)-1,2):
                    wr.writerow([i/2,splitted[i],splitted[i+1]])

