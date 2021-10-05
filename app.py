from flask import Flask
from flask import render_template,request,url_for,redirect
from google.cloud import bigquery
import plotly
import plotly.graph_objects as go
import json

app = Flask(__name__)
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

@app.route('/')
def home():
    message = "Welcome, you are at the home page"
    return render_template('page.html', welcome=message)
    

# define row in the solar potential table
class Item(object):
    def __init__(self, state_name, avg_potential,avg_actual):
        self.state_name = state_name
        self.avg_potential = avg_potential
        self.avg_actual = avg_actual
        self.room_for_growth = round(100*(1-self.avg_actual/self.avg_potential),2)

@app.route('/solarpotential')
def solarpotential():
    #Perform a query
    QUERY = (
        'SELECT state_name, AVG(percent_qualified) as state_potential, AVG(percent_covered) as state_covered, AVG(lat_avg) as state_lat, AVG(lng_avg) as state_long '
        'FROM `bigquery-public-data.sunroof_solar.solar_potential_by_postal_code` '
        'WHERE percent_covered <= 100 AND percent_qualified<=100 '        
        'GROUP BY state_name '
        'ORDER BY state_potential DESC'
        )
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    # print(rows)
    # result = 
    states=[]
    table = []
    for row in rows:
        states.append(row.state_name)
        state_potential = round(row.state_potential,2)
        state_covered=round(row.state_covered,2)
        item =Item(row.state_name,state_potential,state_covered)
        print(item)
        table.append(item)
    print(states)
    return render_template('solarpotential.html',table=table)

class zipcodeItem(object):
    def __init__(self, state_name, zipcode,existing_installs_count,kw_median,kw_total,number_of_panels_median,number_of_panels_total):
        self.state_name = state_name
        self.zipcode = zipcode
        self.existing_installs_count = existing_installs_count
        self.kw_median = kw_median
        self.kw_total = kw_total
        self.percent_rooftopKW_utilized = existing_installs_count*kw_median/kw_total if existing_installs_count!=0 else 0
        self.number_of_panels_median = number_of_panels_median
        self.number_of_panels_total = number_of_panels_total
        self.percent_panels_used = number_of_panels_total/number_of_panels_total
        
@app.route('/bystate/<state>')
def bystate(state):
    QUERY = (
        'SELECT state_name,region_name,lat_avg,lng_avg,carbon_offset_metric_tons,'
        'yearly_sunlight_kwh_median,yearly_sunlight_kwh_total,number_of_panels_total,'
        'number_of_panels_median,kw_median,kw_total,existing_installs_count '
        'FROM `bigquery-public-data.sunroof_solar.solar_potential_by_postal_code` '
        'WHERE state_name="%s" AND kw_median IS NOT NULL'%state
    )  
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    table = []
    for row in rows:
        table.append(zipcodeItem(row.state_name,row.region_name,
        row.existing_installs_count,row.kw_median,row.kw_total,
        row.number_of_panels_median,row.number_of_panels_total))
    return render_template("bystate.html",state=state,table=table)

@app.route('/lookupstate', methods=['POST','GET'])
def lookupstate():
    if request.method =="POST":
        state_name= request.form['state']
        return redirect(url_for('bystate',state=state_name))
    # else:
    #     state_name= request.args.get('state')
    #     return redirect(url_for('bystate',state=state_name))
    return render_template('lookupstate.html')


@app.route('/carbonreduction')
def carbonreduction():
    QUERY = ( 
    'SELECT state_name,AVG(lat_avg) as state_lat,AVG(lng_avg) as state_long,AVG(carbon_offset_metric_tons) as avg_carbon '
    'FROM `bigquery-public-data.sunroof_solar.solar_potential_by_postal_code` '
    'WHERE state_name NOT IN("Aguadilla","Cataño","Arecibo","Baja California","Bayamón","Canóvanas","Carolina","Corozal","Dorado","Guaynabo","Hormigueros","Mayagüez","Moca","Ponce","San Juan","Toa Alta","Toa Baja","Trujillo Alto") '
    'GROUP BY state_name '
    )

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
        title_text='Average Carbon Reduction from Solar Energy by State in the U.S. (not including Puerto Rico)',
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='white'
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('carbon.html',graphJSON=graphJSON)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
