def pymed(email, drugs, n, from_date, to_date):
    from pymed import PubMed
    from tqdm import tqdm

    pubmed = PubMed(tool="MyTool", email=email)
    # query = "baclofen[Abstract]"
    query= "(" + " OR ".join([_+"[Abstract]" for _ in drugs] ) + ")" +" AND " + f"({from_date}[Date - Publication] : {to_date}[Date - Publication])"
    print(query)
    results = pubmed.query(query, max_results=n)

    abstracts=[]

    for article in tqdm(results):
        abstract=article.abstract
        if abstract and any(drug in abstract for drug in drugs):
            # print(abstract)
            # print("\n")
            abstracts.append(abstract)

    print(f"Total abstracts:{len(abstracts)}")
    return abstracts

def main(email,druglistpath,max_results, from_date, to_date):
    import csv
    print(f"Using drug list({druglistpath}), crawling max {max_results}  abstracts for {email}. Corresponding articles were published from {from_date} to {to_date}:")

    drugs = []
    with open(druglistpath, newline='') as inputfile:
        for row in csv.reader(inputfile):
            drugs.append(row[0])

    abstracts = pymed(email,drugs,max_results, from_date, to_date)

    return abstracts

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--email', help='User email')
    parser.add_argument('--druglist_path', help='Path for a CSV with drug list')
    parser.add_argument('--max_results', help='Maximum results for the query')
    parser.add_argument("--from_date", help="The date (YYYY/MM/DD) after which the publication was published")
    parser.add_argument("--to_date", help="The date (YYYY/MM/DD) before which the publication was published")



    args = parser.parse_args()

    main(args.email,args.druglist_path,int(args.max_results), args.from_date, args.to_date)
