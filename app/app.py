import dash
from sqlalchemy import create_engine
from dash import html as html
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime
from os.path import isfile
import plotly.express as px
from dash import dash_table
import read_vaccination_data
import read_aviation_data
import read_from_api
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
db_conn = create_engine("postgresql://username:secret@db:5432/database")

app.logger.info(db_conn.connect())

#data frames for aviation data
testdf2 = pd.read_sql_query('SELECT * FROM aviation',db_conn)
df_1 = testdf2.filter(['Entity','Day','Flights'], axis=1)
df_2 = testdf2.filter(['Entity','Day 2019', 'Flights 2019 (Reference)'], axis=1)
df_2["Day 2019"]= pd.to_datetime(df_2["Day 2019"])
df_1.rename(columns={'Entity':'Country'}, inplace=True)
df_2.rename(columns={'Entity':'Country', 'Day 2019': 'Day', 'Flights 2019 (Reference)': 'Flights'}, inplace=True)

df_1 = df_1.append(df_2)
df_1 = df_1.sort_values(by=['Day'])
df_1['Year'] = df_1['Day'].dt.year
df_1['Month'] = df_1['Day'].dt.month

df_1['Day_MM_DD'] = df_1['Day'].dt.strftime('%d-%m')
df_ger = df_1[df_1['Country']=='Germany']
df_ger_2019 = df_ger[df_ger['Year']==2019]
df_ger_2019 = df_ger_2019.drop_duplicates()
df_ger_2020 = df_ger[df_ger['Year']==2020]
df_ger_2021 = df_ger[df_ger['Year']==2021]
df_che = df_1[df_1['Country']=='Switzerland']
df_che_2019 = df_che[df_che['Year']==2019]
df_che_2019 = df_che_2019.drop_duplicates()
df_che_2020 = df_che[df_che['Year']==2020]
df_che_2021 = df_che[df_che['Year']==2021]
df_isr = df_1[df_1['Country']=='Israel']
df_isr_2019 = df_isr[df_isr['Year']==2019]
df_isr_2019 = df_isr_2019.drop_duplicates()
df_isr_2020 = df_isr[df_isr['Year']==2020]
df_isr_2021 = df_isr[df_isr['Year']==2021]


# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}


#BETÜL COMMENTS:
    #Had to change here 'FormGroup' to 'CardGroup' for the template to run
controls = dbc.CardGroup(
    [
#BETÜL COMMENTS:
    #Had to delete 'block=True' here, cause it threw an exception that the attribute 'block' didn't exist
    ]
)

sidebar = html.Div(
    [
        html.H2('Parameters', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)
content_intro_row = dbc.Row(
    dbc.Col(
        dbc.Card([
            dbc.CardBody(
                [
                    html.H4(id='card_title_intro', children=['Click on the tab for the content. Thanks!'], className='card-title-intro',
                            style=CARD_TEXT_STYLE),
                    html.P(id='card_text_intro', children=['We need to decide if we want to have a homepage thingy or if we want to show the first tab on page load. WHAT COMES HERE???'], style=CARD_TEXT_STYLE),
                ]
            )
        ])
    )
)
content_descr_row = dbc.Row([
    dbc.Col(
        dbc.Card([
            dbc.CardBody(
                [
                    html.H4(id='card_title_1', children=['Card Title 1'], className='card-title',
                            style=CARD_TEXT_STYLE),
                    html.P(id='card_text_1', children=['Sample text.'], style=CARD_TEXT_STYLE),
                ]
            )
        ]),
        md=6
    ),
    dbc.Col(
        dbc.Card([
            dbc.CardBody(
                [
                    html.H4('Card Title 2', className='card-title', style=CARD_TEXT_STYLE),
                    html.P('Sample text.', style=CARD_TEXT_STYLE),
                ]
            ),
        ]),
        md=6
    ),
])

country_df = pd.read_sql_query('SELECT distinct "Entity" FROM aviation',db_conn)

content_first_row = dbc.Row([
    dbc.Col(
        dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
            dcc.Tab(label='Map', children=[
                content_descr_row,
                dcc.Graph(id='graph_4')
            ]),
            dcc.Tab(label='Just flights', children=[
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[
                        {"label": row[0], "value": row[0]}
                        for index, row in country_df.iterrows()
                    ],
                    value=['Germany'],  # default value
                    multi=False
                ),
                dcc.Graph(id='graph_1', style={'display': 'none'}),
                dcc.Graph(id='graph_2', style={'display': 'none'}),
                dcc.Graph(id='graph_3', style={'display': 'none'})
            ]),
            dcc.Tab(label='Covid vs flights', children=[
                #dcc.Graph(id='graph_3'),
                dcc.Graph(id='graph_5')
            ]),
        ])
    )
])

