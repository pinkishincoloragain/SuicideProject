import pandas as pd
def write_file():
    dfADE=pd.read_csv('DRUG-AE.rel', sep='|',
                      names=['PMID','text','ADE','ADE_offsetfrom','ADE_offsetto', 'drug', 'drug_offsetfrom','drug_offsetto']
                      )
    ades = dfADE.loc[:,'ADE']
    drugs = dfADE.loc[:,'drug']
    texts = dfADE.loc[:,'text']
    with open("DRUG-AE_transformed.txt", "w+") as outfile:
        for i in range(len(dfADE)):
            # idx,ade_idx,drug_idx = 0,0,0
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
            text = text.replace(">-","> -")
            res = f'{i}\t"{text}"\nDRUG-ADE(e{idx},e{3-idx})\nComment: DRUG-AE\n\n'
            outfile.write(res)

def get_training_set(**kwargs):
    # rel_types=["Other", "Cause-Effect","DRUG-ADE"]
    rel_types = kwargs.get("rel_types")
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

    with open("train01.txt","w+") as outfile:
        with open("TRAIN_FILE.TXT","r") as in1:
            train_data = in1.read().strip()
            for data in train_data.split("\n\n"):
                lines = data.split("\n")
                for rel in rel_types:
                    if rel in lines[1]:
                        text = lines[0].split("\t")[1]
                        outfile.write(f"{idx}\t{text}\n{lines[1]}\n{lines[2]}\n\n")
                        idx+=1
                        break

        with open("DRUG-AE_transformed.txt", "r") as in2:
            drug_data = in2.read().strip()
            for data in drug_data.split("\n\n"):
                lines = data.split("\n")
                for rel in rel_types:
                    if rel in lines[1]:
                        text = lines[0].split("\t")[1]
                        outfile.write(f"{idx}\t{text}\n{lines[1]}\n{lines[2]}\n\n")
                        idx += 1
                        break
    return

if __name__=="__main__":
    # write_file()
    get_training_set(rel_types=["Other", "Cause-Effect","DRUG-ADE"])
    # get_training_set(rel_types=["DRUG-ADE"])
    # get_training_set(rel_types=[])


