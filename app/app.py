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

app = dash.Dash(__name__)

db_conn = create_engine("postgresql://username:secret@db:5432/database")

app.logger.info(db_conn.connect())
df = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), columns=['a', 'b', 'c'])
df.to_sql('test', db_conn, if_exists='replace')
df2 = pd.read_sql_query('SELECT a FROM test',db_conn)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df2.columns],
    data=df.to_dict('records'),
)

server = app.server

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")