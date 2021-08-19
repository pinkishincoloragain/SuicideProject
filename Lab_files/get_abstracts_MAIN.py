import pandas as pd
from tqdm import tqdm

def label_stats(to_label):
    dfl = pd.DataFrame(to_label)
    if "drugs" in dfl.columns:
        dfl.drop(["drugs"], axis=1, inplace=True)

    # filtered_df = df[df['name'].notnull()]
    # filtered_df = df[df[['name', 'country', 'region']].notnull().all(1)]
    print("\n""sent+drug""")
    print((len(dfl[(dfl['sui_clasifier'] > 0.5) & (dfl["ID"].str.startswith("s"))].index)))
    print((len(dfl[(dfl['sui_keywords'].notnull()) & (dfl["ID"].str.startswith("s")) ].index)))
    print((len(dfl[((dfl['sui_clasifier'] > 0.5) & (dfl['sui_keywords'].notnull())) & dfl["ID"].str.startswith("s")].index)))
    print((len(dfl[
                   ((dfl['sui_clasifier'] > 0.5) | (dfl['sui_keywords'].notnull())) & dfl["ID"].str.startswith("s")
                   ].index)))


    print("")

    print((len(dfl[dfl["ID"].str.startswith("s")].index)))
    print((len(dfl[(dfl['meshs'].notnull())  & dfl["ID"].str.startswith("s")].index)))
    print((len(dfl[(dfl['filters'].notnull()) & dfl["ID"].str.startswith("s")].index)))
    print((len(dfl[(dfl['MEDLINE_ADE'].notnull()) & dfl["ID"].str.startswith("s")].index)) if "MEDLINE_ADE" in dfl.columns else 0)

    print("\n""title+drug""")
    print((len(dfl[(dfl['sui_clasifier'] > 0.5) & (dfl["ID"].str.startswith("t"))].index)))
    print((len(dfl[(dfl['sui_keywords'].notnull()) & (dfl["ID"].str.startswith("t"))].index)))
    print((len(dfl[(dfl['sui_clasifier'] > 0.5) & (dfl['sui_keywords'].notnull())  & dfl["ID"].str.startswith("t")].index)))
    print((len(dfl[
                   ((dfl['sui_clasifier'] > 0.5) | (dfl['sui_keywords'].notnull())) & dfl["ID"].str.startswith("t")
                   ].index)))

    print("")
    print((len(dfl[dfl["ID"].str.startswith("t")].index)))
    print((len(dfl[(dfl['meshs'].notnull()) & dfl["ID"].str.startswith("t")].index)))
    print((len(dfl[(dfl['filters'].notnull()) & dfl["ID"].str.startswith("t")].index)))
    print((len(dfl[(dfl['MEDLINE_ADE'].notnull()) & dfl["ID"].str.startswith("t")].index))if "MEDLINE_ADE" in dfl.columns else 0)

    print("\n""title/sent+drug""")
    print((len(dfl[(dfl['sui_clasifier'] > 0.5) ].index)))
    print((len(dfl[(dfl['sui_keywords'].notnull())  ].index)))
    print((len(dfl[(dfl['sui_clasifier'] > 0.5) & (dfl['sui_keywords'].notnull()) ].index)))
    print((len(dfl[(dfl['sui_clasifier'] > 0.5) | (dfl['sui_keywords'].notnull())].index)))

    print("")
    print((len(dfl.index)))
    print((len(dfl[(dfl['meshs'].notnull()) ].index)))
    print((len(dfl[(dfl['filters'].notnull())].index)))
    print((len(dfl[(dfl['MEDLINE_ADE'].notnull())].index)) if "MEDLINE_ADE" in dfl.columns else 0)

