import pandas as pd

filename = "Drug_mapping_v2.csv"

def drug_list():  # 함수
    drugs = pd.read_csv(filename)
    # print(drugs.shape)

    df1 = drugs[["ingredient"]]

    # all the ingredients, without dropping duplicates
    # return df1["ingredient"].tolist()

    # all the ingredients, without dropping duplicates
    return df1["ingredient"].drop_duplicates().tolist()


# if __name__ == "__main__":
#     print(drug_list())
