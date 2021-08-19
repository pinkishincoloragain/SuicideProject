import pandas as pd
def get_ADE(**kwargs):
    # output_file="DRUG-AE_transformed.txt"
    dfADE=pd.read_csv(kwargs.get("INF"), sep='|', names=['PMID','text','ADE','ADE_offsetfrom','ADE_offsetto', 'drug', 'drug_offsetfrom','drug_offsetto'])
    ades = dfADE.loc[:,'ADE']
    drugs = dfADE.loc[:,'drug']
    texts = dfADE.loc[:,'text']
    with open(kwargs.get("OUTF"), "w+") as outfile:
        for i in range(len(dfADE)):
            text = texts[i]
            ade = ades[i]
            drug = drugs[i]
            drug_idx = text.find(drug)
            ade_idx = text.find(ade)
            if drug_idx < ade_idx:
                idx = 1
            else:
                idx = 2
            text = text.replace(drug,f"<e{idx}>{drug}</e{idx}>")
            text = text.replace(ade, f"<e{3-idx}>{ade}</e{3-idx}>")
            text = text.replace(">-", "> -")
            res = f'{i+1}\t"{text}"\nDRUG-ADE(e{idx},e{3-idx})\nComment: DRUG-AE\n\n'
            outfile.write(res)
    return kwargs.get("OUTF")

def get_training_set(**kwargs):
    # rel_types=["Other", "Cause-Effect","DRUG-ADE"]
    rel_types = kwargs.get("rel_types")
    input_files=kwargs.get("INF")
    output_full=kwargs.get("OUTFULL")

    print(f"Filtering {','.join(rel_types)} relationships from {','.join(input_files)}")
    idx = 0
    if len(rel_types) == 0:
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

    with open(output_full,"w+") as outfile:
        with open(input_files[0], "r") as in1:
            train_data = in1.read().strip()
            for data in train_data.split("\n\n"):
                lines = data.split("\n")
                for rel in rel_types:
                    if rel in lines[1]:
                        text = lines[0].split("\t")[1]
                        outfile.write(f"{text}\n{lines[1]}\n{lines[2]}\n\n")
                        idx += 1
                        break

        with open(input_files[1], "r") as in2:
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

def sep_files(**kwargs):
    full_file = kwargs.get("FULLFILE")
    out_train = kwargs.get("OUTTRAIN")
    out_test = kwargs.get("OUTTEST")
    split_rate = kwargs.get("split_rate")  # TODO, in interval [0,1]


    with open(full_file, "r") as infile:
        full = infile.read().strip()
        writefile = open(out_train,"w+")
        idx = 1
        file_changed = False
        items = full.split("\n\n")
        next_file_idx = len(items) * float(split_rate)
        for item in items:
            writefile.write(f"{idx}\t{item}\n\n")
            idx+=1
            if idx > next_file_idx and not file_changed:
                writefile.close()
                writefile = open(out_test,"w+")
                file_changed = True
                idx = 1
        writefile.close()

    return out_train, out_test, split_rate

def main():
    DRUGADEname=get_ADE(INF='../zzz/ADEdataset/ADE-Corpus-V2/DRUG-AE.rel', OUTF="DRUG-AE_transformed.txt")
    # DRUGADEname=get_ADE(INF='DRUG-AE.rel', OUTF="DRUG-AE_transformed.txt")
    print(f"{DRUGADEname} successfully created.")
    output_full = get_training_set(
        INF=
        ['../RE_BERTs/data/SemEval2010_task8_all_data/SemEval2010_task8_training/TRAIN_FILE.txt',
         "DRUG-AE_transformed.txt"],
        rel_types=["Other", "Cause-Effect", "DRUG-ADE"],
        OUTFULL="full_file.txt",
        split_rate=0.9)
    # output_full = get_training_set(
    #     INF=['TRAIN_FILE.txt', "DRUG-AE_transformed.txt"],
    #     rel_types=["Other", "Cause-Effect", "DRUG-ADE"],
    #     OUTFULL="full_file.txt",
    #     split_rate=0.9
    # )
    trainsetname, testsetname, split_rate = \
        sep_files(FULLFILE="full_file.txt",
                  OUTTRAIN="train02.txt",
                  OUTTEST="test02.txt",
                  split_rate="0.9")

    print(f"Train {trainsetname} and Test {testsetname} sets with {str(split_rate)} split rate are successfully created.")

if __name__=="__main__":
    main()