import pandas as pd
import vincent as vince
from pandasql import sqldf
import matplotlib.pyplot as plt
import numpy as np
import json
import csv


freq_data = pd.read_csv('freq_data.csv',delimiter=',')
pysqldf = lambda q: sqldf(q, globals())

## use pandas dataframe to create Vincent frequency histogram vizualization to be passed to Vega later.
q =  """SELECT * FROM freq_data ORDER BY frequency DESC LIMIT 20;"""
viz_data = pysqldf(q)
vis = vince.Bar(viz_data, columns = ['frequency'], key_on='word',height=400)
vis.axes[0].properties = vince.AxisProperties(labels=vince.PropertySet(angle=vince.ValueRef(value=45),align=vince.ValueRef(value='left')))
#vis.padding['bottom'] = 90
vis.axis_titles(y='Frequency (%)', x='Word')
vis.legend('20 Most Frequent Words in Tweets (%)')
vis.to_json('vega.json')
vis.colors(brew = 'RdPu')
words = viz_data['word']
frequency = viz_data['frequency']

##create matplotlib frequency histogram
ind = np.arange(20)  # the x locations for the groups
width = 0.5
fig, ax = plt.subplots()
rects1 = ax.bar(ind, frequency, width, color='#98FB98')
ax.set_ylabel('(%) Frequency')
ax.set_xticks(ind+width)
ax.set_xticklabels(words)
ax.set_title('20 Most Frequent Words in Tweets (%)')
plt.show()

## Create Mapping Viz

#Map the county codes we have in our geometry to those in the
#county_data file, which contains additional rows we don't need
with open('us_states.topo.json', 'r') as f:
    get_id = json.load(f)

#A little Data Munging that isnt actually that neccesary :)
new_geoms = []
for geom in get_id['objects']['us_states.geo']['geometries']:
    geom['properties']['NAME'] = str(geom['properties']['NAME'])
    new_geoms.append(geom)

get_id['objects']['us_states.geo']['geometries'] = new_geoms

with open('us_states.topo.json', 'w') as f:
    json.dump(get_id, f)

#Grab the State Names and load them into a dataframe, also not neccesary but good practice :)
geometries = get_id['objects']['us_states.geo']['geometries']
state_names = [x['properties']['NAME'] for x in geometries]
state_df = pd.DataFrame({'NAME': state_names}, dtype=str)


#Read into Dataframe, cast to string for consistency
df = pd.read_csv('state_data.csv',delimiter=',')
df['NAME'] = df['State'].astype(str)

#Perform an inner join, pad NA's with data from nearest county
merged = pd.merge(df, state_df, on='NAME', how='inner')
merged = merged.fillna(method='pad')
state_topo = r'us_states.topo.json'
geo_data = [{'name': 'states',
             'url': state_topo,
             'feature': 'us_states.geo'}]

#create Map of states color coded based upon mean tweet sentiment
vis = vince.Map(data=merged, geo_data=geo_data, scale=1100, projection='albersUsa',
          data_bind='Mean Sentiment', data_key='NAME',
          map_key={'states': 'properties.NAME'})
vis.marks[0].properties.enter.stroke_opacity = vince.ValueRef(value=0.5)
vis.rebind(column='Mean Sentiment', brew='YlGnBu')
vis.scales['color'].type = 'threshold'
vis.scales['color'].domain = [-1.0,-0.48, 0.04, 0.56, 1.08, 1.6, 2.11]
vis.legend(title = 'States by Mean Sentiment')
vis.to_json('vega_state_map.json')
