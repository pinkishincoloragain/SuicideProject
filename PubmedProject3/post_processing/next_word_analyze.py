
# 이건 간단해서 읽을 수 있지 않을까..!
# 두 번째 오는 단어들을 set으로 반환함.
import re

special = re.compile(r'[\d"(),.\-%→/®<>;:+]')

if __name__ == "__main__":
    with open("temp.txt","r", encoding='UTF8') as infile:
        with open("next_words_each.txt", "r") as outfile:
            data = infile.read()
            temp = data.split("\n")
            print(temp)
            both_words = {}
            next_words = set()
            for i in range(len(temp)-1):
                temp[i] = re.sub(pattern=special,string=temp[i],repl="")
                print(temp[i])

                try:
                    target, next_word = temp[i].lower().split()
                except:
                    continue
                if target not in both_words.keys():
                    both_words[target] = set()
                both_words[target].add(target + " " + next_word)
                next_words.add(next_word)

            # for drugs in both_words.keys():
            #     for words in both_words[drugs]:
            #         print(words)
            # print(both_words)
            print(sorted(next_words))


# calcium chloride
# calcium salts
# calcium boluses
# calcium gluconate
# calcium channels
# calcium chloride
# calcium gluconate
# calcium oxalate
# calcium ion
# calcium polysulfide
# calcium EDTA

