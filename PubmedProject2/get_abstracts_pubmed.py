def make_query(**kwargs):
    from itertools import product

    suicide_meshs = ["Suicidal Ideation", "Suicide, Attempted", "Suicide, Completed", "Suicide"]
    # meshids=["D059020","D013406","D000081013"]
    suicide_tags=["Mesh", "TW"]

    drug_tags=["Mesh", "Supplementary concept", "TW"]

    query = ""
    if kwargs.get("drugs"):
        query = "(" + " OR ".join([drug + f"[{tag}]" for drug,tag in product(kwargs.get("drugs"), drug_tags)]) + ")" \
                + " AND "
    query = query + f"({kwargs.get('from_date')}[Date - Publication] : {kwargs.get('to_date')}[Date - Publication])"

    if kwargs.get('mesh'):
        query = query + " AND "\
        + "(" + " OR ".join([_ + f"[{tag}]" for _, tag in product(suicide_meshs, suicide_tags)]) + ")"
    if kwargs.get('case_report'):
        query = query + " AND " \
                + "(" + "case reports" + "[Filter]" + ")"
    return query

def post_processing(results, drugs, papers):
    from tqdm import tqdm
    """
    Post-processing
    """
    for article in tqdm(results):
        abstract = article.abstract
        # if abstract and any(drug in abstract for drug in drugs):
        if abstract:
            drugsfound=[]
            for drug in drugs:
                if drug in abstract:
                    drugsfound.append(drug)
                # print(abstract)
                # print("\n")
            if len(drugsfound):
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
        query=make_query(drugs=drugs,from_date=args.get('from_date'),to_date=args.get('to_date'),
                         mesh=args.get('mesh') , case_report=args.get('case_report'))
        print(query)
        results = pubmed.query(query, max_results=args.get('max_results'))
        papers=post_processing(results, drugs, papers)
        queries.append(query)
    except HTTPError as e:
        print("request is too long, chunking...")
        chunks=[drugs[x:x+CHL] for x in range(0, len(drugs), CHL)]
        #print(chunks)
        for _ in chunks:
            args['drugs']=_
            query=make_query(drugs=_,from_date=args.get('from_date'),to_date=args.get('to_date'),
                         mesh=args.get('mesh') , case_report=args.get('case_report'))
            print(query)
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

    abstracts = pymed(kwargs)

    return abstracts

if __name__ == "__main__":
    import argparse

    """Command Prompt"""

    parser = argparse.ArgumentParser()

    parser.add_argument('--email', help='User email', default='???')
    parser.add_argument('--druglist_path', help='Path for a CSV with drug list', default="suicideSE_drugs.csv")
    parser.add_argument('--max_results', help='Maximum results for the query',default=10000)
    parser.add_argument("--from_date", help="The date (YYYY/MM/DD) after which the publication was published", default="2010/01/01")
    parser.add_argument("--to_date", help="The date (YYYY/MM/DD) before which the publication was published",default="2021/05/23")

    parser.add_argument("--mesh", dest="mesh", action="store_true",help="Using suicidal MeSHs(bool)")
    parser.add_argument("--no_mesh", dest="mesh", action="store_false", help="NOT using suicidal MeSHs(bool)")
    parser.set_defaults(mesh=True)

    parser.add_argument("--case_report", dest="case_report", action="store_true", help="Using case report filtering")
    parser.add_argument("--no_case_report", dest="case_report", action="store_false", help="NOT using case report filtering")
    parser.set_defaults(case_report=False)

    parser.add_argument("--drugs", type= list , help="Array of drug names", default=[])


    args = parser.parse_args()

    #TODO
    # main(args)
