import get_abstracts_pubmed
import pandas as pd
from datetime import date


# abstracts, drugs, queries = get_abstracts_pubmed.main(email="???", druglist_path="../../data/Drug_mapping_v2.xlsx", columns=["ingredient", "ingredient_1"],
#                                         max_results=100000, from_date="1990/01/01", to_date="2021/07/07", mesh=True, case_report=True)
# abstracts, drugs, queries = get_abstracts_pubmed.main(email="???", druglist_path="Drug_mapping_v2.xlsx", columns=["ingredient", "ingredient_1"],
#                                         max_results=100000, from_date="1990/01/01", to_date="2021/07/07", mesh=True, case_report=True)
# abstracts, drugs, queries = get_abstracts_pubmed.main(email="???",drugs=["aspirin", "acetaminophen"] ,druglist_path="Drug_mapping_v2.xlsx", columns=["ingredient", "ingredient_1"],
#                                                       max_results=100000, from_date="1990/01/01", to_date="2021/07/07", mesh=True, case_report=True)


# Using suicidal terms as drugs, no meSH. suicide_terms = meshs + tws (at get_abstracts_pubmed.py)
suicide_terms = ["Suicidal Ideation", "Suicide, Attempted", "Suicide, Completed", "Suicide","suicid", "suicidal", "suicidality", "suicidally", "suicidals", "suicide", "suicides", "suicide s", "suicided", "suiciders"]
abstracts, drugs, queries = get_abstracts_pubmed.main(email="smb1103@gmail.com",drugs=suicide_terms ,columns="",
                                                      max_results=100000, from_date="1990/01/01", to_date="2021/07/26", mesh=False, case_report=True)
output_file = "data/abstracts_only_suicidal.xlsx"

# Using only ingredients, no meSH
# columns = ['ingredient_1', 'ingredient_2', 'ingredient_3', 'ingredient_4', 'ingredient_5', 'ingredient_6', 'ingredient_7', 'ingredient_8', 'ingredient_9']
# abstracts, drugs, queries = get_abstracts_pubmed.main(email="smb1103@gmail.com", druglist_path="drug_mapping_v3_210726_2.xlsx", columns=columns,
#                                         max_results=100000, from_date="1990/01/01", to_date="2021/07/26", mesh=False, case_report=True)
# output_file = "data/abstracts_only_ingredients.xlsx"


# Using ingredients, use sucidal terms as meSH
# abstracts, drugs, queries = get_abstracts_pubmed.main(email="smb1103@gmail.com", druglist_path="drug_mapping_v3_210726_2.xlsx", columns=columns,
#                                         max_results=100000, from_date="1990/01/01", to_date="2021/07/26", mesh=True, case_report=True)
# output_file = "data/abstracts_ingredients_and_sucidal.xlsx"


# output_file="PubMed_crawl_sui_casereports_" +date.today().strftime("%Y/%m/%d") + "_1.xlsx"
# output_file = "data/temp.xlsx"
df=pd.DataFrame(abstracts)

if not df.empty:

    df['drugs']=df['drugs'].map(lambda x: ',\n'.join(x))
    df['PMID'] = df['PMIDa'].map(lambda x: ',\n'.join(x))

    df.drop(["PMIDa", "PMIDlist"], axis=1, inplace=True)
    writer=pd.ExcelWriter(output_file, engine='openpyxl')
    print(f"Length: {len(df)}")
    df.to_excel(writer, sheet_name="result", index=False)

    dfdrugs = pd.DataFrame({'Drugs': drugs})
    dfdrugs.to_excel(writer, sheet_name="drugs", index=False)

    dfq = pd.DataFrame({'Queries': queries})
    dfq.to_excel(writer, sheet_name="queries", index=False)

    writer.save()

else:
     print("Empty")
