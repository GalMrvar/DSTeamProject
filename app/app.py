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
df_1['Day_MM_DD'] = df_1['Day'].dt.strftime('%m-%d')

df_ger = df_1[df_1['Country']=='Germany']
df_che = df_1[df_1['Country']=='Switzerland']
df_isr = df_1[df_1['Country']=='Israel']


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
    '''fig = {
        'data': [{
            'x': testdf2['Day 2019'],
            'y': testdf2['Flights 2019 (Reference)'],
            'type': 'bar'
        }]
    }'''
    fig = px.line(df_che, x="Day", y="Flights", color='Year', title='Switzerland')
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
    
    '''fig = {
        'data': [{
            'x': df_ger.Day,
            'y': df_ger.Flights,
            'type': 'bar'
        }]
    }'''
    fig = px.line(df_ger, x="Day", y="Flights", color='Year', title='Germany')
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
    #df = px.data.iris()
    #fig = px.density_contour(df, x='sepal_width', y='sepal_length')
    fig = px.line(df_isr, x="Day", y="Flights", color='Year',title='Israel')
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