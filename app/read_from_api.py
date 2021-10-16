import requests
import json
import pandas as pd


def callApi(url):
    payload={}
    headers = {}
    return requests.request("GET", url, headers=headers, data=payload)

def readFromJsonToPd(response):
    pd_response = pd.read_json(json.dumps(response.json()), convert_dates=['Date'])
    pd_modified = pd_response[["ID", "Country", "CountryCode", "Confirmed", "Deaths", "Recovered", "Active", "Date"]]

    return pd_modified.astype({"Confirmed" : 'int64', "Deaths" : 'int64', "Recovered" : 'int64', "Active" : 'int64'})


germany_api = callApi("https://api.covid19api.com/live/country/germany/status/confirmed/date/2020-03-21T13:13:30Z")
pd_germany = readFromJsonToPd(germany_api)

switzerland_api = callApi("https://api.covid19api.com/live/country/switzerland/status/confirmed/date/2020-03-21T13:13:30Z")
pd_switzerland = readFromJsonToPd(switzerland_api)

israel_api = callApi("https://api.covid19api.com/live/country/israel/status/confirmed/date/2020-03-21T13:13:30Z")
pd_israel = readFromJsonToPd(israel_api)

united_states_api = callApi("https://api.covid19api.com/live/country/united-states/status/confirmed/date/2020-03-21T13:13:30Z")
pd_united_states = readFromJsonToPd(united_states_api)

with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(pd_germany.dtypes)

'''with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(pd_germany.dtypes)
    print(pd_switzerland.dtypes)
    print(pd_israel.dtypes)
    print(pd_united_states.dtypes)'''
