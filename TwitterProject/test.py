import sys
import tweepy as tw
import csv
import nltk
nltk.download('averaged_perceptron_tagger')

consumer_key = 'nnBnOiWoO2HGiCCGmPBAxI82V'
consumer_secret = 'JdDPNCiXNE3iZ2kcGh5mUn7nQV9lubNrx0uOXEhEFXIMpgVuXz'
access_token = '1403921240-WSYAheMHeXGyMt52ZOoBAiBl1hWTbEy7mCVxvAs'
access_token_secret = 'SfO6l3yLMsEyLlAaCsMuiTMkDWtZGpD5AurPtIvS1mmjC'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

def collect(tar,dat,amt):
    query = tar + " -filter:retweets"

    # collect tweets about target
    cursor = tw.Cursor(api.search,
                       q=query,
                       lang="en",
                       since=dat)

    # can use binary file for better speed
    with open("tweets.txt", "w", encoding="utf8", errors='ignore') as outfile:
        case = 1
        for tweet in cursor.items():
            outfile.write(tweet.text.strip())
            case += 1
            if case % 10 == 0:
                print(f"({case} / {amount}) tweets collected ..")
            if case > int(amt):
                break


def analyze():

    with open("tweets.txt","r", encoding="utf8", errors='ignore') as infile:
        data = infile.read()

    symptoms = []
    with open("symptoms.CSV","r", encoding="utf8", errors='ignore') as infile:
        r = csv.reader(infile)
        for symptom in r:
            symptoms.extend(symptom)

    tweet_in = str(data).lower()
    tokenizer = nltk.tokenize.RegexpTokenizer( '[\w]+')
    tokens = tokenizer.tokenize(tweet_in)
    tagged = nltk.pos_tag(tokens)

    # collecting only verbs and nouns
    # NN    noun, common, singular or mass
    # NNP   noun, proper, singular
    # NNS   noun, common, plural
    # VB	verb (ask)
    # VBG	verb gerund (judging)
    # VBD	verb past tense (pleaded)
    # VBN	verb past participle (reunified)
    # VBP	verb, present tense not 3rd person singular(wrap)
    # VBZ	verb, present tense with 3rd person singular (bases)

    res = list(word for word,pos in tagged if pos in ['NN','NNP','NNS','VB','VBG','VBD','VBN','VBP','VBZ'] and word in symptoms)

    freq = nltk.FreqDist(res)
    freq.plot(10,cumulative=False)

    return freq.most_common()


if __name__ == '__main__':

    # input data
    print("meidicine")
    target = sys.stdin.readline().strip()
    print("Input date to start searching. (format:yyyy-mm-dd)")
    date_since = sys.stdin.readline().strip()
    print("Input target amount of tweets to collect: ")
    amount = sys.stdin.readline().strip()

    collect(target,date_since,amount)
    matrix = analyze()

    for i in range(len(matrix)):
        print(f"{matrix[i][0]}: {matrix[i][1]}")
