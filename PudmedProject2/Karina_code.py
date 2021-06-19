import pandas as pd
# import get_drugs
# drugarray=get_drugs.from_excel(path="Drug_mapping_v2.xlsx")
# 이런 형식으로 만들어져야 함

dfADE=pd.read_csv('DRUG-AE.rel', sep='|', names=['PMID','text','ADE','ADE_offsetfrom','ADE_offsetto', 'drug', 'drug_offsetfrom','drug_offsetto'])
# 이런 식으로 뽑을듯 !
