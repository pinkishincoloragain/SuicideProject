
if __name__ == "__main__":
    with open("temp.txt","r") as infile:
        with open("next_words_each.txt", "r") as outfile:
            data = infile.read()
            temp = data.split("\n")
            print(temp)
            next_words = {}
            for i in range(len(temp)):
                target, next_word = temp[i].split()
                if target not in next_words.keys():
                    next_words[target] = set()
                print(next_words)
                next_words[target].add(next_word)

            print(next_words)



