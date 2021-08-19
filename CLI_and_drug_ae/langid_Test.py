import langid
from langdetect import detect

test_file = []
eng_langdetect = []
eng_langid = []
only_id=[]
only_detect = []
open_file = open("C:\\Users\\leeja\\Sucide Project\\WebCrawling\\data\\Baclofen 2016-09-01~2016-10-01.txt", 'rt',encoding='UTF-8')
open_file2 = open("C:\\Users\\leeja\\Sucide Project\\PudmedProject2\\langlib_result.txt", 'wt', encoding='UTF-8')
while True:
    line_str = open_file.readline()
    if line_str == "":
        break
    else:
        if "text" in line_str:
            line_str = line_str.strip()
            line_str = line_str.strip("\"text\":")
            line_str = line_str.strip("@")
            #print(line_str)
            test_file.append(line_str)
        #test_file
#print("\"")
#reader = open_file.readline()
for word in test_file:
    if detect(word) == "en":
        eng_langdetect.append(word)

    detected = langid.classify(word)
    if "en" in detected:
        eng_langid.append(word)

print("\n<langid>\n")
open_file2.write("langid\n")
i=1
for word in eng_langid:
    if word not in eng_langdetect:
        only_id.append(word)
    print("[",i, "]")
    #open_file2.write("[", i, "]")
    print(word)
    open_file2.write(word + "\n\n")


    i+=1


print("\n<langdetect>\n")
open_file2.write("langdetect\n")
i=1
for word in eng_langdetect:
    if word not in eng_langid:
        only_detect.append(word)
    print("[",i ,"]")
    #open_file2.write("[",i ,"]")
    print(word)

    open_file2.write(word + "\n\n")
    i+=1

print("<only langid>\n")
for word in only_id:
    print(word+"\n")

print("<only langdetect>")
for word in only_detect:
    print(word+"\n")



