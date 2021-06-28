def from_excel(**kwargs):
    import pandas as pd
    import re
    pattern1 = re.compile(r'\([^)]*\)')
    replace_dict = {
        "fish oil": "omega-3"
    }
    excp_dict = [
        "immune globulin",
        "immune",
        "crotalidae immune f(ab')2"
    ]
    path=kwargs.get("path") # "drug_mapping_v2.xlsx"
    drugs = pd.read_excel(path)
    columns = kwargs.get("columns")

    flat_list = []
    if columns is None:
        for sublist in drugs.values.tolist():
            for item in sublist:
                if type(item) is str:
                    flat_list.append(item.replace("\u3000",""))
        return list(set(flat_list))
    else:
        print(f"Getting druglist from {path}, using columns: {' '.join(columns)}")
        for sublist in drugs.loc[:,columns].values.tolist():
            for item in sublist:
                if type(item) is str:
                    flat_list.append(item.replace("\u3000"," "))
        drop_exp = []


        for item in flat_list:
            origin = item
            if "," in item:
                print("a ", item)
                idx = item.find(",")
                item = item[:idx]
                print("b ", item)
                drop_exp.append(item.strip())

            if "(" in item:
                print("i-before ", item)
                item = re.sub(pattern=pattern1,repl="",string=item)
                print("i-after ", item)
                drop_exp.append(item.strip())

            else:
                drop_exp.append(item)

        res = list(set(drop_exp))
        for item in res:
            for excp in excp_dict:
                if excp in item:
                    print("rmv: ",excp, item)
                    res.remove(item)
                    break
            if item in replace_dict.keys():
                print("rpl: ", item,":", replace_dict[item])
                # item = replace_dict[item]
                res.remove(item)
                res.append(replace_dict[item])

    return list(set(res))

    # return res.values.tolist()

def from_csv(**kwargs):
    import csv
    drugs = []
    with open(kwargs.get('path'), newline='') as inputfile:
        for row in csv.reader(inputfile):
            drugs.append(row[0])
    return drugs