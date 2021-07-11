import pandas as pd
def get_ADE(**kwargs):
    # output_file="DRUG-AE_transformed.txt"
    dfADE=pd.read_csv(kwargs.get("INF"), sep='|', names=['PMID','text','ADE','ADE_offsetfrom','ADE_offsetto', 'drug', 'drug_offsetfrom','drug_offsetto'])
    ades = dfADE.loc[:,'ADE'] # dataframe에서 뽑기
    drugs = dfADE.loc[:,'drug']
    texts = dfADE.loc[:,'text']
    with open(kwargs.get("OUTF"), "w+") as outfile: # OUTFILE에 쓰는 거.
        for i in range(len(dfADE)):
            text = texts[i]
            ade = ades[i]
            drug = drugs[i]
            drug_idx = text.find(drug)
            ade_idx = text.find(ade)
            if drug_idx < ade_idx: # drug랑 ade idx 찾기 ! - 먼저 나오면 1 나중에 나오면 2
                idx = 1
            else:
                idx = 2
            text = text.replace(drug,f"<e{idx}>{drug}</e{idx}>") # 1 아니면 2 바꾸기
            text = text.replace(ade, f"<e{3-idx}>{ade}</e{3-idx}>") # 2 아니면 1 바꾸기
            text = text.replace(">-", "> -")
            res = f'{i+1}\t"{text}"\nDRUG-ADE(e{idx},e{3-idx})\nComment: DRUG-AE\n\n'
            outfile.write(res)
    return kwargs.get("OUTF")

def get_training_set(**kwargs):
    # rel_types=["Other", "Cause-Effect","DRUG-ADE"]
    rel_types = kwargs.get("rel_types") # 뽑아낼 relationship type
    input_files=kwargs.get("INF") # 읽는 파일.
    output_full=kwargs.get("OUTFULL") # 전체 데이터 다 있는거. index 없음

    print(f"Filtering {','.join(rel_types)} relationships from {','.join(input_files)}")
    idx = 0

    if len(rel_types) == 0: # relation 명시 안하면 다 뽑아버림. 이게 전체 relationship 종류.
        rel_types = ['Instrument-Agency',
                     'Entity-Origin',
                     'Other',
                     'Component-Whole',
                     'Content-Container',
                     'Member-Collection',
                     'Cause-Effect',
                     'Product-Producer',
                     'Entity-Destination',
                     'Product-Producer',
                     'Message-Topic',
                     'DRUG-ADE']

    with open(output_full,"w+") as outfile: # 전체 파일 쓰기
        with open(input_files[0], "r") as in1: # 첫번째 파일. TRAIN_FILE
            train_data = in1.read().strip() #
            for data in train_data.split("\n\n"):
                lines = data.split("\n")
                for rel in rel_types:
                    if rel in lines[1]:
                        text = lines[0].split("\t")[1]
                        outfile.write(f"{text}\n{lines[1]}\n{lines[2]}\n\n")
                        idx += 1

                        break

        with open(input_files[1], "r") as in2: # 두번째 파일. DRUG_ADE
            drug_data = in2.read().strip()
            for data in drug_data.split("\n\n"):
                lines = data.split("\n")
                for rel in rel_types:
                    if rel in lines[1]:
                        text = lines[0].split("\t")[1]
                        outfile.write(f"{text}\n{lines[1]}\n{lines[2]}\n\n")
                        idx += 1
                        break

    return output_full

def sep_files(**kwargs): # FULL_FILE 에서 분리하는 함수
    full_file = kwargs.get("FULLFILE") # 전체 파일
    out_train = kwargs.get("OUTTRAIN") # TRAIN_FILE 출력할 곳.
    out_test = kwargs.get("OUTTEST") # TEST_FILE 출력할 곳.
    split_rate = kwargs.get("split_rate")  # TODO, in interval [0,1]
    rel_types = kwargs.get("rel_types")
    rel_cnt = [0] * len(rel_types)

    with open(full_file, "r") as infile:
        full = infile.read().strip()
        writefile_train = open(out_train,"w+")
        writefile_test = open(out_test,"w+")
        idx = 1
        idx_test = 1
        items = full.split("\n\n")
        for item in items: #rel_types 각각 몇개씩 존재하는지 count
            for i in range(len(rel_types)):
                if rel_types[i] in item.split("\n")[1]:
                    rel_cnt[i] += 1
                    break
        for i in range(len(rel_cnt)): # 몇 개 뽑아야하는지 계산
            rel_cnt[i] = rel_cnt[i] * float(split_rate)

        for item in items: # 뽑아서 train02.txt에 write 나머지는 test02.txt에 write
            for i in range(len(rel_types)):
                if rel_types[i] in item.split("\n")[1]:
                    if rel_cnt[i] >0:
                        writefile_train.write(f"{idx}\t{item}\n\n")  # 인덱스 쓰고 아이템 씁니다
                        idx += 1
                        rel_cnt[i] -= 1
                        break
                    else:
                        writefile_test.write(f"{idx_test}\t{item}\n\n")  # 인덱스 쓰고 아이템 씁니다
                        idx_test += 1
        writefile_train.close()
        writefile_test.close()
    return out_train, out_test, split_rate

def main():
    #DRUGADEname=get_ADE(INF='../zzz/ADEdataset/ADE-Corpus-V2/DRUG-AE.rel', OUTF="DRUG-AE_transformed.txt")
    DRUGADEname=get_ADE(INF='DRUG-AE.rel', OUTF="DRUG-AE_transformed.txt")
    print(f"{DRUGADEname} successfully created.")
    # output_full = get_training_set(
    #     INF=
    #     ['../RE_BERTs/data/SemEval2010_task8_all_data/SemEval2010_task8_training/TRAIN_FILE.txt',
    #      "DRUG-AE_transformed.txt"],
    #     rel_types=["Other", "Cause-Effect", "DRUG-ADE"],
    #     OUTFULL="full_file.txt",
    #     split_rate=0.9)
    output_full = get_training_set(
        INF=['TRAIN_FILE.txt', "DRUG-AE_transformed.txt"],
        rel_types=["Other", "Cause-Effect", "DRUG-ADE"],
        OUTFULL="full_file.txt",
        split_rate=0.9
    )
    trainsetname, testsetname, split_rate = \
        sep_files(FULLFILE="full_file.txt", # 이건 전체 파일에서 읽고
                  OUTTRAIN="train02.txt",
                  OUTTEST="test02.txt",
                  rel_types = ["Other", "Cause-Effect", "DRUG-ADE"],
                  split_rate="0.9")

    print(f"Train {trainsetname} and Test {testsetname} sets with {str(split_rate)} split rate are successfully created.")

if __name__=="__main__":
    main()

