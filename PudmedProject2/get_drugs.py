def from_excel(**kwargs):
    import pandas as pd
    path=kwargs.get("path") # "drug_mapping_v2.xlsx"
    drugs = pd.read_excel(path)
    column = kwargs.get("column")

    flat_list = []
    if column is None:
        for sublist in drugs.values.tolist():
            for item in sublist:
                if type(item) is str:
                    flat_list.append(item.replace("\u3000",""))
        return list(set(flat_list))
    else:
        print(f"Getting druglist from {path}, using columns: {''.join(column)}")
        for sublist in drugs.loc[:,column].values.tolist():
            for item in sublist:
                if type(item) is str:
                    flat_list.append(item.replace("\u3000",""))
        return list(set(flat_list))
    # return res.values.tolist()

def from_csv(**kwargs):
    import csv
    drugs = []
    with open(kwargs.get('path'), newline='') as inputfile:
        for row in csv.reader(inputfile):
            drugs.append(row[0])
    return drugs