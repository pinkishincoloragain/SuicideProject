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



####### 읽는 순서 ########
# harvest -> make_query -> execute_query -> post_processing -> check_tags

class PyMedCrawler:

    def __init__(self, **kwargs):
        import pandas as pd
        # 입력받은 인자에 attribute 붙여 주는 부분
        for k, v in kwargs.items():
            setattr(self, k, v)

        # 쿼리 선언
        self.queries=[]

        # 이건 지금 안 씀.
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

        # 객체에 papers, results를 부여
        # papers에는
        else:
            self.papers=[]
            self.results=[]
            print(
            f"Using drug list {self.druglist_path if hasattr(self, 'druglist_path') else 'input'}, crawling max {self.max_results}  abstracts for {self.email}. "
            f"Corresponding articles were published from {self.from_date if hasattr(self, 'from_date') else str(float('-inf'))} to {self.to_date if hasattr(self, 'to_date') else str(float('inf'))} ")

            # 이것도 입력받은거 attr 붙여 주는거. 쿼리 생성할 확인하면서 씀
            if hasattr(self, "sui_mesh"):
                print(f"using suicide MeSH")
            if hasattr(self,"case_report"):
                print(f"case report filtering")
        self.set_drugs()
        self.n_drugs = len(self.drugs)

    # 지금은 안 씀.
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

    # 이것도 그냥 druglist 생성해 주는 코드. get_drugs랑 똑같음.
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

    # 쿼리 생성 부분
    def make_query(self, drug=None, check_tags=None, tags=None):
        from itertools import product

        # mesh, tw, tag 사용. 필터랑 mesh 어떻게 쓰는 태그 지정해주는듯.
        suicide_meshs = ["Suicidal Ideation", "Suicide, Attempted", "Suicide, Completed", "Suicide"]
        suicide_tws = ["suicid", "suicidal", "suicidality", "suicidally", "suicidals", "suicide", "suicides",
                       "suicide s", "suicided", "suiciders"]
        drug_tags = ["Mesh", "Supplementary concept", "TW"]

        mesh_tags = ["MeSH Subheading", "MeSH"]
        filter_tags=["Filter"]

        filters = []

        # druglist 쓸 지 drug 쓸 지 고르는거.
        if drug:
            filters.append(
                "(" + " OR ".join([drug + f"[{tag}]" for tag in drug_tags]) + ")")

        # if self.drugs:
        #     filters.append(
        #         "(" + " OR ".join([drug + f"[{tag}]" for drug, tag in product(kwargs.get("drugs"), drug_tags)]) + ")")

        # if hasattr(self,'suicide_mesh')

        # 쿼리 생성 부분. if문 읽으면 이해할 수 있을듯. 이전 거랑 거의 차이 없는데 setatter 써서 확인하는 차이.
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

    # 쿼리 실행 부분
    def execute_query(self,Q, drug=None):
        from pymed import PubMed
        from time import sleep
        max_retries=50
        import requests.exceptions

        # 펍메드 크롤링 객체 생성
        pubmed = PubMed(tool="KNU_DSA_PubMed_"+str(drug) if drug else "", email=self.email)
        print(Q)

        # 쿼리를 펍메드 DB에 던지는 부분. retry 50번까지.
        for _ in range(max_retries):

            # response 받음. response에는 쿼리 실행해서 나온 pubmed 객체 꼴임.
            try:
                response = pubmed.query(Q, max_results=self.max_results)
                break
            # Timeout이랑 Type는 언제 생성되는지 모르겠는데
            # requests.exceptions.HTTPError은 DB에 쿼리를 너무 빠르게 많이 던지면 Pubmed 서버가 화내면서 요청 안 받아줌. 오류 던짐.
            except (TimeoutError, TypeError, requests.exceptions.HTTPError) as e:
                sleep(2)
                pass
        # 만약 OK면
        if response: #response OK
            # result에 저장하는 부분, druglist인지 drug인지 판별
            if drug:
                result = [{"obj": item, "drug": drug} for item in response]
            else:
                result = [item for item in response]
        # 크롤링 과정에서 오류 뜨면 warning
        else:
            import warnings
            warnings.warn(f"Connection failed for {drug if drug else  '_'} after {max_retries} retries")
            if drug:
                result = [{"obj": [], "drug": drug}]
            else:
                result = []

        # result 모양이 리스트 안에 dict가 들어 있는 모양.
        # dict 안에는 pubmed 객체랑 약물 들어 있음.
        return result

    # 이제 execute_query까지 해서 객체에 result 모임이 저장되어 있으니까
    # result 가지고 있는 것들 가지고 후처리 진행
    def post_processing(self): #GROUP BY imitation with PMID key to get an array of drug for each paper
        from tqdm import tqdm
        """
        Post-processing
        """
        #keys = ["PMIDlist"]

        # 지금 객체가 갖고 있는 result 중에서 갖고와서 검사 하고 나서 이 객체가 가진 paper에 넣을 거임.
        papers = []
        print("Postprocessing...")
        for article in tqdm(self.results):
            obj = article.get("obj")
            # data = {"abstract": None, "drugs": None,
            #         "title": None, "DOI": None,
            #         "date": None, "PMIDa": None}
            if obj.abstract:
                data = {"abstract": obj.abstract, "drugs": [article.get("drug")],
                        "title": obj.title[0] if isinstance(obj.title, list) else obj.title, "DOI": obj.doi,
                        "date": obj.publication_date, "PMIDa": obj.pubmed_id.splitlines()}
            else:
                continue

            iii = [i for i, x in enumerate(papers) if x["PMIDa"] == data.get("PMIDa")]  # if there are duplicate PMIDs
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


            # raw_abstract = obj.abstract
            # raw_drugs = data['drugs']


            # 여기는 내가 짠 부분. abstract에서 약물이 있는 부분 인덱스 찾고 가져와서 그 뒤 1개 단어 가져옴.
            # 가져오는 이유는 calcium만 갖고 오는데 calcium gluconate도 같이 가져와 버려서..
            # 뒤에 어떤 단어들이 붙는지 찾고 나서 그 그 단어들을 저장. -> next_word_analysis에서 사용.

            # raw_abstract = obj.abstract
            # raw_drugs = data['drugs']
            # res = []
            # if raw_abstract is not None:
            #     for item in raw_drugs:
            #         tokens = raw_abstract.split()
            #         if item in tokens:
            #             drug_idx = tokens.index(item)
            #             res.append(tokens[drug_idx] + " " + tokens[drug_idx+1] + "\n")
            #
            # with open(f"post_processing/temp.csv", "a+") as f:
            #     for item in res:
            #         f.write(item)


            # 이건 대웅좌가 시킨 거 -
            raw_abstract = obj.abstract
            raw_drugs = data['drugs']
            res = []
            if raw_abstract is not None:
                with open(f"post_processing/{data['drugs']}.csv", "a+",encoding='UTF8') as f:
                    f.write("Abstract: " + data['abstract'] + "\n")
                    f.write("Date: "+ str(data['date']) + "\n\n")

        # 이 객체가 가진 papers에 추가.
        self.papers.extend(papers)
        # for paper in self.papers:
        #     del paper["PMIDlist"]

    # 쿼리 실행하고 객체에 저장.
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

        #
        for drug in tqdm.tqdm(drugs): #temporary workaround: 1 process
            # 쿼리 만들어주고
            query=self.make_query(drug)
            # 쿼리 실행해서 아까 그 list 안 dictionary 꼴인 result 받고
            res = self.execute_query(drug=drug, Q=query)

            # 쿼리들, result들에 추가.
            self.queries.append(query)
            self.results.extend(res)

    # 결과 안에 있는 abstract를 문장 단위로 자름.
    def split_to_sents(self,classify=False, keywords=False, titles=False):
        print("Getting sentences...")
        from tqdm import tqdm
        import nltk.data
        sui_keywords=["suicid"]
        exc_sents=["(ABSTRACT TRUNCATED AT 250 WORDS)"]
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

        # 분류하는거. 지금 안씀.
        if classify:
            from transformers import pipeline
            sui_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            candidate_labels = ["suicide", "non-suicide"]

        x = 0 #cross-paper sentence counter
        for paper in tqdm(self.papers):
            ss = tokenizer.tokenize(paper['abstract']) #TODO tokenizers???
            list = []
            if titles:
                paper.update({"is_suicidal":"", "ADE":""})
                if keywords:
                    suiskw = [kw for kw in sui_keywords if kw in paper.get("title")]
                    if suiskw:
                        paper.update({"sui_keywords": suiskw})
                        if classify:
                            k = sui_classifier(paper.get("title"), candidate_labels)
                            paper.update({"sui_clasifier": k.get("scores")[k.get("labels").index("suicide")]})  # score for suicide
                            # sdict.update({"sui_classifier": k.get("labels")[k.get("scores").index(max(k.get("scores")))]}) #a label
            # 잘라서 문장 단위로 넣어줌.
            for s in ss:
                if s not in exc_sents:
                    sdict={"ID": "s" + str(x), "sent": s, "is_suicidal": "", "ADE": "",
                                 "drugs": [drug for drug in paper['drugs'] if drug in s]}
                    if keywords:
                        suiskw=[kw for kw in sui_keywords if kw in s]
                        if suiskw:
                            sdict.update({"sui_keywords":suiskw})

                    if classify:
                        k = sui_classifier(s, candidate_labels)
                        sdict.update({"sui_clasifier":k.get("scores")[k.get("labels").index("suicide")]}) #score for suicide
                        # sdict.update({"sui_classifier": k.get("labels")[k.get("scores").index(max(k.get("scores")))]}) #a label
                    list.append(sdict)
                x += 1
            # paper에 업데이트해주고.. 그리고 뭐 안하는듯..?
            paper.update({"sentences": list})

    # 이것도 지금은 안 씀.
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
    crawlerObj.check_tags(type="filter", list=["case reports"])
    crawlerObj.check_tags(type="mesh", list=["adverse effects"])
    crawlerObj.split_to_sents(keywords=True, classify=False, titles=True) #classifying takes some time

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
