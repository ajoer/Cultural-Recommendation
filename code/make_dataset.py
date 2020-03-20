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

languages = sorted(open("resources/wikipedia_LVs.txt").readlines()) #sorted(["fr", "da", "sv", "nb", "nl", "de", "is"]) #
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


def get_languages_with_events(events):
	languages_with_event_query = """
		SELECT DISTINCT ?language 
		WHERE {
		    ?sitelink schema:about %s .
			?sitelink schema:inLanguage ?language .
		    ?sitelink schema:isPartOf [ wikibase:wikiGroup "wikipedia" ] .
		}
		"""

	languages_with_events = {}

	for n,event_type in enumerate(events):
		for event in events[event_type]:

			q = "wd:"+event
			result = utils.query_wikidata(languages_with_event_query % q)

			if result.empty == True: continue 
			languages_with_events[event] = [x for x in result["language.value"]]
			print('languages with events', len(languages_with_events[event]) )

		utils.save2json(languages_with_events, "resources/languages_with_events_%s.json" % n)
	return languages_with_events
	
def make_representation(event_type, qlanguage, languages_with_event):

	# Classification:
	if qlanguage in languages_with_event:
		y = 1
	else:
		y = 0

	representation = []

	# Event type
	try:
		event_type_prob = event_type_distributions[qlanguage][event_type]
	except KeyError:
		event_type_prob = 0 # --> maybe add smoothing here

	representation.append(event_type_prob)

	# Language weight
	for l1 in languages:
		l1 = l1.strip()

		if l1 == qlanguage:
			continue

		# l1 does have the event
		if l1 in languages_with_event:
			exists = 1
		else:
			exists = 0

		# weight 1 is language links
		if l1 in language_links[qlanguage]:

			ll_score = 1+language_links[qlanguage][l1]
		else:
			ll_score = 0+language_links[qlanguage][l1]

		# weight 2 is event type prob in l1:
		try:
			l1_event_type_prob = 1+event_type_distributions[l1][event_type]
		except KeyError:
			l1_event_type_prob = 0+language_links[qlanguage][l1] # --> maybe add smoothing here

		representation.append(exists)
		representation.append(ll_score)
		representation.append(l1_event_type_prob)
	
	return representation, y


def main():

	events = utils.read_from_json("resources/events.json")
	languages_with_events = utils.read_from_json("resources/languages_with_events.json") #get_languages_with_events(events)

	for language in languages:
		language = language.strip("\n")
		if language != "ar": continue
		if language not in language_links: continue

		event_representations = {}

		for event_type in events:
			for event in events[event_type]:
				if event not in languages_with_events: 
					continue

				representation, y = make_representation(event_type, language, languages_with_events[event]) 
				event_rep = {'representation': representation, 'y': y}
				event_representations[event] = event_rep
				if y == 1:
					print(language, event_representations[event])

		utils.save2json(event_representations, "data/data_%s.json" % language)

if __name__ == "__main__":
	main()
