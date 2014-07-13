import sys
import json
import nltk
import enchant
from nltk.corpus import wordnet
import shapefile
import csv
import numpy
from scipy import stats


#output to data structure
#store tweets and their sentiment, get location for tweet, dict of location and a list of sentiments,

freq_dict = {}
polygon = shapefile.Reader("ne_110m_admin_1_states_provinces/ne_110m_admin_1_states_provinces_shp.shp")
states_names = []
state_acronym = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District Of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

#builds dictionary of 5000 most populated cities, that matches to their state acronym
def build_cities_dict():
  cities_states_dict = {}
  with open('Top5000Population.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',', quoting=csv.QUOTE_NONE)
    for row in reader:
      if row[0].lower().strip() in cities_states_dict.keys():
        pass
      else:
        cities_states_dict[row[0].lower().strip()] = row[1].upper().strip()
  return cities_states_dict


#list of state names
def build_states_list(states_acronyms_dict, empty_list):
  #pass in states_acronyms dict
  dict = states_acronyms_dict
  for key in dict.keys():
    empty_list.append(dict[key].lower().strip())
  return empty_list

#Sentiment Dictionary
def build_dict():
  afinnfile = open("AFINN-111.txt")
  scores = {} # initialize an empty dictionary
  #scores_tuples = [line.decode('utf-8').split('\t') for line in afinnline]
  #scores = dict((a,int(b)) for a,b in scores_tuples)
  for line in afinnfile:
    term, score  = line.decode('utf-8').split("\t")  # The file is tab-delimited. "\t" means "tab character"
    scores[term] = int(score)  # Convert the score to an integer.

  return scores

def analyze_tweets(nlp_dict):
  print "analyzing tweets"
  file = open("enTweets.json")
  term_sents = {}
  total_terms = 0
  scored_tweets = []
  #break up a tweet into tokens, and determine net sentiment of tweet.
  for line in file:
    tweet = json.loads(line)
    if "text" in tweet and tweet["lang"] == "en":
      score = 0
      terms = 0
      tweet_data = tweet["text"].encode('utf-8')
      tokenized_tweet = nltk.word_tokenize(tweet_data)
      terms, score = det_sent(tokenized_tweet,nlp_dict,term_sents)
      t = [tweet, score, terms]
      scored_tweets.append(t)

  with open('freq_data.csv', 'wb') as csvfile1:
    freq_writer = csv.writer(csvfile1, delimiter=',')
    freq_writer.writerow(["word","frequency"])
    for key in freq_dict.keys():
      total_terms += freq_dict[key]
    for key in freq_dict.keys():
      freq_dict[key] = float(freq_dict[key])/float(total_terms)
      freq_writer.writerow([key,str(freq_dict[key]*100)])

  with open('learned_sentiments.csv','wb') as sentcsv:
    sent_writer = csv.writer(sentcsv,delimiter=',')
    sent_writer.writerow(["word","score"])
    for key in term_sents.keys():
      sent_writer.writerow([key,str(term_sents[key][0])])

  file.close()
  return scored_tweets

def det_location(tweets, shp_file, states_acronyms, state_names, cities_dict):
  print "determining location of tweets"
  located_tweets =[]
  #determine a location for scored tweets if possible.
  for i in tweets:
    curr_tweet = i[0]

    if curr_tweet["coordinates"]: #first use a shapefile and PIP algorithm to determine state name
      coords = curr_tweet["coordinates"]["coordinates"]
      lon_coord = coords[0]
      lat_coord = coords[1]
      for record in shp_file.shapeRecords():
        #print record.record[12]
        if point_in_poly(lon_coord,lat_coord,record.shape.points) == "IN":
          i.append(record.record[12])
          break

    if curr_tweet["place"] != None and len(i) < 4: #use cities, and state names dictionaries to locate based on state field
      #need rule for washington
      #concat word list, with spaces and check that stripped and lowered.
      location_helper(i,"place","name",states_acronyms,state_names)
      if len(i) < 4 and curr_tweet["place"]["place_type"] == "city":
        if curr_tweet["place"]["name"].encode('utf-8').lower().strip() in cities_dict.keys():
          i.append(states_acronyms[cities_dict[curr_tweet["place"]["name"].encode('utf-8').lower().strip()]])

    elif curr_tweet["user"]["location"] != None and len(i) < 4: #use manually entered user data to determine a location
      location_helper(i,"user","location",states_acronyms,state_names)
      if len(i) < 4:
        if curr_tweet["user"]["location"].encode('utf-8').lower().strip() in cities_dict.keys():
          i.append(states_acronyms[cities_dict[curr_tweet["user"]["location"].encode('utf-8').lower().strip()]])

    if len(i) > 3:
      located_tweets.append(i)

  return located_tweets

def location_helper(tweet,field_1,field_2,acronyms,states):
  curr_tweet = tweet[0]
  word_list = nltk.word_tokenize(curr_tweet[field_1][field_2])
  for word in word_list:
    if word.upper().strip() in acronyms.keys():
      tweet.append(acronyms[word.upper().strip()])
      break
    elif word.lower().strip() in states and word != "washington":
      tweet.append(word.lower().strip().title())
      break
    if word == "washington":
      if "DC" in word_list:
        tweet.append(acronyms['DC'])
      else:
        tweet.append(acronyms['WA'])
    else:
      maybe_state =''
      for i in word_list:
        maybe_state += (i + ' ')
      if maybe_state.lower().strip() in states:
        tweet.append(maybe_state.lower().strip().title())

def det_sent(tweet, dict, sents_dict): #helper method for determining net sentiment, will use the sentiment score to appply scores to unscored words.
  terms_count = 0
  score = 0
  d = enchant.Dict("en_US")
  residual_words = []
  for word in tweet:
    stripped_word = word.lower().strip().replace('.','').replace('?','').replace('!','')
    if stripped_word.decode('utf-8') in dict.keys():
      terms_count += 1
      score += dict[stripped_word]
      freq_histogram(stripped_word, freq_dict)
    else:
      residual_words.append(stripped_word)

  for word in residual_words:
    if len(word) > 3:
      if d.check(word):
        if word in sents_dict.keys() and terms_count > 0:
          curr_score = float(sents_dict[word][0])
          curr_terms= float(sents_dict[word][1])
          sents_dict[word][0] = (curr_score*curr_terms + float(score))/(curr_terms + float(terms_count))
          sents_dict[word][1] = sents_dict[word][1] + terms_count
        else:
          fin_score = 0
          if terms_count > 0:
            fin_score = float(score)/float(terms_count)
          list = [fin_score,terms_count]
          sents_dict[word] = list


  return terms_count, score


#from collections import Counter
#freq_dict[word] += 1
# no need for if, else
def freq_histogram(word, frequency_dict):
  if word in frequency_dict.keys():
    frequency_dict[word] += 1
  else:
    frequency_dict[word] = 1

def make_plot():
  pass

# Determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs. This function
# returns True if inside poly or False if not.  The algorithm is called
# the "Ray Casting Method".
def point_in_poly(x,y,poly):
   # check if point is a vertex
   #print x,y
   #print poly
   if (x,y) in poly:
      return "IN"

   # check if point is on a boundary
   for i in range(len(poly)):
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
         return "IN"

   n = len(poly)
   inside = False

   p1x,p1y = poly[0]
   for i in range(n+1):
      p2x,p2y = poly[i % n]
      if y > min(p1y,p2y):
         if y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
               if p1y != p2y:
                  xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
               if p1x == p2x or x <= xints:
                  inside = not inside
      p1x,p1y = p2x,p2y

   if inside:
     return "IN"
   else:
     return "OUT"

def happy_states(located_tweets):
  #after tweets are scored and located, determine statistics for each state, output a dictionary of state name keys
  dict = {}
  for tweet in located_tweets:
    sent_n_tweets = []
    if tweet[3] not in dict.keys():
      sent_n_tweets.append(1)
      sent_n_tweets.append(tweet[1])
      sent_n_tweets.append([tweet])
      dict[tweet[3]] = sent_n_tweets
    else:
      dict[tweet[3]][0] +=1
      dict[tweet[3]][1] += tweet[1]
      dict[tweet[3]][2].append(tweet)

  for key in dict.keys():
    scores =[tweet[1] for tweet in dict[key][2]]
    dict[key].append(numpy.std(scores))
    dict[key].append(numpy.median(scores))
    dict[key].append(stats.mode(scores))
    dict[key].append(numpy.amin(scores))
    dict[key].append(numpy.amax(scores))

  return dict

def main():
    state_list = build_states_list(state_acronym,states_names)
    #state_list = state_acronym.values()
    cities_states = build_cities_dict()
    nlpdict = build_dict()
    scoredtweets = analyze_tweets(nlpdict)
    loc_tweets = det_location(scoredtweets, polygon,state_acronym,state_list,cities_states)
    happystates = happy_states(loc_tweets)

    with open('state_data.csv', 'wb') as csvfile:
      writer = csv.writer(csvfile, delimiter=',')
      writer.writerow(["State","Count","Net Sentiment","Mean Sentiment", "St. Dev", "Median","mode","min","max"])
      for key in happystates.keys():
        writer.writerow([key,str(happystates[key][0]),str(happystates[key][1]),\
        str(float(happystates[key][1])/float(happystates[key][0])),\
        str(happystates[key][3]),str(happystates[key][4]),str(happystates[key][5][0][0]),str(happystates[key][6]),str(happystates[key][7])])

    jsonfile = open('final_tweets.json','w')
    for tweet in loc_tweets:
      json_tweet = tweet[0]
      json_tweet["score"] = tweet[1]
      json_tweet["terms"] = tweet[2]
      json_tweet["state_name"] = tweet[3]
      jsonfile.write(json.dumps(json_tweet)+"\n")
    jsonfile.close()
    print "process completed"

if __name__ == '__main__':
    main()

