def pymed(args):
    """
    :type mesh: bool
    :type case_report: bool
    """

    from pymed import PubMed # pymed - PubMed에 대한 접근을 제공하는 라이브러리
    from tqdm import tqdm # 연속적인 작업(ex. for문 while문) 수행시 진행률을 알려주는 라이브러리

    meshs = ["Suicidal Ideation", "Suicide, Attempted", "Suicide, Completed"]
    # meshids=["D059020","D013406","D000081013"]

    pubmed = PubMed(tool="MyTool", email=args.get('email')) #
    print(pubmed)
    # query = "baclofen[Abstract]"
    # query = " Suicide/drug effects[Mesh]"
    # query =" OR ".join([_+"[Mesh]" for _ in meshs] )
    query = "(" + " OR ".join([_ + "[Abstract]" for _ in args.get('drugs')]) + ")" \
            + " AND " \
            + f"({args.get('from_date')}[Date - Publication] : {args.get('to_date')}[Date - Publication])"
# 'drug' : ['aspirin', 'vitamin', 'omega-3']
# 'from_date' : 10/10/11, to_date : 11/08/10
# query = ( aspirin[Abstract] OR vigamin[Abstract] OR ...)
#          AND (10/10/11[Date - Publication] : 11/08/10[Date - Publication])

    if args.get('mesh'): # 키 'mesh'의 value가 true이면
        query = query + " AND " \
                     + "(" + " OR ".join([_ + "[Mesh]" for _ in meshs]) + ")"
    # query에 AND (Suicidal Ideation[Mesh] OR Suicide, Attempted[Mesh] OR Suicide, Completed[Mesh]) 추가

    if args.get('case_report'): #키 'case_report'의 value가 true이면
        query = query + " AND " \
                     + "(" +"case reports"+ "[Filter]" + ")"
    # query에 AND (case reports[Filter]) 추가

    print(query)
    results = pubmed.query(query, max_results=args.get('max_results'))

    papers = []

    """
    Post-processing
    """
    for article in tqdm(results): #
        abstract = article.abstract #
        # if abstract and any(drug in abstract for drug in drugs):
        if abstract:
            drugsfound=[]
            for drug in args.get('drugs'):
                if drug in abstract:
                    drugsfound.append(drug)
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
    # 'mesh' value가 true이면 "using MeSH" 프린트
    #               false이면 "no MeSH:" 프린트

    print(f"case report filtering:" if kwargs.get('case_report') else 'no filtering:')
    # 'case_report' value가 true이면 "case report filtering:" 프린트
    #                      false이면 "no filtering:" 프린트


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
    #paser 객체 생성

    parser.add_argument('--email', help='User email', default='???')
    parser.add_argument('--druglist_path', help='Path for a CSV with drug list', default="suicideSE_drugs.csv")
    parser.add_argument('--max_results', help='Maximum results for the query',default=10000, type=int)
    parser.add_argument("--from_date", help="The date (YYYY/MM/DD) after which the publication was published", default="2010/01/01")
    parser.add_argument("--to_date", help="The date (YYYY/MM/DD) before which the publication was published",default="2021/05/23")

    parser.add_argument("--mesh", dest="mesh", action="store_true",help="Using suicidal MeSHs(bool)")
    parser.add_argument("--no_mesh", dest="mesh", action="store_false", help="NOT using suicidal MeSHs(bool)")
    parser.set_defaults(mesh=True)

    parser.add_argument("--case_report", dest="case_report", action="store_true", help="Using case report filtering")
    parser.add_argument("--no_case_report", dest="case_report", action="store_false", help="NOT using case report filtering")
    parser.set_defaults(case_report=False)

    parser.add_argument("--drugs", type= list , help="Array of drug names")
    
    # parser에 넣어 주는 거 .
    # 사실 쿼리는 거의 다 만들어져 있고 ,, type 지정 잘 해 주고 예외처리만 예쁘게 하면 됩니다

    args_main = parser.parse_args() # args_main은 넣어 주는 인자들의 이름들 -- 떼고 email, druglist_path, .. 등을 갖고 있습니다

    for key in args_main.__dict__: # 사실 필요하지 않지만, 인자들에 어떤 값이 들어 있는지 출력해주는 부분. args_main을 dict 형식으로 만들어서
        print(args_main.__dict__.get(key)) # dict 안에 키값으로 불러와서 출력함.

    # 이제 해야 할 부분은
    # 1. 어떤 인자가 만약 잘못 들어 오면 어떻게 할 것인지 (예외처리)
    # 2. drug_list type이 list인데 저걸 어떻게 예쁘게 받아 올 지. csv파일 써서 가져올지, 아님 get_drugs.py 저거 만든 걸 쓸지. 아니면 따로 뭐 새로 만들지.
    # 3. 사용자가 CLI에 인자 하나하나 넣어 줄지 아니면 한방에 빡 넣어 버릴 지.. 근데 아마 카리나좌가 원하는 건 한방에 넣는 거 좋아할듯.
    # 4. 결과 잘 실행되고 쿼리문 들어간 결과를 output 파일에 넣기
    # (4.1) output 파일 전처리 - 이건 할 게 많아 보임.
    # 5. tqdm 저거 지금은 조금 이상해 보여서 - 예쁘게 수정하기
    # 6. 마지막으로 get_abstracts_pubmed.py (지금 이 파이썬 파일) exe파일로 만들기 ! - 이건 그냥 라이브러리 하나 써서 import 해서 만들어버리면 됨.

    temp = pymed(args_main.__dict__) # pymed에 넣어 줌. 지금은 예외처리 하나도 되지 않고 그냥 인자 받은 그대로 넘겨줌.
    print("!!!!",args_main.email)

    # 실행 방법
    # 터미널창에 가서 \SuicideProject\PubmedProject2> 경로에 가서
    # python get_abstracts_pubmed.py --email smb1103@gmail.com --druglist_path Drug_mapping_v2.csv --max_results 10 --from_date 2021/01/01 --to_date 2021/07/01 --no_mesh  --case_report --drugs a
    # 이렇게 넣어 주면 실행이 됩니다.
    # --(인자이름) (인자에 넣을 값) 이런 형식으로 들어가고,
    # 저걸 하나하나 가져오려면 args_main.(인자이름) 이렇게 가져오면 됨. 예를 들면 args_main.email 이렇게 


    for article in temp: # 결과값 temp라는 곳에 저장했으니까 그 안에 article들이 max_num 갯수만큼 있는데
        print(article) # 지금은 output 파일에 넣지 않고 그냥 출력함.


    #python
    #get_abstracts_pubmed.py - -email
    #leeja0407 @ naver.com - -mesh - -case_report - -drugs[aspirin]
    # TODO
    # main(args)

