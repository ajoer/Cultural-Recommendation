#!/usr/bin/python3
"""
	Query Wikidata using SPARQL. 

	1 the distance from the event to the center of query LV, e.g. capitol.
    2 the prior similarity of other LVs with the given article to query LV (how many articles are both on the FR and DE pages, normalized by querying language)
    3 the prior relevance of the type of event to query LV  (how many "sport events" are on DE Wiki, normalized)
    4 event related entities popularity in query language (e.g. length of entity page in query language) or number of mentions of entity on query language Wiki.)

1: Stabile: query LV center
2: Fully stabile: dict of counters, normalized(!) { de: { fr: 29, en: 12 }, fr: { de: 30, en: 89, da: 3 } }
3: Fully stabile: dict of counters, normalized(!) { de: { sports: 2, election: 12, performance: 0 }, fr: { sport: 30, election: 89, performance: 3 } }
4: Online.

"""

import pandas as pd
import requests

from collections import defaultdict, Counter

languages = sorted(open("resources/wikipedia_LVs.txt").readlines()) #["de", "fr", "da", "sv"] 

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
LIMIT 10
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

def query_wikidata(wikidata_query):

	sparql = "https://query.wikidata.org/sparql"  
	r = requests.get(sparql, params = {'format': 'json', 'query': wikidata_query}).json()
	result = pd.io.json.json_normalize(r['results']['bindings'])
	return result

def normalize_values(event_dist_lang):

	total = sum(event_dist_lang.values())
	print(total)

	for key, value in event_dist_lang.items():
		event_dist_lang[key] = value/total
		print(key, value, total, event_dist_lang[key])

	return event_dist_lang

def get_language_pairs():
	''' Get language links per query language for languages that have the same pages as query language.'''
	language_pairs = defaultdict()

	for lang in languages:
		pairs = Counter()
		print(10*" * ", lang)
		result = query_wikidata(language_pairs_query % (lang, lang))

		l1s = result["l1.value"]
		values = result["cnt.value"]

		for l1, v in zip(l1s, values):
			pairs[l1s] = int(v)
			print(l1, '\t', v)
		language_pairs[l] = pairs

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
		event_dist_lang = Counter()
		print(10*" * ", lang)

		event_classes = ["wd:Q1656682"]
		for n, event_code in enumerate(event_classes): #, "wd:Q1190554"]:

			event_dist = Counter()
			result = query_wikidata(event_distribution_query % (event_code, lang))
			if not result: continue
			print(result)
			event_types = result["eventType.value"]
			values = result["cnt.value"]

			for et,v in zip(event_types, values):
				event_dist[et.split("/")[-1]] = int(v)

			event_dist_lang += event_dist

		if event_dist_lang:
			normalized_distribution = normalize_values(event_dist_lang)
			print(normalized_distribution)
			event_dist_per_language(normalized_distribution)
	
	return event_dist_per_language

get_event_distributions()

