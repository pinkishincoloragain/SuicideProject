# def get_DOI_crossref(title):
#     import requests
#     url = 'https://api.crossref.org/works?query.bibliographic=' + title + '&sort=relevance'
#     r = requests.get(url)
#     if r.status_code == 200 and r.json()["message"]["items"]:
#
#         # print(r.json()["message"]["items"][0]["title"][0])
#         return r.json()["message"]["items"][0].get("DOI")
#
# def get_API_SS(doi, fields):
#     import requests
#     # print(doi)
#     SS_dict = {}
#     semantics_r = requests.get('https://api.semanticscholar.org/v1/paper/' + doi)
#     if semantics_r.status_code == 200:
#         semantics = semantics_r.json()
#         if "error" not in semantics.keys():
#             SS_dict.update(({k: v for k, v in semantics.items() if k in fields}))
#             if "topics" in SS_dict.keys():
#                 if len(SS_dict["topics"]) > 0:
#                     SS_dict["topics"] = [_.get('topic') for _ in
#                                          SS_dict["topics"]]  # the topics value contains few fields, parsing
#                 else:
#                     del SS_dict["topics"]
#         else:
#             SS_dict.update({"_semanticscholar": False})
#     return SS_dict


def make_query(**kwargs):
    from itertools import product

    suicide_meshs = ["Suicidal Ideation", "Suicide, Attempted", "Suicide, Completed", "Suicide"]
    suicide_tws = ["suicid",  "suicidal",  "suicidality",  "suicidally",  "suicidals",  "suicide",  "suicides",  "suicide s",  "suicided",  "suiciders"]
    # meshids=["D059020","D013406","D000081013"]
    # suicide_tags=["Mesh", "TW"]
    drug_tags=["Mesh", "Supplementary concept", "TW"]
    # languages=["English"]
    filters=[]

    if kwargs.get("drugs"):
        filters.append("(" + " OR ".join([drug + f"[{tag}]" for drug,tag in product(kwargs.get("drugs"), drug_tags)]) + ")")

    if kwargs.get('suicide_mesh') != kwargs.get('suicide_tw'): #if one presents
        if kwargs.get('suicide_mesh'):
            filters.append("(" + " OR ".join([mesh + f"[{tag}]" for mesh, tag in product(suicide_meshs, ["Mesh"])]) + ")")
        if kwargs.get('suicide_tw'):
            filters.append("(" + " OR ".join([tw + f"[{tag}]" for tw, tag in product(suicide_tws, ["TW"])]) + ")")
    elif kwargs.get('suicide_mesh') and kwargs.get('suicide_tw'): #two present
            filters.append("("+
                "(" + " OR ".join([mesh + f"[{tag}]" for mesh, tag in product(suicide_meshs, ["Mesh"])]) + ")"
                           +" OR "
                           + "(" + " OR ".join([tw + f"[{tag}]" for tw, tag in product(suicide_tws, ["TW"])]) + ")"
                           +")"
                           )

    if kwargs.get("from_date"): #start time is required by PubMed
        filters.append(f"({kwargs.get('from_date')}[Date - Publication] : {kwargs.get('to_date') if kwargs.get('to_date') else str(3000)}[Date - Publication])")

    if kwargs.get('case_report'):
        filters.append("(" + "case reports" + "[Filter]" + ")") #[Title/Abstract]

    if kwargs.get('lang'):
        filters.append(
            "(" + " OR ".join([l + f"[{tag}]" for l, tag in product(kwargs.get('lang'), ["Language"])]) + ")")

    return " AND ".join(filters)

def post_processing(results, drugs, papers):
    from tqdm import tqdm
    """
    Post-processing
    """
    # for article in tqdm(results):
    for article in results:
        abstract = article.abstract
        # if abstract and any(drug in abstract for drug in drugs):
        if abstract:
            drugsfound=[]
            for drug in drugs:
                if drug in abstract:
                    drugsfound.append(drug)
            if len(drugsfound) or (len(drugsfound)==0 and len(drugs)==0):
                data={"abstract":abstract,  "drugs":drugsfound, "title":article.title[0] if isinstance(article.title, list) else article.title, "DOI": article.doi, "date": article.publication_date, "PMIDa":article.pubmed_id.splitlines(),"PMIDlist":article.pubmed_id}
                if data not in papers:
                    papers.append(data)
    return papers

