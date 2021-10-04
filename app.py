from flask import Flask
from flask import render_template
#import mysql.connector
import json
from google.cloud import bigquery

app = Flask(__name__)
client = bigquery.Client(project="kubernetes-docker-327413")

@app.route('/')
def home():
    message = "Welcome, you are at the home page"
    return render_template('page.html', welcome=message)
    

# define row in the Flask API table
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
        'FROM `bigquery-public-data.sunroof_solar.solar_potential_by_censustract` '
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

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)