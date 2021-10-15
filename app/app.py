import dash
from dash import html as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from datetime import datetime
from os.path import isfile
import plotly.express as px

app = dash.Dash(__name__)


#COPIED HERE CODE FROM READ_VACCINATION_DATA FOR DEBUGGING PURPOSE

####################################################################


app.layout = html.Div(children=[
    html.H1(children='Vaccination and Air traffic: the thin line between skies and covid.'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    #HERE WE CREATE THE TABLE WITH THE DATA FROM THE VACCINATION

])


server = app.server

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")