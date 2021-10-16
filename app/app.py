import dash
from sqlalchemy import create_engine
from dash import html as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from datetime import datetime
from os.path import isfile
import plotly.express as px
from dash import dash_table
#import read_vaccination_data
import read_aviation_data
import read_from_api

app = dash.Dash(__name__)

db_conn = create_engine("postgresql://username:secret@db:5432/database")

app.logger.info(db_conn.connect())

df2 = pd.read_sql_query('SELECT * FROM german_aviation_20',db_conn)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df2.columns],
    data=df2.to_dict('records'),
)

server = app.server

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")