def pymed(args):
    """
    :type mesh: bool
    :type case_report: bool
    """

    from pymed import PubMed
    from requests.exceptions import HTTPError
    from itertools import chain
    CHL=30 #

    pubmed = PubMed(tool="MyTool", email=args.get('email'))

    drugs = args.get('drugs')
    papers = []
    results=[]
    queries=[]
    try:
        query=make_query(**args)
        # print(query)
        results = pubmed.query(query, max_results=args.get('max_results'))
        post_processing(results, drugs, papers)
        queries.append(query)
    except HTTPError as e:
        print("request is too long, chunking...")
        chunks=[drugs[x:x+CHL] for x in range(0, len(drugs), CHL)]
        for _ in chunks:
            args['drugs']=_
            query=make_query(**args)
            # print(query)
            subres = pubmed.query(query, max_results=args.get('max_results'))
            results=chain(results,subres)
            queries.append(query)

    post_processing(results, drugs, papers)


    print(f"Total abstracts:{len(papers)}")
    return papers, drugs, queries

def main(**kwargs):

    import get_drugs

    print(
        f"Using drug list({kwargs.get('druglist_path') if kwargs.get('druglist_path') else 'input'}), crawling max {kwargs.get('max_results')}  abstracts for {kwargs.get('email')}. "
        f"Corresponding articles were published from {kwargs.get('from_date')} to {kwargs.get('to_date')} ")

    print(f"using MeSH" if kwargs.get('mesh') else 'no MeSH:')

    print(f"case report filtering:" if kwargs.get('case_report') else 'no filtering:')




    if not isinstance(kwargs.get('drugs') , list):
        drugs = []
        if kwargs.get('druglist_path'):
            if kwargs.get('druglist_path').endswith('.xlsx') or kwargs.get('druglist_path').endswith('.xls'):
                drugs=get_drugs.from_excel(path=kwargs.get('druglist_path'), columns=kwargs.get('columns'))
            elif kwargs.get('druglist_path').endswith('.csv'):
                drugs=get_drugs.from_csv(path=kwargs.get('druglist_path'))
        kwargs["drugs"]=drugs

    papers,drugs, queries= pymed(kwargs)

    # for _ in papers:
    #     doi=_.get("DOI")
    #     if doi is not None:
    #         SSdata=get_API_SS(doi,["abstract"])
    #         _.update({'SS_abstract':SSdata.get("abstract"), 'SS_topic':SSdata.get("topic")})
    #     else:
    #         doi=get_DOI_crossref(_.get("title"))
    #         _.update({'DOI': doi,
    #                   "crossref_doi":1}) #debug

    print("OK")

    return papers, drugs, queries

if __name__ == "__main__":
    import argparse

    """Command Prompt"""

    parser = argparse.ArgumentParser()

    parser.add_argument('--email', help='User email', default='???')
    parser.add_argument('--druglist_path', help='Path for a CSV with drug list', default="suicideSE_drugs.csv")
    parser.add_argument('--max_results', help='Maximum results for the query',default=10000)
    parser.add_argument("--from_date", help="The date (YYYY/MM/DD) after which the publication was published", default="2010/01/01")
    parser.add_argument("--to_date", help="The date (YYYY/MM/DD) before which the publication was published",default="2021/05/23")

    parser.add_argument("--mesh", dest="suicide_mesh", action="store_true",help="Using suicidal MeSHs(bool)")
    parser.add_argument("--no_mesh", dest="suicide_mesh", action="store_false", help="NOT using suicidal MeSHs(bool)")
    parser.set_defaults(suicide_mesh=True)

    parser.add_argument("--sui", dest="suicide_tw", action="store_true", help="Using suicidal text words(bool)")
    parser.add_argument("--no_sui", dest="suicide_tw", action="store_false", help="NOT using suicidal text words(bool)")
    parser.set_defaults(suicide_tw=True)

    parser.add_argument("--case_report", dest="case_report", action="store_true", help="Using case report filtering")
    parser.add_argument("--no_case_report", dest="case_report", action="store_false", help="NOT using case report filtering")
    parser.set_defaults(case_report=False)

    parser.add_argument("--drugs", type= list , help="Array of drug names", default=[])
    parser.add_argument('--lang', help='Language filter', default=["English"])

    args = parser.parse_args()

    #TODO

    # main(args)

