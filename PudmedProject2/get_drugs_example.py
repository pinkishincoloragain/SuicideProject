def from_excel(**kwargs):
    import pandas as pd
    path=kwargs.get("path") #"drug_mapping_v2.xlsx"
    drugs = pd.read_excel(path)
    columns = kwargs.get("columns")
    print(f"Getting druglist from {path}, using columns: { ''.join(columns)}")
    flat_list = []
    if columns is None:
        for sublist in drugs.values.tolist():
            for item in sublist:
                flat_list.append(item)
        return list(set(flat_list))
    else:
        for sublist in drugs.loc[:,columns].values.tolist():
            for item in sublist:
                flat_list.append(item)
        return list(set(flat_list))
    # return res.values.tolist()

def from_csv(**kwargs):
    import csv
    drugs = []
    with open(kwargs.get('path'), newline='') as inputfile:
        for row in csv.reader(inputfile):
            drugs.append(row[0])
    return drugs