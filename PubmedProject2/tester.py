import get_drugs
# drugarray=get_drugs.from_excel(path="Drug_mapping_v2.xlsx", column=["ingredient", "ingredient_1"])
drugarray=get_drugs.from_excel(path="Drug_mapping_v2.xlsx", columns=["ingredient", "ingredient_1"])
# drugarray=get_drugs.from_excel(path="Drug_mapping_v2.xlsx")

print(drugarray)
