#!/usr/bin/python3
"""
	Get prior probabilities for event type and language links.
	Query Wikidata using SPARQL. 

	1) Prior probability of event type P(Et): # events of type T / total # of events
	2) Prior probability of lanugage link P(Ll): # ll to language L / total # of language links to all language	

	Also need:
		1 the distance from the event to the center of query LV, e.g. capitol.
    	4 event related entities popularity in query language (e.g. length of entity page in query language) or number of mentions of entity on query language Wiki.)

"""
import json
import pandas as pd
import requests
import time
import utils

from collections import defaultdict, Counter

languages = sorted(open("resources/wikipedia_LVs.txt").readlines()) 
# LV_stats = sorted(open("resources/wikipedia_LV_stats.tsv").readlines()[1:])
# LV_sizes = {}
# for line in LV_stats:
# 	line = line.split("\t")
# 	language = line[1].strip()

# 	size = int(line[2].strip().replace(",",""))
# 	if size > 30000:
# 		LV_sizes[language] = size

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
"""


# def get_sum_lls(language_links):
# 	sum_lls_per_lang = Counter()
# 	for l in language_links:
# 		for l1 in language_links[l]:
# 			sum_lls_per_lang[l1] += language_links[l][l1]
# 	return sum_lls_per_lang

# def normalize_by_lls(language_links, sum_lls_per_lang):
# 	for l in language_links:
# 		for l1 in language_links[l]:
# 			if l1 not in sum_lls_per_lang: del language_links[l][l1]
# 			normalized = language_links[l][l1]/sum_lls_per_lang[l1]
# 			language_links[l][l1] = normalized
# 	return language_links

# def normalize_by_LVsize(pairs):
# 	to_delete = []
# 	for l1 in pairs:
# 		if l1 in LV_sizes:
# 			pairs[l1] = pairs[l1]/LV_sizes[l1]
# 		else:
# 			to_delete.append(l1)
# 	for l in to_delete:
# 		print(l)
# 		del pairs[l]
# 	return pairs

def normalize(counter):
	total = sum(counter.values())

	for key, value in counter.items():
		counter[key] = (value/total) * 100
	return counter

def get_language_pairs():
	''' Get language links per query language for languages that have the same pages as query language.'''

	for lang in languages:
		language_links = {}
		lang = lang.strip()
		pairs = Counter()
		print(10*" * ", lang)
		result = utils.query_wikidata(language_pairs_query % (lang, lang))
		if result.empty == True: continue

		l1s = result["l1.value"]
		values = result["cnt.value"]

		for l1, v in zip(l1s, values):
			pairs[l1] = int(v)

		language_links[lang] = normalize(pairs)
		utils.save2json(language_links, "resources/language_links_%s.json" % lang)

def get_event_distributions():

	for lang in languages:

		event_dist_per_language = {}
		event_distribution = Counter()

		lang = lang.strip()
		print(10*" * ", lang)

		# Just using one of the wds for "event":
		result = utils.query_wikidata(event_distribution_query % ("wd:Q1656682", lang))
		
		if result.empty == True: continue
		event_types = result["eventType.value"]
		values = result["cnt.value"]

		for et, v in zip(event_types, values):
			event_distribution[et.split("/")[-1]] = int(v)

		if event_distribution:
			normalized_distribution = normalize(event_distribution)
			event_dist_per_language[lang] = normalized_distribution

		utils.save2json(event_dist_per_language, "resources/event_distributions_%s.json" % lang)
		event_dist_per_language = {}

if __name__ == "__main__":
	get_language_pairs()
	#get_event_distributions()

