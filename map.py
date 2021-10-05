import pandas as pd
import plotly.graph_objects as go
from google.cloud import bigquery

client = bigquery.Client(project="kubernetes-docker-327413")

#convert state names to codes in order to format for plotly
state_to_code = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Palau': 'PW',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

QUERY = ( 
    'SELECT state_name,AVG(lat_avg) as state_lat,AVG(lng_avg) as state_long,AVG(carbon_offset_metric_tons) as avg_carbon '
    'FROM `bigquery-public-data.sunroof_solar.solar_potential_by_postal_code` '
    'WHERE state_name NOT IN("Aguadilla","Cataño","Arecibo","Baja California","Bayamón","Canóvanas","Carolina","Corozal","Dorado","Guaynabo","Hormigueros","Mayagüez","Moca","Ponce","San Juan","Toa Alta","Toa Baja","Trujillo Alto") '
    'GROUP BY state_name '
    )

query_job = client.query(QUERY)


statescarbon = (
    client.query(QUERY)
    .result()
    .to_dataframe(
        # Optionally, explicitly request to use the BigQuery Storage API. As of
        # google-cloud-bigquery version 1.26.0 and above, the BigQuery Storage
        # API is used by default.
        create_bqstorage_client=True,
    )
)

statescarbon['state_code'] = [state_to_code[state] for state in statescarbon['state_name']]

#create choropleth using plotly
fig = go.Figure(
    data=go.Choropleth(                     #set graph type
        locations=statescarbon['state_code'],     #Plotly uses abbreviated two-letter postal codes for state 
        z=statescarbon['avg_carbon'],  #set values to map by
        locationmode='USA-states',          #set map that matches locations
        marker_line_color='white',          #set state border color
        colorscale='darkmint',              #set colorbar range
        autocolorscale=False,                     
        colorbar_title='Average Carbon Reduction'))

# #adjust layout settings and preferences, then show the figure
fig.update_layout(
    title_text='Average Carbon Reduction from Solar Energy by State in the U.S. (not including Puerto Rico',
     geo=dict(
         scope='usa',
         projection=go.layout.geo.Projection(type='albers usa'),
         showlakes=True,
         lakecolor='white'
     )
)

fig.show()