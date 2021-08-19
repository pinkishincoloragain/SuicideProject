from get_abstracts_pubmed import PyMedCrawler

# amiodarone
# amfetamine
# fluoxetine

crawlerObj = PyMedCrawler(
    email="??",
    druglist_path="data/drug_mapping_v3_210726_2.xlsx",
    columns=["ingredient_1","ingredient_2", "ingredient_3","ingredient_4","ingredient_5", "ingredient_6","ingredient_7","ingredient_8", "ingredient_9"],
    drugs=["baclofen"],
    max_results=100000,
    suicide_mesh=True,
    from_date="2021/01/01",
    to_date="2021/01/30",
    suicide_tw=True,case_report=True,lang=["English"],
)

crawlerObj.harvest()
crawlerObj.post_processing()

# crawlerObj.check_tags(type="filter", list=["case reports"])
# crawlerObj.check_tags(type="mesh", list=["adverse effects"])
# """plain text of sentences for pretraining"""
# paper = crawlerObj.split_to_sents(keywords=True, classify=False, titles=False)