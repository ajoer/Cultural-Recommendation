# Cultural Recommendation

This repository contains code to determine the cultural relevance of a not-yet-created Wikipedia page. It can be used to suggest new pages to language versions based on the estimated cultural relevance of the topic. 

The repository is still work in progress and does not yet reach usable results.

The code is open source and free to use under the MIT license.

## Repository overview

The repository has two subdirectories [code](https://github.com/ajoer/Cultural-Recommendation/tree/master/code) and [resources](https://github.com/ajoer/Cultural-Recommendation/tree/master/resources).

**[Code](https://github.com/ajoer/Cultural-Recommendation/tree/master/code)**

* [get_priors.py](https://github.com/ajoer/Cultural-Recommendation/blob/master/code/get_priors.py) gets the prior probabilities for event type and language links by querying Wikidata using SPARQL

* [make_dataset.py](https://github.com/ajoer/Cultural-Recommendation/blob/master/code/make_dataset.py) creates a dataset of events with the probability of an event being culturally relevant for a language version.

* [train.py](https://github.com/ajoer/Cultural-Recommendation/blob/master/code/train.py) trains a machine learning algorithm for predicting cultural relevance of each event for a language version (currently sklearn's SVM).

* [utils.py](https://github.com/ajoer/Cultural-Recommendation/blob/master/code/utils.py) contains the general utilities used in the project.

* [wiki_queries.txt](https://github.com/ajoer/Cultural-Recommendation/blob/master/code/wiki_queries.txt) contains the SPARQL queries used to query Wikidata in the project.

**[Resources](https://github.com/ajoer/Cultural-Recommendation/tree/master/resources)**

This subdirectory contains different JSON files with probabilities and other resource files. 

* [event_distributions.json](https://github.com/ajoer/Cultural-Recommendation/blob/master/resources/event_distributions.json) contains the distribution of events per language version (the prior probability of an event given a language, P( e | l ).

* [events.json](https://github.com/ajoer/Cultural-Recommendation/blob/master/resources/events.json) contains a dictionary of event classes with a list of events in that event class as value.

* [language_links.json](https://github.com/ajoer/Cultural-Recommendation/blob/master/resources/language_links.json) contains the probability of two languages having a page in common. The probability is unique to the query language, as the probabilities for each language are normalized and sum to one. P(Danish-German link | Danish links).

* [languages_with_events.json](https://github.com/ajoer/Cultural-Recommendation/blob/master/resources/languages_with_events.json) is a dictionary of events with a list of Wikipedia language versions that have that event. 

* [wikipedia_LVs.txt](https://github.com/ajoer/Cultural-Recommendation/blob/master/resources/wikipedia_LVs.txt) contains all language codes of the Wikipedia language versions.

* [wikipedia_LVs_stats.tsv](https://github.com/ajoer/Cultural-Recommendation/blob/master/resources/wikipedia_LVs_stats.tsv) contains an overview of statistics for each Wikipedia language versions.

## Acknowledgements
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 812997