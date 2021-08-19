import twitter_set_drugs
import twitter_crawling_Ver_API

drug_brand = twitter_set_drugs.Drugs()
main_crawling = twitter_crawling_Ver_API.Crawling()

# print(drug_brand.brandname_lists[0])
# print(drug_brand.columns[0])

'''
for i in range(0, 1): #len(drug_brand.columns)):
    print(drug_brand.columns[i] + " start")
    main_crawling.main_act_months(drug_brand.brandname_lists[i], drug_brand.columns[i])
    print(drug_brand.columns[i] + " done")
'''

# main_crawling.main_act_id("1061602142", "2016-01-01T00:00:00Z", "2017-01-01T00:00:00Z")

main_crawling.main_act_months(drug_brand.brandname_lists[0], drug_brand.columns[0], 2016, 2020)

# main_crawling.main_act_indi(drug_brand.brandname_lists[0], drug_brand.columns[0])

# main_crawling.main_act_weeks(drug_brand.brandname_lists[3], drug_brand.columns[3])

# main_crawling.main_act_indi(drug_brand.brandname_lists[3], drug_brand.columns[3])
