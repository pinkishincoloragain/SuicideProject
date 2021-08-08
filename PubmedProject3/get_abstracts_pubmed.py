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

class PyMedCrawler:

    def __init__(self, **kwargs):
        import pandas as pd
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.queries=[]
        if hasattr(self, 'restore') : #TODO if none
            import json
            from tqdm import tqdm
            print(f"Restoring from excel {self.restore}")
            self.papers=pd.read_excel(self.restore, sheet_name="result", index_col=None).to_dict('records')
            for _ in tqdm(self.papers):
                _.update({"drugs": json.loads(_.get("drugs").replace("\'", "\""))})
                _.update({"PMIDa":_.get("PMID").split(",")})
                for attr in ["meshs", "filters"]:
                    if hasattr(_, attr):
                        del _[attr]
            self.queries=pd.read_excel(self.restore, sheet_name="queries", index_col=None).to_dict('records')
        else:
            self.papers=[]
            self.results=[]
            print(
            f"Using drug list {self.druglist_path if hasattr(self, 'druglist_path') else 'input'}, crawling max {self.max_results}  abstracts for {self.email}. "
            f"Corresponding articles were published from {self.from_date if hasattr(self, 'from_date') else str(float('-inf'))} to {self.to_date if hasattr(self, 'to_date') else str(float('inf'))} ")
            if hasattr(self, "sui_mesh"):
                print(f"using suicide MeSH")
            if hasattr(self,"case_report"):
                print(f"case report filtering")
        self.set_drugs()
        self.n_drugs = len(self.drugs)

    def utils(self, config="sentence_number", entity="sentences", key=None):

        if config=="sentence_number":
            return len(list(set([_.get("ID") for _ in [item for sublist in [ss.get('sentences') for ss in self.papers] for item in sublist]])))

        if config=="delete_items" and key:
            print(f"Dropping {key} items from {entity}...")
            for paper in self.papers:
                if entity=="papers":
                    del paper[key]
                if entity=="sentences":
                    for s in paper.get(entity):
                        del s[key]

        if config=="wrong_parsing":
            import re
            aaa=[sublist.get('sentences') for sublist in self.papers]
            return [item.get('sent') for sublist in aaa for item in sublist if re.findall(r'[!?.][A-Z]', item.get('sent')) and (item.get('drugs') if entity=="drugs" else True)]

    def set_drugs(self):
        import get_drugs
        if not hasattr(self,'drugs'):
            # if not isinstance(self.drugs, list):
            drugs = []
            if self.druglist_path:
                if self.druglist_path.endswith('.xlsx') or self.druglist_path.endswith('.xls'):
                    drugs = get_drugs.from_excel(path=self.druglist_path, columns=self.columns)
                elif self.druglist_path.endswith('.csv'):
                    drugs = get_drugs.from_csv(path=self.druglist_path)
        else:
            drugs=self.drugs
        self.drugs = list(set(drugs))

    def make_query(self, drug=None, check_tags=None, tags=None):
        from itertools import product

        suicide_meshs = ["Suicidal Ideation", "Suicide, Attempted", "Suicide, Completed", "Suicide"]
        suicide_tws = ["suicid", "suicidal", "suicidality", "suicidally", "suicidals", "suicide", "suicides",
                       "suicide s", "suicided", "suiciders"]
        drug_tags = ["Mesh", "Supplementary concept", "TW"]

        mesh_tags = ["MeSH Subheading", "MeSH"]
        filter_tags=["Filter"]

        filters = []

        if drug:
            filters.append(
                "(" + " OR ".join([drug + f"[{tag}]" for tag in drug_tags]) + ")")

        # if self.drugs:
        #     filters.append(
        #         "(" + " OR ".join([drug + f"[{tag}]" for drug, tag in product(kwargs.get("drugs"), drug_tags)]) + ")")

        # if hasattr(self,'suicide_mesh')
        if self.suicide_mesh != self.suicide_tw:  # if one presents
            if self.suicide_mesh:
                filters.append(
                    "(" + " OR ".join([mesh + f"[{tag}]" for mesh, tag in product(suicide_meshs, ["Mesh"])]) + ")")
            if self.suicide_tw:
                filters.append("(" + " OR ".join([tw + f"[{tag}]" for tw, tag in product(suicide_tws, ["TW"])]) + ")")
        elif self.suicide_mesh and self.suicide_tw:  # two present
            filters.append("(" +
                           "(" + " OR ".join(
                [mesh + f"[{tag}]" for mesh, tag in product(suicide_meshs, ["Mesh"])]) + ")"
                           + " OR "
                           + "(" + " OR ".join([tw + f"[{tag}]" for tw, tag in product(suicide_tws, ["TW"])]) + ")"
                           + ")"
                           )

        if hasattr(self,'from_date'):
            if self.from_date:# start time is required by PubMed
                filters.append(
                    f"({self.from_date}[Date - Publication] : {self.to_date if hasattr(self,'to_date') else str(3000)}[Date - Publication])")

        if hasattr(self,'case_report'):
            if self.case_report:
                filters.append("(" + "case reports" + "[Filter]" + ")")  # [Title/Abstract]

        if hasattr(self,'lang'):
            if self.lang:
                filters.append(
                    "(" + " OR ".join([l + f"[{tag}]" for l, tag in product(self.lang, ["Language"])]) + ")")

        if check_tags:
            if check_tags=="mesh":
                filters.append(
                    "(" + " OR ".join([m + f"[{tag}]" for m, tag in product(tags, mesh_tags)]) + ")"
                )
            if check_tags == "filter":
                filters.append(
                    "(" + " OR ".join([m + f"[{tag}]" for m, tag in product(tags, filter_tags)]) + ")"
                )


        return " AND ".join(filters)

    def execute_query(self,Q, drug=None):
        from pymed import PubMed
        from requests import exceptions as reqexc
        max_retries=10

        pubmed = PubMed(tool="KNU_DSA_PubMed_"+str(drug) if drug else "", email=self.email)

        for _ in range(max_retries):
            try:
                response = pubmed.query(Q, max_results=self.max_results) #TODO retry
                break
            except (TimeoutError, reqexc.ConnectionError, reqexc.ConnectionTimeout) as e:
                pass

        if response: #response OK
            if drug:
                result = [{"obj": item, "drug": drug} for item in response]
            else:
                result = [item for item in response]
        else:
            import warnings
            warnings.warn(f"Connection failed for {drug if drug else  '_'} after {max_retries} retries")
            if drug:
                result = [{"obj": [], "drug": drug}]
            else:
                result = []

        return result

    def post_processing(self): #GROUP BY imitation with PMIDlist key to get an array of drug for each paper
        from tqdm import tqdm
        """
        Post-processing
        """
        keys = ["PMIDlist"]
        papers = []
        print("Postprocessing...")
        for article in tqdm(self.results):
            obj = article.get("obj")
            if obj.abstract:
                data = {"abstract": obj.abstract, "drugs": [article.get("drug")],
                        "title": obj.title[0] if isinstance(obj.title, list) else obj.title, "DOI": obj.doi,
                        "date": obj.publication_date, "PMIDa": obj.pubmed_id.splitlines(),
                        "PMIDlist": obj.pubmed_id}

            iii = [i for i, x in enumerate(papers) if x["PMIDlist"] == data.get("PMIDlist")]  # if there are duplicate PMIDs
            if iii: #YES, update
                duplicatesdrug = data.get("drugs")
                for d in iii:
                    if papers[d].get("drugs")[0] not in duplicatesdrug:
                        duplicatesdrug.extend(papers[d].get("drugs"))
                data.update({"drugs": duplicatesdrug})
                for i in iii:
                    papers[i] = data
            else: #NO, append
                papers.append(data)
        self.papers.extend(papers)

    def harvest(self):
        from multiprocessing import Pool, freeze_support
        if __name__ == '__main__':
            freeze_support()
        import tqdm
        drugs = self.drugs

        # import os
        # n_cpu = os.cpu_count()
        # n_drugs=self.n_drugs
        # with Pool(processes=min(n_drugs,n_cpu)) as p:
        #     for res, req in tqdm.tqdm(p.imap_unordered(self.execute_query, drugs), total=n_drugs,
        #                               colour='white'):  # TODO multiprocessing lib initializes duplicated task which leads to Error 429 : to many requests
        #         self.queries.append(req)
        #         if res:
        #             # print(_)
        #             self.results.extend(res)
        #             pass

        for drug in tqdm.tqdm(drugs): #temporary workaround: 1 process
            query=self.make_query(drug)
            res = self.execute_query(drug=drug, Q=query)
            self.queries.append(query)
            self.results.extend(res)

    def split_to_sents(self,classify=False, keywords=False):
        print("Getting sentences...")
        from tqdm import tqdm
        import nltk.data
        sui_keywords=["suicid"]
        exc_sents=["(ABSTRACT TRUNCATED AT 250 WORDS)"]
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

        if classify:
            from transformers import pipeline
            sui_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            candidate_labels = ["suicide", "non-suicide"]

        x = 0 #cross-paper sentence counter
        for paper in tqdm(self.papers):
            ss = tokenizer.tokenize(paper['abstract']) #TODO tokenizers???
            list = []
            #TODO is "is_suicidal": " ", "ADE": " ", sui_keywords, sui_classifier for title
            for s in ss:
                if s not in exc_sents:
                    sdict={"ID": "s" + str(x), "PMID":paper["PMIDa"],"sent": s, "is_suicidal": " ", "ADE": " ",
                                 "drugs": [drug for drug in paper['drugs'] if drug in s]}
                    if keywords:
                        suiskw=[kw for kw in sui_keywords if kw in s]
                        if suiskw:
                            sdict.update({"sui_keywords":suiskw})

                    if classify:
                        k = sui_classifier(s, candidate_labels)
                        sdict.update({"sui_classifier": k.get("labels")[k.get("scores").index(max(k.get("scores")))]})
                        #TODO provide suicide probability instead of

                    list.append(sdict)
                x += 1
            paper.update({"sentences": list})

    def check_tags(self, type="mesh", list=None):
        from tqdm import tqdm
        """type: mesh or filter
        list: list of instances"""
        if type in ["mesh", "filter"] and list:
            print(f"Checking {','.join(list)} {type}s:") #

            for _ in list:
                query=self.make_query(check_tags=type,tags=list)
                res=self.execute_query(Q=query)
                PMIDA = [_.pubmed_id.splitlines() for _ in res]
                PMIDA = [item for sublist in PMIDA for item in sublist] #papers with those PMIDs has the mesh/filter
                for paper in tqdm(self.papers):
                    if set(paper.get("PMIDa")).intersection(PMIDA):
                        paper.update({
                            type+"s":list(set(paper.get(type+"s").append(_))) if hasattr(paper,type+"s")
                                      else [_]})

def main(**kwargs):
    crawlerObj = PyMedCrawler(**kwargs)

    crawlerObj.harvest()
    crawlerObj.post_processing()
    # crawlerObj.check_tags(type="filter", list=["case reports"])
    # crawlerObj.check_tags(type="mesh", list=["adverse effects"])
    # crawlerObj.split_to_sents(keywords=True, classify=False) #classifying takes some time

    print(crawlerObj.utils(config="sentence_number"))


    return crawlerObj.papers, crawlerObj.drugs, crawlerObj.queries

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


    main(args)
