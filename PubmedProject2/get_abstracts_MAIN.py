import get_abstracts_pubmed
import pandas as pd
# abstracts, drugs, queries = get_abstracts_pubmed.main(email="???", druglist_path="../../data/Drug_mapping_v2.xlsx", columns=["ingredient", "ingredient_1"],
#                                         max_results=100000, from_date="1990/01/01", to_date="2021/06/30", mesh=True, case_report=True)
abstracts, drugs, queries = get_abstracts_pubmed.main(email="smb1103@gmail.com", druglist_path="Drug_mapping_v2.csv", columns=["ingredient", "ingredient_1"],
                                        max_results=100000, from_date="1990/01/01", to_date="2021/06/30", mesh=True, case_report=True)

output_file="PubMed_crawl_sui_casereports_210630.xlsx"
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