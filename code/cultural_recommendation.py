#!/usr/bin/python3
"""

Calculate probability that a page is culturally relevant for a language version.

for event in events:

	if check_if_page_exists == True: continue

	page_probability = calculate_page_probability(event_type, event_geo, LVs_with)

	if page_probability > threshold:
		recommend_page == True


"""
import json
import pandas as pd
import requests
import time
import utils

from collections import defaultdict, Counter
"""
event_types = all subclasses from "Event"

recommended_pages = {}

for type in events:
	for event in events[type]:
		# get all languages that have that event
		event_languages = get_event_languages(event)

		for language in languages:
			# page already exists
			if language in event_languages: continue
			event_probability = calculate_event_probability(lang, event, type, event_languages)
			if event_probability > threshold:
				recommended_pages[lang].append(event)

"""

languages = ["fr", "da", "sv", "nb", "nl", "de", "is"]
event_type_distributions = utils.read_from_json("resources/event_distributions.json")
language_links = utils.read_from_json("resources/language_links.json")

def get_events_from_type():
	events_query = """
		SELECT ?subtype ?subtypeLabel ?type ?typeLabel #(COUNT(?x) AS ?cnt)
		WHERE
		{
			?type wdt:P279 wd:Q1656682 .
			?subtype wdt:P31 ?type .
			SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
		} 

		"""

	events_in_type = defaultdict(lambda: [])
	result = utils.query_wikidata(events_query)

	subtypes = result["subtype.value"]
	EVENT_type = result["type.value"]

	for t, st in zip(EVENT_type,subtypes):
		t = t.split("/")[-1]
		st = st.split("/")[-1]
		events_in_type[t].append(st)
	utils.save2json(events_in_type, "resources/events_in_type.json")
	return events_in_type


def get_languages_with_event(event):
	languages_with_event_query = """
		SELECT DISTINCT ?language 
		WHERE {
		    ?sitelink schema:about %s .
			?sitelink schema:inLanguage ?language .
		    ?sitelink schema:isPartOf [ wikibase:wikiGroup "wikipedia" ] .
		}
		"""
	q = "wd:"+event
	result = utils.query_wikidata(languages_with_event_query % q)

	if result.empty == True: return []
	languages_with_event = [x for x in result["language.value"]]
	return languages_with_event
	
def calculate_event_probability(event, event_type, language, languages_with_event):

	try:
		event_type_prob = event_type_distributions[language][event_type]
	except KeyError:
		event_type_prob = 0 # --> maybe add smoothing here

	event_language_sum = event_type_prob

	for l1 in language_links[language]:
		if l1 in languages_with_event:
			language_link_prob = language_links[language][l1]
		else:
			language_link_prob = 0
		event_language_sum += language_link_prob
	
	if event_language_sum > 0.10:
		print("language", language)
		print("event", event)
		print("event type", event_type)
		print("sum", event_language_sum)
		print("etp", event_type_prob)
		print("llp", language_link_prob)

def get_recommendations():
	#events = get_events_from_type()
	events = utils.read_from_json("resources/events_in_type.json")

	for event_type in events:
		for event in events[event_type]:
			# get list of languages with that event
			languages_with_event = get_languages_with_event(event)
			if len(languages_with_event) == 0: continue
			for language in languages:
				if language in languages_with_event: continue
				else: 
					event_probability = calculate_event_probability(event, event_type, language, languages_with_event) 


if __name__ == "__main__":
	get_recommendations()
