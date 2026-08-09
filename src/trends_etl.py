
import pandas as pd

from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=360)

kw_list = ["Monster Energy"] 

pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')