
import pandas as pd
import csv
from nltk.corpus import stopwords, words
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize
import nltk



class Pre:
    def __init__(self):
        pd.options.display.max_colwidth = 100
        pass

    def normalizeCase(self, inFile, outputCSV):
        process = pd.read_csv(inFile)

        print("Original: \n", process["selftext"].head(n=3))

        process['selftext'] = process['selftext'].str.lower()
        print("Lower:\n ",process["selftext"].head(n=3))

        process['selftext'] = process['selftext'].str.replace('[^\w\s]',' ')
        print("Remove Punctuations:\n ", process["selftext"].head(n=3))

        process['selftext'] = process['selftext'].str.replace('\\n', ' ')
        print("Remove New Lines:\n ", process["selftext"].head(n=3))

        stop = stopwords.words('english')
        englishWords = set(words.words())
        process['selftext'] = process['selftext'].apply(
            lambda x: " ".join(x for x in str(x).strip().split() if (x in englishWords or not x.isalpha()) and len(x) >=3 and x not in stop))
        print("Remove Stopwords:\n ", process["selftext"].head(n=3))

        lemmatizer = WordNetLemmatizer()
        stemmer = PorterStemmer()
        process['selftext'] = process['selftext'].apply(
            lambda x: " ".join([lemmatizer.lemmatize(word) for word in x.split()]))
        print("Lemmatize:\n ", process["selftext"].head(n=3))
        process['selftext'] = process['selftext'].apply(lambda x: " ".join([stemmer.stem(word) for word in x.split()]))
        print("Stemmatize:\n ", process["selftext"].head(n=3))

        MostFreq = pd.Series(' '.join(process['selftext']).split()).value_counts()[:3500]
        # LeastFreq = pd.Series(' '.join(process['selftext']).split()).value_counts()#[-16200:]
        # self.frequentWords(LeastFreq)
        print(process.shape)
        print(process["selftext"].head())
        print(MostFreq)
        # print(LeastFreq)
        process['selftext'] = process['selftext'].apply(
            lambda x: " ".join(x for x in str(x).strip().split() if x in MostFreq))
        LeastFreq = pd.Series(' '.join(process['selftext']).split()).value_counts()[-2000:]

        print(process["selftext"].head())
        print(LeastFreq)

        header = ['author', 'subreddit', 'created_utc', 'score', 'selftext']
        process.to_csv(outputCSV, columns=header)
        pass

    def frequentWords(self, freqWords):
        freqWords.to_csv('freqWordsInTS2.csv')



Pre.normalizeCase("test.csv","out.csv")
