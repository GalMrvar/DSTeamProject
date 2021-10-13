import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from datetime import datetime
from os.path import isfile
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)


#COPIED HERE CODE FROM READ_VACCINATION_DATA FOR DEBUGGING PURPOSE
filepath = "data/covid/owid-covid-data.csv"

rows_to_keep = ['AFG']
vaccination_data = pd.read_csv(filepath,
                               sep=",",
                               header=0,
                               parse_dates= ['date'],
                               usecols=['iso_code','location','date','total_cases','total_vaccinations','people_vaccinated','people_fully_vaccinated','total_boosters','new_vaccinations','new_vaccinations_smoothed','total_vaccinations_per_hundred','people_vaccinated_per_hundred','people_fully_vaccinated_per_hundred','total_boosters_per_hundred','new_vaccinations_smoothed_per_million'])
#filer by country
filtered = vaccination_data[(vaccination_data['iso_code'].isin(['USA','DEU','CHE','ISR']))]
####################################################################


app.layout = html.Div(children=[
    html.H1(children='Vaccination and Air traffic: the thin line between skies and covid.'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    #HERE WE CREATE THE TABLE WITH THE DATA FROM THE VACCINATION
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in filtered.columns],
        data=filtered.to_dict('records'),
    )
])


server = app.server

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")