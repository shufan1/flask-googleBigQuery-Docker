from google.cloud import bigquery

client = bigquery.Client()

def test_name():
    #Perform a query
    QUERY = (
        'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` '
        'WHERE state = "NC" '
        'LIMIT 5')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    names = [] 
    for row in rows:
        print(row.name)
        names.append(row.name)
    
    assert names == ['Ruth', 'Lillie', 'Minnie', 'Sallie', 'Janie']

