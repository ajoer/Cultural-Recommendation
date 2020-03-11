#!/usr/bin/python3
"""
	Query Wikidata using SPARQL. 

	1 the distance from the event to the center of query LV, e.g. capitol.
    2 the prior similarity of other LVs with the given article to query LV (how many articles are both on the FR and DE pages, normalized by querying language)
    3 the prior relevance of the type of event to query LV  (how many "sport events" are on DE Wiki, normalized)
    4 (this is not for here. Wikipedia.) event related entities popularity in query language (e.g. length of entity page in query language) or number of mentions of entity on query language Wiki.)

1: Stabile: query LV center
2: Fully stabile: dict of counters, normalized(!) { de: { fr: 29, en: 12 }, fr: { de: 30, en: 89, da: 3 } }
3: Fully stabile: dict of counters, normalized(!) { de: { sports: 2, election: 12, performance: 0 }, fr: { sport: 30, election: 89, performance: 3 } }
4: Online.

"""
import json
import pandas as pd
import requests
import time

from collections import defaultdict, Counter

languages = sorted(open("resources/wikipedia_LVs.txt").readlines()) #["da", "sv"] #"de", "fr", "da", "sv"]  #

all_languages = """
SELECT ?l 
WHERE
{
	?l wdt:P31/wdt:P279 wd:P424 .
"""

language_pairs_query = """
SELECT (COUNT(DISTINCT(?item)) AS ?cnt) ?l1 
WHERE 
{
	?item wdt:P31/wdt:P279 wd:Q1190554 .
	?article1 schema:about ?item .
	?article1 schema:inLanguage "%s" .
	?article2 schema:about ?item .
	?article2 schema:inLanguage ?l1 .
	FILTER("%s" != ?l1) .
}
GROUP BY ?l1 ORDER BY DESC(COUNT(DISTINCT(?item)))
#LIMIT 10
"""

# (Two types of event classes)
# %s = wd:Q1656682, wd:Q1190554
event_types_query = """
SELECT ?item ?itemLabel (COUNT(?x) AS ?cnt)
WHERE
{
	?item wdt:P279 %s .
	?x wdt:P31 ?item .
	SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
} 
GROUP BY ?item ?itemLabel ORDER BY DESC(COUNT(?x))
LIMIT 10
"""

event_distribution_query = """
SELECT ?eventType (COUNT(?event) AS ?cnt)
WHERE
{
	?event wdt:P31 ?eventType .
 	?eventType wdt:P279* %s .
 
	?sitelink schema:about ?event .
	?sitelink schema:inLanguage "%s" .
	SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }

}
GROUP BY ?eventType ORDER BY DESC(COUNT(?event))
LIMIT 10
"""

def save_json(new_data, file_name):

	with open(file_name, "r+") as file:
		file_data = json.load(file)
		file_data.update(new_data)
		file.seek(0)
		json.dump(file_data, file, sort_keys=True, indent=4)

def query_wikidata(wikidata_query):

	sparql = "https://query.wikidata.org/sparql"  
	r = requests.get(sparql, params = {'format': 'json', 'query': wikidata_query})
	print(r, r.status_code)
	# http errors have codes >= 400, 200 is good.
	if r.status_code != 200: return pd.DataFrame()
	r = r.json()
	result = pd.io.json.json_normalize(r['results']['bindings'])
	return result

def normalize_values(event_distribution):

	total = sum(event_distribution.values())

	for key, value in event_distribution.items():
		event_distribution[key] = value/total

	return event_distribution

def get_language_pairs():
	''' Get language links per query language for languages that have the same pages as query language.'''
	#language_links = defaultdict()

	for lang in languages:
		lang = lang.strip()
		pairs = Counter()
		print(10*" * ", lang)
		result = query_wikidata(language_pairs_query % (lang, lang))
		if result.empty == True: continue

		l1s = result["l1.value"]
		values = result["cnt.value"]

		for l1, v in zip(l1s, values):
			pairs[l1] = int(v)
		#language_links[lang] = pairs
		save_json(pairs, "language_links.json")

# def get_event_types():
# 	''' Get counts of event types. 
# 		Get distributions of event types per language version'''

# 	result = query_wikidata(event_types_query)
# 	items = result["item.value"]
# 	itemlabels = result["itemLabel.value"]
# 	values = result["cnt.value"]
# 	print(result)

def get_event_distributions():
	event_dist_per_language = defaultdict()

	for lang in languages:
		event_distribution = Counter()

		lang = lang.strip()
		print(10*" * ", lang)

		# Just using one of the wds for "event":
		result = query_wikidata(event_distribution_query % ("wd:Q1656682", lang))
		
		if result.empty == True or result is None: continue
		event_types = result["eventType.value"]
		values = result["cnt.value"]

		for et, v in zip(event_types, values):
			event_distribution[et.split("/")[-1]] = int(v)

		if event_distribution:
			normalized_distribution = normalize_values(event_distribution)
			print(normalized_distribution)
			event_dist_per_language[lang] = normalized_distribution
	
			save_json(event_dist_per_language, "event_distributions.json")
			del event_dist_per_language[lang]
	#return event_dist_per_language

if __name__ == "__main__":
	#get_language_pairs()
	get_event_distributions()

