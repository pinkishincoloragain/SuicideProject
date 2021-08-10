
# 이건 간단해서 읽을 수 있지 않을까..!
# 두 번째 오는 단어들을 set으로 반환함.
if __name__ == "__main__":
    with open("temp2.txt","r", encoding='UTF8') as infile:
        with open("next_words_each.txt", "r") as outfile:
            data = infile.read()
            temp = data.split("\n")
            print(temp)
            next_words = {}
            for i in range(len(temp)-1):
                target, next_word = temp[i].split()
                if target not in next_words.keys():
                    next_words[target] = set()
                next_words[target].add(target + " " + next_word)

            for drugs in next_words.keys():
                for words in next_words[drugs]:
                    print(words)
            print(next_words)

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

