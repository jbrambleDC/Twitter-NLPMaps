Twitter-NLPMaps
===============

Tokenize tweets to determine net sentiments and locations, generate Viz for states mean sentiment


In order to Run: First download a shapefile for US states and provinces, package into the repository: http://www.naturalearthdata.com/downloads/

You must also download all of the requirements listed in import statements. Then you need a sample of tweets. This current code is set to read in a json filed called EnTweets.json which I did not host because it is far too large. The Best way to curate tweets is to use the Twitter Sample API, which gives a large random sample, and curate them into a .json file. Let your scraper run for 5-10 minutes in order to curate enough Data. I initially curated ~53,000 Tweets, and then decided to filter down to English language only, yielding ~23,000 Tweets. Of these, I was able to score and locate > 10%.
