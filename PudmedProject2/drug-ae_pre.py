import pandas as pd
def write_file():
    dfADE=pd.read_csv('DRUG-AE.rel', sep='|', names=['PMID','text','ADE','ADE_offsetfrom','ADE_offsetto', 'drug', 'drug_offsetfrom','drug_offsetto'])
    ades = dfADE.loc[:,'ADE']
    drugs = dfADE.loc[:,'drug']
    texts = dfADE.loc[:,'text']
    with open("DRUG-AE_transformed.txt", "w+") as outfile:
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
            res = f'{i}\t"{text}"\nDRUG-ADE(e{idx},e{3-idx})\nComment: DRUG-AE\n\n'
            outfile.write(res)

if __name__=="__main__":
    write_file()



