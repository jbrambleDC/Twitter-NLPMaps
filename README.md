Twitter-NLPMaps
===============

Tokenize tweets to determine net sentiments and locations, generate Viz for states mean sentiment
for background on this data science study read this : https://medium.com/@JBramVB/mapping-happiness-with-twitter-natural-language-processing-ac231e70fe7

In order to Run: First download a shapefile for US states and provinces, package into the repository: http://www.naturalearthdata.com/downloads/

You must also download all of the requirements listed in import statements. Then you need a sample of tweets. This current code is set to read in a json filed called EnTweets.json which I did not host because it is far too large. The Best way to curate tweets is to use the Twitter Sample API, which gives a large random sample, and curate them into a .json file. Let your scraper run for 5-10 minutes in order to curate enough Data. I initially curated ~53,000 Tweets, and then decided to filter down to English language only, yielding ~23,000 Tweets. Of these, I was able to score and locate > 10%.

I elected not to seperate the analysis stage into multiple files because I conducted this study in the following way:

1. Data Curation
2. Data Wrangling/Munging/Cleaning
3. Data Analysis
4. Visualization and Insight

After installing all dependencies, the next step is to run the tweet_sentiment.py file on your json data, keep in mind no database is used, and algorithms are not always optimized, so it may take 10-30 minutes to run if you are analyzing more than 50,000 tweets. This file will do the following:

1. Tokenize each tweet and determine a net sentiment.
2. Determine a very naive "learned sentiment" for words not in the sentiment dictionary and tally a running average over time.
3. Attempt to Determine a location for tweets by running a Point in Polygon Ray Casting algorithm on a shapefile and tweet coordinates if possible. If not possible, determine a location from the "Place" and "User""Location" fields.
4. Perform descriptive statistical analysis on the resulting data, to determine central tendencies and variances.
5. Write all the resulting data to .csv files and tweets to .json.

After the resulting data has been generated, you must do $ sudo pip install vincent, and then also get Vega( a .js visualization package). Getting Vega is not a trivial operation however. Fortunately I've written code that will generate a histogram in Vincent/Vega as well as in matplotlib. However, the mapping visualizations are generated exclusively in Vincent.

The first step to improving upon this, is to use a much better open source sentiment dictionary, the one I am currently using I got for free from a coursera.org Data Science course. Algorithm efficiency as well, as storing Data in a database that optimizes reads is a neccesity as well.
