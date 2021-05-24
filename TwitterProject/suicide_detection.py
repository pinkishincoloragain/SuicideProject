import csv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


Text = []
stop_words = set(stopwords.words("english"))
punctuations=["?",":","!",".",",",";","--","-","’",";","[","]","”", "“",".."]


with open('test.csv','w',newline='') as csvfile:
    fieldnames = ['id','text']
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    thewriter.writeheader()
    id = 1
    for text in Text:
        Text_Tokenized = word_tokenize(text)
        words = []
        for word in Text_Tokenized:
            if not word in stop_words:
                if not word in punctuations:
                    words.append(word)
        if len(words) > 0:
            thewriter.writerow({'id' : id, 'text':words})
            id +=1