def save_crawled(output_file, abstracts, drugs=None, queries=None, label=None):
    df = pd.DataFrame(abstracts)

    if not df.empty:

        # df['drugs'] = df['drugs'].map(lambda x: ',\n'.join(x))
        df['PMID'] = df['PMIDa'].map(lambda x: ',\n'.join(x))

        df.drop(["PMIDa", "PMID"], axis=1, inplace=True) #, "PMIDlist"
        if "sentences" in df.columns:
            df.drop(["sentences"], axis=1, inplace=True)
        writer = pd.ExcelWriter(output_file, engine='openpyxl')
        df.to_excel(writer, sheet_name="result", index=False)

        if drugs:
            dfdrugs = pd.DataFrame({'Drugs': drugs})
            dfdrugs.to_excel(writer, sheet_name="drugs", index=False)

        if queries:
            dfq = pd.DataFrame({'Queries': queries})
            dfq.to_excel(writer, sheet_name="queries", index=False)

        if label:
            dfl=pd.DataFrame(label)
            if "drugs" in dfl.columns:
                dfl.drop(["drugs"], axis=1, inplace=True)
            dfl.to_excel(writer, sheet_name="label", index=False)

        writer.save()
        print(f"Saved crawled {output_file}")

    else:
        print("Empty")
    return df

def make_for_labelling(papers, MEDLINE_dataset=False, titles=False):
    from tqdm import tqdm

    #TODO include titles

    print("For labeling...")
    paper_level_keys = ["PMIDa", "meshs", "filters"]
    title_keys=["PMIDa","meshs","title",
                # "is_suicidal", "ADE",
                "filters"]
    title_attr_keys=["sui_clasifier","sui_keywords","regex"] #med7 requires preprocessing

    oldlist=[]
    for ss in papers:
        ll=[
            {**dict((k, ss[k]) for k in paper_level_keys if k in ss.keys()),
             **s}
            for s in ss.get('sentences')
        ]

        for l in ll:
            if "med7" in l.keys():
                l.update({"med7": [_.get('text') for _ in l.get("med7")]})
            # try: #hasattr is not working
            #     l.update({"med7": [_.get('text') for _ in l.get("med7")]})
            # except TypeError:
            #     continue


        oldlist.extend([item for item in ll if item.get('drugs')])

        if titles:
            if ss.get("title"):
                d={k: v for k, v in ss.items() if k in title_keys}
                if "title_attr" in ss.keys():
                    d.update({k: v for k, v in ss["title_attr"].items() if k in set(title_attr_keys).intersection(ss["title_attr"].keys())})
                    if "med7" in ss["title_attr"].keys():
                        d.update({"med7": [_.get('text') for _ in ss["title_attr"].get("med7")]})#
                d.update({"drugs":[drug for drug in ss.get('drugs') if drug.lower() in ss.get("title").lower()]}) #TODO drug overlap
                d["sent"] = d.pop("title")
                d["ID"]="t"+d.get("PMIDa")[0]

                oldlist.append(d)

    # oldlist = [item for sublist in aaa for item in sublist if item.get('drugs')] #all sentence dictionaries with drugs
    # oldlist = [item for sublist in [ss.get('sentences') for ss in papers] for item in sublist]  # all sentence dictionaries

    #TODO calculate % sentences that we have in the old list , probably split above command into two and calculate in between?

    #deal with multidrugs: split to unique sentence - drug pairs
    newlist=[]
    for _ in oldlist:
        for d in _.get('drugs'):
            newitem = _.copy() #copy and edit the copy
            newitem["drug"] = d
            if "med7" in _.keys():
                if d.lower() in [item.lower() for item in _.get("med7")]:
                    newitem["med7_match"] = 1
            # try:
            #     if d.lower() in [item.lower() for item in _.get("med7")]:
            #         newitem["med7_match"] = 1
            # except TypeError:
            #     continue
            newlist.append(newitem)

    if MEDLINE_dataset:
        MEDLINE_dataset_path="data/DRUG-AE.rel"
        MEDLINEdf = pd.read_csv(MEDLINE_dataset_path, sep='|',
                            names=['PMID', 'text', 'ADE', 'ADE_offsetfrom', 'ADE_offsetto', 'drug', 'drug_offsetfrom',
                                   'drug_offsetto'], usecols=['PMID', 'text', 'ADE','drug'])
        MEDLINEdf['PMID']=MEDLINEdf.PMID.astype('string')
        for _ in tqdm(newlist, desc="Pairs"):
            df=MEDLINEdf[MEDLINEdf['PMID'].isin(_["PMIDa"])] #PMID filter #TODO
            df=df.loc[df['text']==_["sent"]] #sentence filter, should it be more flexible?
            df=df.loc[df['drug']==_["drug"]] #drug filter
            if not df.empty: _["MEDLINE_ADE"] = df["ADE"].tolist()

    return newlist

