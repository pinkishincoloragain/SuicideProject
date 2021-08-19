def pymed(email, drugs, n):
    from pymed import PubMed
    # from tqdm import tqdm

    pubmed = PubMed(tool="MyTool", email=email)
    # query = "baclofen OR retinoic acid[Abstract]"
    query=" OR ".join([_+"[Abstract]" for _ in drugs])
    results = pubmed.query(query, max_results=n)

    abstracts=[]

    # for article in tqdm(results):
    for article in results:
        abstract=article.abstract
        if abstract and any(drug in abstract for drug in drugs):
            # print(abstract)
            # print("\n")
            abstracts.append(abstract)

    print(f"Total abstracts:{len(abstracts)}")
    return abstracts

def main(email,druglistpath,max_results):
    import csv
    print(f"Using druglist({druglistpath}), crawling max {max_results} abstracts for {email}:")

    drugs = []
    with open(druglistpath, newline='') as inputfile:
        for row in csv.reader(inputfile):
            drugs.append(row[0])

    abstracts = pymed(email,drugs,max_results)
    print(abstracts)
    return abstracts

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--email', help='User email')
    parser.add_argument('--druglist_path', help='Path for a CSV with druglist')
    parser.add_argument('--max_results', help='Maximum results for the query')
    args = parser.parse_args()

    main(args.email,args.druglist_path,int(args.max_results))
