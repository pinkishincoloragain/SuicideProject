import get_drugs
drugarray=get_drugs.from_excel(path="Drug_mapping_v2_excel.xlsx", column="ingredient")
print(drugarray)