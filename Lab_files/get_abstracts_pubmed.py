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
#         else:`
#             SS_dict.update({"_semanticscholar": False})
#     return SS_dict

class PyMedCrawler:

    def __init__(self, **kwargs):
        import pandas as pd

        # Sampling for test
        self.source = ["pubmed", "twitter"]
        # self.source = ["twitter"]

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.queries=[]
        if hasattr(self, 'restore') : #TODO if none
            import json
            from tqdm import tqdm
            print(f"Restoring from excel {self.restore}")
            self.papers=pd.read_excel(self.restore, sheet_name="result", index_col=None).to_dict('records')
            for _ in tqdm(self.papers, desc="Papers"):
                _.update({"drugs": json.loads(_.get("drugs").replace("\'", "\""))})
                _.update({"PMIDa":_.get("PMID").split(",")})
                for attr in ["meshs", "filters"]:
                    if hasattr(_, attr):
                        del _[attr]
            self.queries=pd.read_excel(self.restore, sheet_name="queries", index_col=None).to_dict('records')
        else:
            self.papers=[]
            self.tweets = []
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

        # TODO put brands in self.brand_names
        self.brand_names = ["aspirin"]

        # attributes for twitter crawling
        self.bearer_token = "AAAAAAAAAAAAAAAAAAAAAMjyOwEAAAAAYm8zDZ9NMtvCd4K%2FTckEVsozHCA%3Daj3fsQ8Pgmka7tfdzLkeTFcY8jtvZW0hhDps7UFVnsiU1aJhnv"
        self.search_url = "https://api.twitter.com/2/tweets/search/all"
        self.query_params = {'query': '', 'tweet.fields': 'created_at,lang,author_id',
                             'start_time': '2016-01-01T00:00:00Z',
                             'end_time': '2021-01-01T00:00:00Z', 'max_results': '500'}


    def utils(self, config="sentence_number", entities=None, drugs=None):
        if entities:
            if isinstance(entities,dict):
                if "papers" in entities.keys():
                    if isinstance(entities.get("papers"), list):p_attrs = entities.get("papers")
                    else:p_attrs = [entities.get("papers")]
                if "sentences" in entities.keys():
                    if isinstance(entities.get("sentences"), list):s_attrs = entities.get("sentences")
                    else:s_attrs = [entities.get("sentences")]

        if config == "drug_pivot":
            """pymed results pivot by drug"""
            from collections import Counter
            if drugs:   l=Counter(tok['drug'] for tok in self.results if tok['drug'] in drugs)
            else:   l=Counter(tok['drug'] for tok in self.results)
            return l

        if config=="abstract_number":
            if entities:
                return [ss.get('abstract') for ss in self.papers if ss.get('abstract') and ss.get(entities)]
            else:
                return [ss.get('abstract') for ss in self.papers if ss.get('abstract')]

        if config=="title_number":
            if drugs:
                return [ss.get('title') for ss in self.papers
                            if ss.get('title')
                            and any(drug in ss.get('title') for drug in self.drugs)
                            ]
            else:
                return [ss.get('title') for ss in self.papers if ss.get('title') ]


        if config=="sentence_number":
            if drugs:
                return list(set([_.get("ID") for _ in
                                     [item for sublist in [ss.get('sentences') for ss in self.papers] for item in
                                      sublist] if _.get("drugs")]))
                # if isinstance(drugs,list): return len(list(set([_.get("ID") for _ in [item for sublist in [ss.get('sentences') for ss in self.papers] for item in sublist] if _.get("drugs") in drugs])))
                # else: return len(list(set([_.get("ID") for _ in [item for sublist in [ss.get('sentences') for ss in self.papers] for item in sublist] if _.get("drugs")])))
            else:
                return list(set([_.get("ID") for _ in [item for sublist in [ss.get('sentences') for ss in self.papers] for item in sublist] ]))

        if config=="delete_items":
            """ entities={"papers":[], "sentences":[]} """
            i=0
            for k in entities.keys():
                print(f"\nDropping {','.join(entities.get(k))} items from {k}...")
            for paper in self.papers:
                i=i+1
                if i%100==0: print(i, end=',')

                if "papers" in entities.keys():
                    for pattr in p_attrs:
                        paper.pop(pattr,None)
                        # delattr(paper, pattr)

                if "sentences" in entities.keys():
                    for sattr in s_attrs:
                        for s in paper.get("sentences"):
                            s.pop(sattr,None)
            print("\nDeletion completed")

        if config=="wrong_parsing":
            import re
            aa=[sublist.get('sentences') for sublist in self.papers]
            aaa= [item for sublist in aa for item in sublist if re.findall(r'[!?.][A-Z]', item.get('sent'))]
            if drugs:
                return [_ for _ in aaa if _.get('drugs')]
            else: return aaa

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
        q = ""
        if "pubmed" in self.source:
            from itertools import product

            suicide_meshs = ["Suicidal Ideation", "Suicide, Attempted", "Suicide, Completed", "Suicide"]
            suicide_tws = ["suicid", "suicidal", "suicidality", "suicidally", "suicidals", "suicide", "suicides",
                           "suicide s", "suicided", "suiciders"]
            drug_tags = ["Mesh",  "Supplementary concept", "TW"]

            mesh_tags = ["MeSH Subheading", "MeSH"]
            filter_tags = ["Filter"]

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
                    filters.append(
                        "(" + " OR ".join([tw + f"[{tag}]" for tw, tag in product(suicide_tws, ["TW"])]) + ")")
            elif self.suicide_mesh and self.suicide_tw:  # two present
                filters.append("(" +
                               "(" + " OR ".join(
                    [mesh + f"[{tag}]" for mesh, tag in product(suicide_meshs, ["Mesh"])]) + ")"
                               + " OR "
                               + "(" + " OR ".join([tw + f"[{tag}]" for tw, tag in product(suicide_tws, ["TW"])]) + ")"
                               + ")"
                               )

            if hasattr(self, 'from_date'):
                if self.from_date:  # start time is required by PubMed
                    filters.append(
                        f"({self.from_date}[Date - Publication] : {self.to_date if hasattr(self, 'to_date') else str(3000)}[Date - Publication])")

            if hasattr(self, 'case_report'):
                if self.case_report:
                    filters.append("(" + "case reports" + "[Filter]" + ")")  # [Title/Abstract]

            if hasattr(self, 'lang'):
                if self.lang:
                    filters.append(
                        "(" + " OR ".join([l + f"[{tag}]" for l, tag in product(self.lang, ["Language"])]) + ")")

            if check_tags:
                if check_tags == "mesh":
                    filters.append(
                        "(" + " OR ".join([m + f"[{tag}]" for m, tag in product(tags, mesh_tags)]) + ")"
                    )
                if check_tags == "filter":
                    filters.append(
                        "(" + " OR ".join([m + f"[{tag}]" for m, tag in product(tags, filter_tags)]) + ")"
                    )
            q = " AND ".join(filters)

        return q

    def execute_query(self,Q, drug=None):
        result = []
        if "pubmed" in self.source:
            from pymed import PubMed
            from time import sleep
            max_retries=50
            import requests.exceptions

            pubmed = PubMed(tool="KNU_DSA_PubMed_"+str(drug) if drug else "", email=self.email)

            for _ in range(max_retries):
                try:
                    response = pubmed.query(Q, max_results=self.max_results)
                    break
                except (TimeoutError, TypeError, requests.exceptions.HTTPError) as e:
                    sleep(2)
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

        if "twitter" in self.source:
            # TODO time issue
            from time import sleep
            import json
            import requests
            import datetime
            headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
            data = []

            date = datetime.datetime.strptime(self.from_date,"%Y/%m/%d")
            end_date = datetime.datetime.strptime(self.to_date,"%Y/%m/%d")
            self.query_params['start_time'] = str(date)[0:10] + "T00:00:00Z"
            self.query_params['query'] = drug

            while True:
                date = date + datetime.timedelta(weeks=1)
                self.query_params['end_time'] = str(date)[0:10] + "T00:00:00Z"
                if str(date)[0:10] > str(end_date)[0:10]:
                    break

                response = requests.request("GET", self.search_url, headers=headers, params=self.query_params).json()

                try:
                    data.extend(response["data"])
                    self.query_params['next_token'] = response['meta']['next_token']
                except Exception as e:
                    self.query_params['next_token'] = "DUMMY"
                    del self.query_params['next_token']
                    # print(e)

                sleep(2)
            # TODO too big result - line
            result.extend([{"tw_obj": item, "drug": drug} for item in data])

        return result

    def tw_processing(self,data):
        import re

        if data.get("lang") != "en":
            return None

        pattern_rt = re.compile(r'@RT[\S\s]+')
        pattern_special = re.compile(r'[-=+,#/:^$.*\"※~&%ㆍ!』\\‘|\[\]`…》]')
        pattern_email = re.compile(r"\S*@\S*\s?")
        pattern_link = re.compile(r'http\S+')

        # TODO add processing
        text = data.get("text")
        text = text.lower().strip()
        text = re.sub(pattern=pattern_rt, repl='', string=text)
        text = re.sub(pattern=pattern_email, repl='', string=text)
        text = re.sub(pattern=pattern_link, repl='', string=text)
        res = re.sub(pattern=pattern_special, repl="", string=text)

        data["text"] = res

        return data

    def post_processing(self): #GROUP BY imitation with PMIDlist key to get an array of drug for each paper
        from tqdm import tqdm
        """
        Post-processing
        """
        if "pubmed" in self.source:
            keys = ["PMIDlist"]
            papers = []
            print("\nPostprocessing articles...")
            for article in tqdm(self.results, desc="Response items"):
                obj = article.get("obj")
                if obj is not None and obj.abstract:
                    data = {"abstract": obj.abstract,
                            "drugs": [article.get("drug")],
                            "title": obj.title[0] if isinstance(obj.title, list) else obj.title,
                            "DOI": obj.doi,
                            "date": obj.publication_date,
                            "PMIDa": obj.pubmed_id.splitlines()}

                iii = [i for i, x in enumerate(papers) if x["PMIDa"] == data.get("PMIDa")]  # if there are duplicate PMIDs
                if iii: #YES, update
                    duplicatesdrug = data.get("drugs")
                    for d in iii:
                        if papers[d].get("drugs")[0] not in duplicatesdrug:
                            duplicatesdrug.extend(papers[d].get("drugs"))
                    data.update({"drugs": duplicatesdrug})
                    for i in iii:
                        papers[i] = data
                # TODO detects whether the obj is tw_obj or obj - checks all articles (takes too long time)
                elif article.get("tw_obj"):
                    pass
                else: #NO, append
                    papers.append(data)
            self.papers.extend(papers)
            # for paper in self.papers:
            #     del paper["PMIDlist"]

        if "twitter" in self.source:
            keys = ["id"]
            tweets = []
            print("\nPostprocessing tweets...")
            for tweet in tqdm(self.results, desc="Response items"):
                tw_obj = tweet.get("tw_obj")
                # TODO need to check whether obj is null or not
                if tw_obj is not None and tw_obj["text"]:
                    data = {
                        "id":tw_obj["id"],
                        "lang": tw_obj["lang"],
                        "text": tw_obj["text"],
                        "author_id": tw_obj["author_id"],
                        "drugs": [tweet.get("drug")],
                        "created_at": tw_obj["created_at"]}
                    data = self.tw_processing(data)
                    if data is None:
                        continue
                    # TODO indent issue with iii
                    iii = [i for i, x in enumerate(tweets) if x["id"] == data.get("id")]  # if there are duplicate ids
                    if iii:  # YES, update
                        duplicatesdrug = data.get("drugs")
                        for d in iii:
                            if tweets[d].get("drugs")[0] not in duplicatesdrug:
                                duplicatesdrug.extend(tweets[d].get("drugs"))
                        data.update({"drugs": duplicatesdrug})
                        for i in iii:
                            tweets[i] = data
                    else:  # NO, append
                        tweets.append(data)
            self.tweets.extend(tweets)
            print(self.tweets)

    def harvest(self):
        """self.source = "pubmed" AND/OR "twitter"""

        from multiprocessing import freeze_support
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

        for drug in tqdm.tqdm(drugs, desc="Drugs"): #temporary workaround: 1 process
            query=self.make_query(drug)
            res = self.execute_query(drug=drug, Q=query)
            self.queries.append(query)
            self.results.extend(res)

    def split_to_sents(self,classify=False, keywords=False, titles=False, regex_sentsplit=False, med7=False): #wasnt tested on multiple filters/meshs
        print("\nGetting sentences...")
        from tqdm import tqdm
        import nltk.data,re
        import warnings
        warnings.filterwarnings('ignore')

        sui_keywords=["suicid"]
        exc_sents=["(ABSTRACT TRUNCATED AT 250 WORDS)"]
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

        if classify:
            from transformers import pipeline
            sui_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            candidate_labels = ["suicide", "non-suicide"]
        if med7:
            import spacy
            med7_model = spacy.load("en_core_med7_lg")

        x = 0 #cross-paper sentence counter
        for paper in tqdm(self.papers, desc="Papers"):
            ss = tokenizer.tokenize(paper['abstract']) #TODO tokenizers???
            list = []
            if titles: #TODO inapplicable for twitter
                tdict={}
                if paper.get("title"):
                    # paper.update({"is_suicidal":"", "ADE":""})
                    if keywords:
                        suickw = [kw for kw in sui_keywords if kw in paper.get("title").lower()]
                        if suickw:
                            tdict.update({"sui_keywords": suickw})
                    if classify:
                        k = sui_classifier(paper.get("title"), candidate_labels)
                        tdict.update({"sui_clasifier": k.get("scores")[k.get("labels").index("suicide")]})  # score for suicide
                            # sdict.update({"sui_classifier": k.get("labels")[k.get("scores").index(max(k.get("scores")))]}) #a label
                    if med7:
                        med7drugs=[{"text":ent.text, "start_char":ent.start_char, "end_char":ent.end_char} for ent
                                   in med7_model(paper.get("title")).ents if ent.label_=="DRUG"]
                        if med7drugs:
                            tdict.update({"med7":med7drugs})
                        del med7drugs

                    if regex_sentsplit:
                        if re.findall(r'[!?.][A-Z]', paper.get('title')):
                            tdict.update({"regex":1})

                    paper.update({"title_attr":tdict})

            for s in ss:
                if s not in exc_sents:
                    sdict={"ID": "s" + str(x), "sent": s,
                           # "is_suicidal": "", "ADE": "",
                                 "drugs": [drug for drug in paper['drugs'] if drug.lower() in s.lower()]}
                    if keywords:
                        suiskw=[kw for kw in sui_keywords if kw in s.lower()]
                        if suiskw:
                            sdict.update({"sui_keywords":suiskw})

                    if classify:
                        k = sui_classifier(s, candidate_labels)
                        sdict.update({"sui_clasifier":k.get("scores")[k.get("labels").index("suicide")]}) #score for suicide
                        # sdict.update({"sui_classifier": k.get("labels")[k.get("scores").index(max(k.get("scores")))]}) #a label

                    if med7:
                        med7drugs = [{"text": ent.text, "start_char": ent.start_char, "end_char": ent.end_char} for ent
                                     in med7_model(s).ents if ent.label_ == "DRUG"]
                        if med7drugs:
                            sdict.update({"med7": med7drugs})
                        del med7drugs

                    if regex_sentsplit:
                        if re.findall(r'[!?.][A-Z]', s):
                            sdict.update({"regex": 1})

                    list.append(sdict)
                x += 1
            paper.update({"sentences": list})

    def check_tags(self, type="mesh", list=None):
        #TODO inapplicable for twitter
        from tqdm import tqdm
        """type: mesh or filter
        list: list of instances"""
        if type in ["mesh", "filter"] and list:
            print(f"\nChecking {','.join(list)} {type}s:") #

            for _ in list:
                query=self.make_query(check_tags=type,tags=list)
                res=self.execute_query(Q=query)
                PMIDA = [_.pubmed_id.splitlines() for _ in res]
                PMIDA = [item for sublist in PMIDA for item in sublist] #papers with those PMIDs has the mesh/filter
                for paper in tqdm(self.papers, desc="Papers"):
                    if set(paper.get("PMIDa")).intersection(PMIDA):
                        paper.update({
                            type+"s":list(set(paper.get(type+"s").append(_))) if hasattr(paper,type+"s")
                                      else [_]})

def main(**kwargs):
    crawlerObj = PyMedCrawler(**kwargs)

    crawlerObj.harvest()
    crawlerObj.post_processing()
    if crawlerObj.source=="pubmed":
        crawlerObj.check_tags(type="filter", list=["case reports"])
        crawlerObj.check_tags(type="mesh", list=["adverse effects"])
    crawlerObj.split_to_sents(keywords=True, classify=False, titles=True) #classifying takes some time

    print(crawlerObj.utils(config="sentence_number"))

    return crawlerObj.papers, crawlerObj.drugs, crawlerObj.queries

if __name__ == "__main__":
    import argparse

    """Command Prompt"""
    #TODO update

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
