import pandas as pd
from pymed import PubMed

suicide_df = pd.DataFrame(columns=['abstract','title','date'])

pubmed = PubMed(tool="MyTool", email="my@email.address")

query = "(zoster[Mesh] OR zoster[Supplementary concept] OR zoster[TW] OR zoster virus[Mesh] \
OR zoster virus[Supplementary concept] OR zoster virus[TW] OR) AND (1990/01/01[Date - Publication] : 2021/07/26[Date - Publication])\
AND (case reports[Filter]) AND (English[Language])"

results = pubmed.query(query, max_results=1000000)

cnt = 0
cnt2 = 0
cnt3 = 0

abstract_list = []
title_list = []
date_list = []

for article in results:
    cnt += 1
    if article.abstract is not None:
        cnt2 += 1
        if ('zoster' or 'zoster virus') in article.abstract:
            abstract_list.append(article.abstract)
            title_list.append(article.title)
            date_list.append(article.publication_date)
            cnt3 += 1

print(cnt, cnt2, cnt3)

suicide_df['abstract'] = abstract_list
suicide_df['title'] = title_list
suicide_df['date'] = date_list

