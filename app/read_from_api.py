import requests
import json
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, time, timedelta
import uuid
from sqlalchemy import create_engine, inspect, Table

db_conn = create_engine("postgresql://username:secret@db:5432/database")

def callApi(url):
    payload={}
    headers = {}
    return requests.request("GET", url, headers=headers, data=payload)

def readFromJsonToPdCountry(response):
    pd_response = pd.read_json(json.dumps(response.json()), convert_dates=['Date'])
    pd_modified = pd_response[["Country", "CountryCode", "Cases", "Date"]] #active & recovered as well?
    
    pd_modified = pd_modified.astype({"Cases" : 'int64'})
    
    #sum specific regions from the whole country by date field
    aggregated_pd = pd_modified.groupby(pd_modified['Date']).sum()
    aggregated_pd["Country"] = pd_modified['Country'].values[0]
    aggregated_pd["CountryCode"] = pd_modified['CountryCode'].values[0]
    #aggregated_pd["ID"] = pd_modified['ID'].values[:len(aggregated_pd.index)]
    aggregated_pd["Date"] = aggregated_pd.index
    aggregated_pd['ID'] = [uuid.uuid4() for _ in range(len(aggregated_pd.index))]
    aggregated_pd = aggregated_pd.set_index('ID')
        
    #substract from previous dates to get values per each day
    aggregated_pd["Cases"] = aggregated_pd.Cases.diff()
    
    #dropping na values and return (na is always going to be the first value in list) that's why we specify datetime - 2
    return aggregated_pd.dropna()
    
def processDataFromApi(dateFrom, newTable):
    if(dateFrom is not None):
        dateFrom = dateFrom - timedelta(2)
    else:
        dateFrom = datetime.today() - timedelta(2)
    #edit dateTime var
    dateFrom = datetime.combine(dateFrom, time(0, 0, 0, 0)).strftime("%Y-%m-%dT%H:%M:%SZ")
    today = datetime.combine(datetime.today(), time(0, 0, 0, 0)).strftime("%Y-%m-%dT%H:%M:%SZ")
    germany_api = callApi("https://api.covid19api.com/country/germany/status/confirmed?from="+dateFrom+"&to="+today)
    pd_germany = readFromJsonToPdCountry(germany_api)
    
    switzerland_api = callApi("https://api.covid19api.com/country/switzerland/status/confirmed?from="+dateFrom+"&to="+today)
    pd_switzerland = readFromJsonToPdCountry(switzerland_api)

    israel_api = callApi("https://api.covid19api.com/country/israel/status/confirmed?from="+dateFrom+"&to="+today)
    pd_israel = readFromJsonToPdCountry(israel_api)
    
    ##group them all together:
    pd_all_countries = pd_germany.append(pd_switzerland)
    pd_all_countries = pd_all_countries.append(pd_israel)
    
    if(newTable):
        pd_all_countries.to_sql('apiCases', db_conn, if_exists='replace')
    else:
        #create temp table
        pd_all_countries.to_sql('tmp_apiCases', db_conn, if_exists='replace')
        #remove all values that match the temp table (from the original table)
        sql = """
                delete from "apiCases" t1 where "Date" in (select "Date" from "tmp_apiCases" t2 WHERE t1."Country" = t2."Country")
            """
        db_conn.execute(sql)
        #then append cases to the original table
        pd_all_countries.to_sql('apiCases', db_conn, if_exists='append')
        #print(pd.read_sql_query('SELECT * FROM "apiCases"',db_conn))
        
if(inspect(db_conn).has_table("apiCases")):
    #old table add update and append missing values
    date = pd.read_sql_query('SELECT MAX("Date") FROM "apiCases" WHERE "Cases" > 0 ',db_conn)
    date = pd.to_datetime(date["max"])
    processDataFromApi(date.iloc[0], False)
else:
    #new table add 
    dateFrom = datetime(2020, 1, 1)
    processDataFromApi(dateFrom, True)
