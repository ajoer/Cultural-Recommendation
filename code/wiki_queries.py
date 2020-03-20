# queries:


# ---------- RECOMMENDATION -----------
# Get events per type and subtype:
events_query = """ 
SELECT ?subtype ?subtypeLabel ?type ?typeLabel #(COUNT(?x) AS ?cnt)
WHERE
{
	?type wdt:P279 wd:Q1656682 .
	?subtype wdt:P31 ?type .
	SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
} 
"""

# Get list of languages that have the event
languages_with_event_query = """
SELECT DISTINCT ?lang 
WHERE {
    ?sitelink schema:about wd:Q45578 .
	?sitelink schema:inLanguage ?lang .
    ?sitelink schema:isPartOf [ wikibase:wikiGroup "wikipedia" ] .
}
"""



# ---------- GET PRIORS -----------
# Get event types:

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





# BELOW IS NOT USED YET




all_languages = """
SELECT ?l 
WHERE
{
	?l wdt:P31/wdt:P279 wd:P424 .
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


US_presidential_elections_events_query = """
SELECT ?event ?eventLabel ?lang
WHERE
{
	?event wdt:P31 wd:Q47566 .
    ?sitelink schema:about ?event .
	?sitelink schema:inLanguage ?lang .
	SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
} 
GROUP BY ?event ?eventLabel ?lang
"""

languages_with_event_query = """
SELECT DISTINCT ?lang 
WHERE {
    ?sitelink schema:about wd:Q45578 .
	?sitelink schema:inLanguage ?lang .
    ?sitelink schema:isPartOf [ wikibase:wikiGroup "wikipedia" ] .
}
"""

event_type_query = """
SELECT ?eventType ?eventTypeLabel
WHERE
{
	"%s" wdt:P31 ?eventType .
 	?eventType wdt:P279* wd:Q1656682 .
	SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }

}
"""