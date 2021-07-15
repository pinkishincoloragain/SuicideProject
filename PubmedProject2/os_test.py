import os


path = "Drug_mapping_v2.csv"
print(os.path.exists("Drug_mapping_v2.csv"))
print(os.path.exists(""))

name, extension = os.path.splitext("Drug_mapping_v2.csv")

print(name,extension)
