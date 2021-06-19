def pymed(args):
    """
    :type mesh: bool
    :type case_report: bool
    """

    from pymed import PubMed
    from tqdm import tqdm

    meshs = ["Suicidal Ideation", "Suicide, Attempted", "Suicide, Completed"]
    # meshids=["D059020","D013406","D000081013"]

    pubmed = PubMed(tool="MyTool", email=args.get('email'))
    # query = "baclofen[Abstract]"
    # query = " Suicide/drug effects[Mesh]"
    # query =" OR ".join([_+"[Mesh]" for _ in meshs] )
    query = "(" + " OR ".join([_ + "[Abstract]" for _ in args.get('drugs')]) + ")" \
            + " AND " \
            + f"({args.get('from_date')}[Date - Publication] : {args.get('to_date')}[Date - Publication])"

    if args.get('mesh'):
        query = query + " AND " \
                     + "(" + " OR ".join([_ + "[Mesh]" for _ in meshs]) + ")"
    if args.get('case_report'):
        query = query + " AND " \
                     + "(" +"case reports"+ "[Filter]" + ")"


    print(query)
    results = pubmed.query(query, max_results=args.get('max_results'))

    papers = []

    """
    Post-processing
    """
    for article in tqdm(results):
        abstract = article.abstract
        # if abstract and any(drug in abstract for drug in drugs):
        if abstract:
            drugsfound=[]
            for drug in args.get('drugs'):
                if drug in abstract:
                    drugsfound.append(drug)
                # print(abstract)
                # print("\n")
            if len(drugsfound):
                papers.append({"abstract":abstract,  "drugs":drugsfound, "title":article.title, "DOI": article.doi, "date": article.publication_date, "PMIDa":article.pubmed_id.splitlines(),"PMIDlist":article.pubmed_id})

    print(f"Total abstracts:{len(papers)}")
    return papers

def main(**kwargs):

    import csv
    print(
        f"Using drug list({kwargs.get('druglist_path') if kwargs.get('druglist_path') else 'input'}), crawling max {kwargs.get('max_results')}  abstracts for {kwargs.get('email')}. "
        f"Corresponding articles were published from {kwargs.get('from_date')} to {kwargs.get('to_date')} ")

    print(f"using MeSH" if kwargs.get('mesh') else 'no MeSH:')

    print(f"case report filtering:" if kwargs.get('case_report') else 'no filtering:')


    if not isinstance(kwargs.get('drugs') , list):
        drugs = []
        with open(kwargs.get('druglist_path'), newline='') as inputfile:
            for row in csv.reader(inputfile):
                drugs.append(row[0])
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

    parser.add_argument("--drugs", type= list , help="Array of drug names")


    args = parser.parse_args()

    #TODO
    # main(args)
