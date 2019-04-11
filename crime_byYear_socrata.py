#!/usr/bin/env python

# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import pandas as pd
from sodapy import Socrata
import time

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofchicago.org", None)

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
offset = 0
limit = 30000
results = []
for i in range(0,10):
    # ADJUST YEAR IN PARAMETERS
    results += client.get("6zsd-86xi", where="year == 2014",limit=limit,offset=offset)
    offset += limit
    time.sleep(.300)

# Convert to pandas DataFrame
df = pd.DataFrame.from_records(results)
print(df)
df.to_csv ('crime2014.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path
