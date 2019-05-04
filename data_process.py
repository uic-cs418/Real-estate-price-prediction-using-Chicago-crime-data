from google.cloud import storage

def process_crime():
	%%bigquery df

	SELECT community_area, year, primary_type, COUNT(*) as count FROM `bigquery-public-data.chicago_crime.crime`
	WHERE community_area IS NOT NULL AND year > 2009  AND year < 2019 AND community_area > 0 AND primary_type IS NOT NULL
	GROUP BY community_area, year, primary_type
	ORDER BY community_area, year, primary_type

	return df