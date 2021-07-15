import os
from datetime import date


path = "Drug_mapping_v2.csv"
print(os.path.exists("Drug_mapping_v2.csv"))
print(os.path.exists(""))

name, extension = os.path.splitext("Drug_mapping_v2.csv")

print(name,extension)
today = date.today()

# dd/mm/YY
d1 = today.strftime("%d/%m/%Y")
print("d1 =", d1)