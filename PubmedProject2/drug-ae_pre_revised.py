import pandas as pd
def get_ADE(**kwargs):
    # output_file="DRUG-AE_transformed.txt"
    dfADE=pd.read_csv(kwargs.get("INF"), sep='|', names=['PMID','text','ADE','ADE_offsetfrom','ADE_offsetto', 'drug', 'drug_offsetfrom','drug_offsetto'])
    ades = dfADE.loc[:,'ADE']
    drugs = dfADE.loc[:,'drug']
    texts = dfADE.loc[:,'text']
    with open(kwargs.get("OUTF"), "w+") as outfile:
        for i in range(len(dfADE)):
            idx,ade_idx,drug_idx = 0,0,0
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
    output_train=kwargs.get("OUTTRAIN")
    output_test = kwargs.get("OUTTEST") #TODO
    split_rate=kwargs.get("rate") #TODO, in interval [0,1]

    print(f"Filtering {','.join(rel_types)} relationships from {','.join(input_files)}")
    all_rel = False
    idx = 0
    if len(rel_types) == 0:
        all_rel = True
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

    with open(output_train,"w+") as outfile:
        with open(input_files[0],"r") as in1:
            train_data = in1.read().strip()
            for data in train_data.split("\n\n"):
                lines = data.split("\n")
                for rel in rel_types:
                    if rel in lines[1]:
                        text = lines[0].split("\t")[1]
                        outfile.write(f"{idx+1}\t{text}\n{lines[1]}\n{lines[2]}\n\n")
                        idx+=1
                        break

        with open(input_files[1], "r") as in2:
            drug_data = in2.read().strip()
            for data in drug_data.split("\n\n"):
                lines = data.split("\n")
                for rel in rel_types:
                    if rel in lines[1]:
                        text = lines[0].split("\t")[1]
                        outfile.write(f"{idx+1}\t{text}\n{lines[1]}\n{lines[2]}\n\n")
                        idx += 1
                        break

    return output_train, output_test, split_rate

def main():
    DRUGADEname=get_ADE(INF='../zzz/ADEdataset/ADE-Corpus-V2/DRUG-AE.rel', OUTF="DRUG-AE_transformed.txt")
    print(f"{DRUGADEname} successfully created.")
    trainsetname, testsetname, split_rate = get_training_set(
        INF=
        ['../RE_BERTs/data/SemEval2010_task8_all_data/SemEval2010_task8_training/TRAIN_FILE.txt',
         "DRUG-AE_transformed.txt"], rel_types=["Other", "Cause-Effect", "DRUG-ADE"],
        OUTTRAIN="train02.txt", OUTTEST="test02.txt", split_rate=0.9)
    print(f"Train {trainsetname} and Test {testsetname} sets with {str(split_rate)} split rate are successfully created.")

if __name__=="__main__":
    main()