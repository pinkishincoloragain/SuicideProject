def from_excel(**kwargs):
    import pandas as pd
    import re
    pattern1 = re.compile(r'\([^)]*\)')
    replace_dict = {
        "fish oil": "omega-3"
    }
    excp_dict = [
        # "immune globulin",
        # "immune",
        # "crotalidae immune f(ab')2",
        # "factor",
        "other",
        "",
        " "
    ]

    path=kwargs.get("path") # "drug_mapping_v3_210726_2.xlsx"
    drugs = pd.read_excel(path)
    columns = kwargs.get("columns")

    flat_list = []
    if columns is None:
        for sublist in drugs.values.tolist():
            for item in sublist:
                if type(item) is str and ("other" not in item) and not ("oil" in item and len(item) == 3):
                    flat_list.append(item.replace("\u3000"," ").strip())
    else:
        print(f"Getting druglist from {path}, using columns: {' '.join(columns)}")
        for sublist in drugs.loc[:,columns].values.tolist():
            for item in sublist:
                if type(item) is str and ("other" not in item) and not ("oil" in item and len(item) == 3):
                    flat_list.append(item.replace("\u3000"," ").strip())

    # drop_exp = []
    # for item in flat_list:
    #     if "," in item:
    #         idx = item.find(",")
    #         item = item[:idx]
    #         drop_exp.append(item.strip())
    #
    #     if "(" in item:
    #         item = re.sub(pattern=pattern1,repl="",string=item)
    #         drop_exp.append(item.strip())
    #
    #     if "/" in item:
    #         temp = item.split("/")
    #         for i in range(len(temp)):
    #             drop_exp.append(temp[i].strip())
    #
    #     else:
    #         drop_exp.append(item.strip())

    # res = list(set(drop_exp))
    # for item in res:
    #     for excp in excp_dict:
    #         if excp in item:
    #             res.remove(item)
    #             break
    #     if item in replace_dict.keys():
    #         res.remove(item)
    #         res.append(replace_dict[item])

    return sorted(list(set(x for x in flat_list if x not in excp_dict)))
    # return sorted(list(set(res)))
    # return res.values.tolist()

def from_csv(**kwargs):
    import csv
    drugs = []
    with open(kwargs.get('path'), newline='') as inputfile:
        for row in csv.reader(inputfile):
            drugs.append(row[0])
    return drugs

if __name__ == "__main__":
    columns = []
    for i in range(9):
        columns.append("ingredient_" + str(i+1))
    temp = from_excel(path="drug_mapping_v3_210726_2.xlsx", columns=columns)
    with open("test.txt","w+") as f:
        for item in temp:
            f.write(item + "\n")
