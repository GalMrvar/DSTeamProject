import requests
import json
import pandas as pd

url = "https://api.covid19api.com/total/country/south-africa/status/confirmed"


def callApi(url):
    payload={}
    headers = {}

    return requests.request("GET", url, headers=headers, data=payload)

germany = callApi("https://api.covid19api.com/total/country/germany/status/confirmed")
print(germany.text)