def main():

    output="crawled/PubMed0813"
    # output = "crawled/calcium2"
    filepath_pickle=output+"_object.pickle"
    label_pickle = output + "_to_label.pickle"
    from get_abstracts_pubmed import PyMedCrawler
    import pickle,re
    #
    with open(filepath_pickle, 'rb') as f:
        print("Loading the pickle...")
        crawlerObj = pickle.load(f)
        print(f"Object has been loaded from the {filepath_pickle} file")


    # print(f"\nCrawling (../{output})...")
    # crawlerObj = Crawler(email="?",
    #                                                    druglist_path="data/drug_mapping_v3_210726_2.xlsx", columns=["ingredient_1","ingredient_2", "ingredient_3","ingredient_4","ingredient_5", "ingredient_6","ingredient_7","ingredient_8", "ingredient_9"],
    #                                                    # drugs=["calcium", "aspirin", "lactic acid", "salicylic acid"],
    #                                                    # drugs=["calcium", "calcium gluconate"],
    #                                                    # drugs=["glucagon", "isoprenaline","isoprenaline", "propranolol","amlodipine", "calcium", "aspirin"],
    #                                                    max_results=100000,
    #                                                    suicide_mesh=True, suicide_tw=True,
    #                                                    lang=["English"],
    #                      source=["pubmed", "twitter"]
    #                           )
                              # ,restore=output+"_to_label.xlsx")
    # #

    crawlerObj.harvest()
    # crawlerObj.post_processing()
    # crawlerObj.check_tags(type="filter", list=["case reports"])
    # crawlerObj.check_tags(type="mesh", list=["adverse effects"])
    # crawlerObj.split_to_sents(keywords=True, classify=True, titles=True, regex_sentsplit=True, med7=True)
    # #


    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # #
    # import tqdm
    # for paper in tqdm.tqdm(crawlerObj.papers):
    #     for s in paper["sentences"]:
    #         suiskw = [kw for kw in ['suicid'] if kw in s["sent"].lower()]
    #         if suiskw:
    #             s.update({"sui_keywords": suiskw})
    # """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    with open(filepath_pickle, 'wb') as f:
        print("Saving the pickle...")
        pickle.dump(crawlerObj, f)
        print(f"Saved crawled object as a pickle {filepath_pickle}")


    with open(filepath_pickle, 'wb') as f:
        print("Saving the pickle...")
        pickle.dump(crawlerObj, f)
        print(f"Saved crawled object as a pickle {filepath_pickle}")
    # #
    sentences=[item.get("sent") for sublist in
               [ss.get('sentences') for ss in crawlerObj.papers]
                                             for item in sublist] #flatten
    with open(output+'_plain_text.txt', mode='w+', encoding='utf-8') as myfile: #and saving
        myfile.write('\n\n'.join(sentences))
        myfile.write('\n')
        myfile.close()
        print("Plain file saved")

    print(len(crawlerObj.utils(config='wrong_parsing')))
    print(len(crawlerObj.utils(config='wrong_parsing', drugs=True)))
    print(len(crawlerObj.utils(config="abstract_number", entities="meshs")))
    print(len(crawlerObj.utils(config="abstract_number", entities="filters")))
    print("")
    print(len(crawlerObj.utils(config="title_number")))
    print(len(crawlerObj.utils(config="title_number", drugs=True)))
    print(len(crawlerObj.utils(config="abstract_number")))
    print(len(crawlerObj.utils(config="sentence_number")))
    print(len(crawlerObj.utils(config="sentence_number", drugs=True)))

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    to_label= make_for_labelling(crawlerObj.papers, MEDLINE_dataset=True, titles=True)
    with open(label_pickle, 'wb') as f:
        print("Saving the pickle...")
        pickle.dump(to_label, f)
        print(f"Saved to label object as a pickle ")
    df=save_crawled(abstracts=crawlerObj.papers, drugs=crawlerObj.drugs,
                 queries=crawlerObj.queries,
                 output_file=output+"_to_label.xlsx", label=to_label)
    #

    label_stats(to_label)

    # with open(label_pickle, 'rb') as f:
    #     print("Loading the pickle...")
    #     to_label = pickle.load(f)
    #     print(f"Object has been loaded from the {label_pickle} file")


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    main()
