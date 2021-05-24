
filename = "power_word_count_2_.csv"
with open("result/" + filename, "r", encoding="utf-8") as infile:
    with open("result/2.csv","w+",encoding="utf-8") as infile_2:
        while True:
            line = infile.readline()
            if not line:
                break




