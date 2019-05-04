import pandas as pd

def process_crime():
	df = pd.read_csv('crime_data.csv')
	crime_type = list(set(df['primary_type'].values))
	codes = list(set(df['community_area'].values))
	years = [i for i in range(2011, 2019)]
	records = []
	for co in codes:
		for y in years:
			rec = [co, y]
			for t in crime_type:
				count = 0
				curr = df.loc[(df['community_area']==co) & (df['year']==y) & (df['primary_type']==t), 'count']

				if len(curr.values) != 0:
				    count = curr.values[0]
				    
				rec.append(count)

			records.append(rec)
	cols = ['community', 'year'] + crime_type
	return pd.DataFrame(records, columns=cols)