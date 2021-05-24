import twitter_set_drugs
import twitter_crawling_Ver_API

drug_brand = twitter_set_drugs.Drugs()
main_crawling = twitter_crawling_Ver_API.Crawling()

# print(drug_brand.brandname_lists)
# print(drug_brand.columns)

for i in range(0, 1): #len(drug_brand.columns)):
    print(drug_brand.columns[i] + " start")
    main_crawling.main_act(drug_brand.brandname_lists[i], drug_brand.columns[i])
    print(drug_brand.columns[i] + " done")
