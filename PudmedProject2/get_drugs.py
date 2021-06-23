import pandas as pd

# def from_excel(path="drug_mapping_v2.xlsx",column="ingredient"):
def from_excel(path="drug_mapping_v2.xlsx",**kwargs):
    drugs = pd.read_excel(path)

    column = kwargs.get("column")
    flat_list = []

    if column is None:
        for sublist in drugs.values.tolist():
            for item in sublist:
                flat_list.append(item)
        return list(set(flat_list))


    else:
        for sublist in drugs.loc[:,column].values.tolist():
            for item in sublist:
                flat_list.append(item)
        return list(set(flat_list))
    # return res.values.tolist()
