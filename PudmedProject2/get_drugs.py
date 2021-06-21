import pandas as pd

def from_excel(path,**kwargs):
    drugs = pd.read_excel(path)
    df1 = drugs[[column]]
    return df1[column].drop_duplicates().tolist()


