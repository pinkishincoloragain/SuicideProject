import pandas as pd
import get_drugs
drug_num = get_drugs.drug_list()
# drugarray=get_drugs.from_excel(path="Drug_mapping_v2.xlsx")
# 이런 형식으로 만들어져야 함

def write_file():
    dfADE=pd.read_csv('DRUG-AE.rel', sep='|', names=['PMID','text','ADE','ADE_offsetfrom','ADE_offsetto', 'drug', 'drug_offsetfrom','drug_offsetto'])
    #  'PMID', 'text', 'ADE', 'ADE_offsetfrom', 'ADE_offsetto', 'drug','drug_offsetfrom', 'drug_offsetto'

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
            # print(text,drug_idx, ade_idx)

            if drug_idx < ade_idx:
                idx = 1
            else:
                idx = 2

            text = text.replace(drug,f"<e{idx}>{drug}</e{idx}>")
            text = text.replace(ade, f"<e{3-idx}>{ade}</e{3-idx}>")

            # drug causes ADE!
            # if first found word is drug -> write Drug-ADE(e1,e2)
            # if first found word is ADE -> write Drug-ADE(e2,e1)

            res = f'{i}\t"{text}"\nDRUG-ADE(e{idx},e{3-idx})\nComment: DRUG-AE\n\n'
            outfile.write(res)

if __name__=="__main__":
    write_file()

# 이런 식으로 뽑을듯 !



