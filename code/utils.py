#!/usr/bin/python3
"""
	Cultural Recommendation for Wikipedia Utils
"""
import json
import pandas as pd
import requests
import time

from collections import defaultdict, Counter

def save2json(data, filename):
	with open(filename, "w") as file:
		json.dump(data, file, sort_keys=True, indent=4)

def read_from_json(filename):
	''' read from json file if the file exists '''
	return json.load(open(filename))

def query_wikidata(wikidata_query):

	sparql = "https://query.wikidata.org/sparql"  
	r = requests.get(sparql, params = {'format': 'json', 'query': wikidata_query})

	# http errors have codes >= 400, 200 is good.
	#if r.status_code != 200: return pd.DataFrame()
	r = r.json()
	result = pd.json_normalize(r['results']['bindings'])

	return result

if __name__ == "__main__":
	save2json()
	query_wikidata()