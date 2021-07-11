from pymed import PubMed

import pandas as pd
pubmed = PubMed(tool="PubMedSearcher", email="myemail@ccc.com")

## PUT YOUR SEARCH TERM HERE ##
search_term = "Your search term"
results = pubmed.query(search_term, max_results=20)

print(results)