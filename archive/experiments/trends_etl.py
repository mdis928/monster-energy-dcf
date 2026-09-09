#pytrends is not working because HTTP 429 error. Too many automated requests

import pandas as pd

from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=360)

kw_list = ["Monster Energy"] 

pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')

trends_etl = pytrends.interest_over_time()

print(trends_etl)