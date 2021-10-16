import requests
import json
import csv
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def callApi(url):
    payload={}
    headers = {}
    return requests.request("GET", url, headers=headers, data=payload)

def readFromJsonToPd(response):
    pd_response = pd.read_json(json.dumps(response.json()), convert_dates=['Date'])
    pd_modified = pd_response[["Country", "CountryCode", "Confirmed", "Deaths", "Recovered", "Active", "Date"]]

    return pd_modified.astype({"Confirmed" : 'int64', "Deaths" : 'int64', "Recovered" : 'int64', "Active" : 'int64'})


germany_api = callApi("https://api.covid19api.com/total/country/germany")
pd_germany = readFromJsonToPd(germany_api)

switzerland_api = callApi("https://api.covid19api.com/total/country/switzerland")
pd_switzerland = readFromJsonToPd(switzerland_api)

israel_api = callApi("https://api.covid19api.com/total/country/israel")
pd_israel = readFromJsonToPd(israel_api)


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(pd_germany.dtypes)

    
covid_data_processed = [pd_germany, pd_switzerland, pd_israel]
print(type(covid_data_processed))

db_conn = create_engine("postgresql://username:secret@db:5432/database")

df_covid = pd.DataFrame(np.row_stack(covid_data_processed))
df_covid.to_sql('CovidData', db_conn, if_exists='replace')
print(df_covid)