content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1'), md=4
        ),
        dbc.Col(
            dcc.Graph(id='graph_2'), md=4
        ),
        dbc.Col(
            dcc.Graph(id='graph_3'), md=4
        )
    ]
)

content_third_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_4'), md=12,
        )
    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_5'), md=6
        ),
        dbc.Col(
            dcc.Graph(id='graph_6'), md=6
        )
    ]
)

content = html.Div(
    [
        html.H2('Analytics Dashboard Template', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_intro_row,
        #content_second_row,
        #content_third_row,
        #content_fourth_row
    ],
    style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])

@app.callback(Output('tabs-content-example-graph', 'children'),
              [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),
     State('radio_items', 'value')
     ])
def render_content(tab):
    if tab == 'tab-1-example-graph':
        return html.Div(
            content_third_row
        )
    elif tab == 'tab-2-example-graph':   
        return html.Div(
            content_fourth_row
        )
    elif tab == 'tab-3-example-graph':   
        return html.Div(
            content_second_row
        )

@app.callback(
    Output('graph_1', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),
     State('radio_items', 'value')
     ])
def update_graph_1(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
    print(n_clicks)
    print(dropdown_value)
    print(range_slider_value)
    print(check_list_value)
    print(radio_items_value)
    
    #fig = px.line(df_ger_2019, x="Day", y="Flights", color="Year")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_che_2019.Day, y=df_che_2019.Flights, name='2019',
                        line = dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=df_che_2019.Day, y=df_che_2020.Flights, name='2020',
                        line = dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=df_che_2019.Day, y=df_che_2021.Flights, name='2021',
                        line=dict(color='green', width=2)))
    fig.update_xaxes(dtick="M1", tickformat="%d %B")
    fig.update_layout(title='Switzerland',
                   xaxis_title='Month',
                   yaxis_title='Flights per day')
    return fig


@app.callback(
    Output('graph_2', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),
     State('radio_items', 'value')
     ])
def update_graph_2(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
    print(n_clicks)
    print(dropdown_value)
    print(range_slider_value)
    print(check_list_value)
    print(radio_items_value)

    #fig = px.line(df_ger, x="Day", y="Flights", color='Year', title='Germany')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ger_2019.Day, y=df_ger_2019.Flights, name='2019',
                        line = dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=df_ger_2019.Day, y=df_ger_2020.Flights, name='2020',
                        line = dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=df_ger_2019.Day, y=df_ger_2021.Flights, name='2021',
                        line=dict(color='green', width=2)))
    fig.update_xaxes(dtick="M1", tickformat="%d %B")
    fig.update_layout(title='Germany',
                   xaxis_title='Month',
                   yaxis_title='Flights per day')
    return fig


@app.callback(
    Output('graph_3', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),
     State('radio_items', 'value')
     ])
def update_graph_3(n_clicks, dropdown_value, range_slider_value, check_list_value, radio_items_value):
    print(n_clicks)
    print(dropdown_value)
    print(range_slider_value)
    print(check_list_value)
    print(radio_items_value)
    
    #fig = px.line(df_isr, x="Day", y="Flights", color='Year',title='Israel')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_isr_2019.Day, y=df_isr_2019.Flights, name='2019',
                        line = dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=df_isr_2019.Day, y=df_isr_2020.Flights, name='2020',
                        line = dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=df_isr_2019.Day, y=df_isr_2021.Flights, name='2021',
                        line=dict(color='green', width=2)))
    fig.update_xaxes(dtick="M1", tickformat="%d %B")
    fig.update_layout(title='Israel',
                   xaxis_title='Month',
                   yaxis_title='Flights per day')
    return fig

@app.callback(
    Output("graph_1", "style"),
    [
        Input("country-dropdown", "value")
    ],
)

def update_chart_germany(country):
    if country == "Germany":
        return {'display':'inline'}
    else :
        return {'display':'none'}

@app.callback(
    Output("graph_2", "style"),
    [
        Input("country-dropdown", "value")
    ],
)

def update_chart_switzerland(country):
    if country == "Switzerland":
        return {'display':'inline'}
    else :
        return {'display':'none'}

@app.callback(
    Output("graph_3", "style"),
    [
        Input("country-dropdown", "value")
    ],
)

def update_chart_israel(country):
    if country == "Israel":
        return {'display':'inline'}
    else :
        return {'display':'none'}

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")