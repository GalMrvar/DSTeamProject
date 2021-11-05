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
from sklearn import preprocessing

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

db_conn = create_engine("postgresql://username:secret@db:5432/database")

app.logger.info(db_conn.connect())

#data frames for aviation data
testdf2 = pd.read_sql_query('SELECT * FROM aviation',db_conn)
df_1 = testdf2.filter(['Entity','Day','Flights'], axis=1)
df_2 = testdf2.filter(['Entity','Day 2019', 'Flights 2019 (Reference)'], axis=1)
df_2["Day 2019"]= pd.to_datetime(df_2["Day 2019"])
df_1.rename(columns={'Entity':'Country'}, inplace=True)
df_2.rename(columns={'Entity':'Country', 'Day 2019': 'Day', 'Flights 2019 (Reference)': 'Flights'}, inplace=True)

#data frames for each year and country of aviation data
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

#Data frames for vaccinations data
df_vacc = pd.read_sql_query('SELECT * FROM vaccinations',db_conn)
df_vacc_ger = df_vacc[df_vacc['location']=='Germany']
df_vacc_che = df_vacc[df_vacc['location']=='Switzerland']
df_vacc_isr = df_vacc[df_vacc['location']=='Israel']

#Merged data frames flights and vaccinations on date and countries
dfinal = testdf2.merge(df_vacc, how='inner', left_on=['Day','Entity'], right_on=['date','location'])
dfinal_ger = dfinal[dfinal['Entity']=='Germany']
dfinal_che = dfinal[dfinal['Entity']=='Switzerland']
dfinal_isr = dfinal[dfinal['Entity']=='Israel']

#Data frames for api data
germany = pd.read_sql_query("""SELECT * FROM "apiCases" WHERE "Country" = 'Germany' AND "Cases" > 0 ORDER BY "Date" ASC """,db_conn)
israel = pd.read_sql_query("""SELECT * FROM "apiCases" WHERE "Country" = 'Israel' AND "Cases" > 0 ORDER BY "Date" ASC """,db_conn)
switzerland = pd.read_sql_query("""SELECT * FROM "apiCases" WHERE "Country" = 'Switzerland' AND "Cases" > 0 ORDER BY "Date" ASC """,db_conn)

#Total cases Data frames for api data
total_cases_germany = pd.read_sql_query("""SELECT * FROM "totalCases" WHERE "Country" = 'Germany' ORDER BY "Date" DESC """,db_conn)
total_cases_israel = pd.read_sql_query("""SELECT * FROM "totalCases" WHERE "Country" = 'Israel' ORDER BY "Date" DESC """,db_conn)
total_cases_switzerland = pd.read_sql_query("""SELECT * FROM "totalCases" WHERE "Country" = 'Switzerland' ORDER BY "Date" DESC """,db_conn)

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

TEXT_INFO_STYLE = {
    'textAlign': 'lefrt',
    'color': '#191970'
}

FILTER_STYLE = {
    'textAlign': 'Left',
    'color': '#0074D9',
    'margin-left': '5%',
    'margin-right': '65%',
    'margin-top': '5%',
    'margin-bottom': '2%',
    'padding': '20px 10p'
}

# composition of sidebar's live data
sidebar = html.Div(
    [
        html.H2('Live Data', style=TEXT_STYLE),
        html.Hr(),
        html.H3('Germany', style=TEXT_STYLE),
        html.H5('Cases on '+ germany.iloc[-1]["Date"].date().strftime('%d.%m.%Y') + ": {cases:,}".format(cases = germany.iloc[-1]["Cases"]), style=TEXT_STYLE),
        html.Hr(),
        html.H3('Switzerland', style=TEXT_STYLE),
        html.H5('Cases on '+ switzerland.iloc[-1]["Date"].date().strftime('%d.%m.%Y') + ": {cases:,}".format(cases = switzerland.iloc[-1]["Cases"]), style=TEXT_STYLE),
        html.Hr(),
        html.H3('Israel', style=TEXT_STYLE),
        html.H5('Cases on '+ israel.iloc[-1]["Date"].date().strftime('%d.%m.%Y') + ": {cases:,}".format(cases = israel.iloc[-1]["Cases"]), style=TEXT_STYLE),
        html.Hr()
    ],
    style=SIDEBAR_STYLE,
)

country_df = pd.read_sql_query('SELECT distinct "Entity" FROM aviation',db_conn) # create list of countrie for the dropdown menu

# germany dataframe for the cases over time graph
germanyCases = pd.read_sql_query("""SELECT "Date", "Cases" FROM "apiCases" WHERE "Country" = 'Germany' AND "Cases" > '0'""",db_conn)

germany_plot_cases = go.Figure()
germany_plot_cases.add_trace(go.Scatter(x=germanyCases.Date, y=germanyCases.Cases, name='germany_cases_over_time',line = dict(color='blue', width=2)))
germany_plot_cases.update_xaxes(dtick="M1", tickformat="%d %B")
germany_plot_cases.update_layout(title='Covid cases in Germany',xaxis_title='Month',yaxis_title='Flights per day')

# switzerland dataframe for the cases over time graph
switzerlandCases = pd.read_sql_query("""SELECT "Date", "Cases" FROM "apiCases" WHERE "Country" = 'Switzerland' AND "Cases" > '0'""",db_conn)

switzerland_plot_cases = go.Figure()
switzerland_plot_cases.add_trace(go.Scatter(x=switzerlandCases.Date, y=switzerlandCases.Cases, name='switzerland_cases_over_time',line = dict(color='blue', width=2)))
switzerland_plot_cases.update_xaxes(dtick="M1", tickformat="%d %B")
switzerland_plot_cases.update_layout(title='Covid cases in Switzerland',xaxis_title='Month',yaxis_title='Flights per day')

# israel dataframe for the cases over time graph
israelCases = pd.read_sql_query("""SELECT "Date", "Cases" FROM "apiCases" WHERE "Country" = 'Israel' AND "Cases" > '0'""",db_conn)

israel_plot_cases = go.Figure()
israel_plot_cases.add_trace(go.Scatter(x=israelCases.Date, y=israelCases.Cases, name='israel_cases_over_time',line = dict(color='blue', width=2)))
israel_plot_cases.update_xaxes(dtick="M1", tickformat="%d %B")
israel_plot_cases.update_layout(title='Covid cases in Israel',xaxis_title='Month',yaxis_title='Flights per day')


content_first_row = dbc.Row([
    dbc.Col(
        dcc.Tabs(id="tabs-example-graph", value='General', children=[
            dcc.Tab(label='General', value = 'General', children=[
                dcc.Graph(id='graph_4'),
                html.Br(),
                html.H3('Germany', style=TEXT_INFO_STYLE),
                html.H5('Total cases: {cases:,} '.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["total_cases"]) + ' - Total vaccinated: {vaccinated:,}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["people_fully_vaccinated"]), style=TEXT_INFO_STYLE),
                html.Br(),
                dcc.Graph(figure=germany_plot_cases,id='graph_germany_cases'),
                html.H3('Switzerland', style=TEXT_INFO_STYLE),
                html.H5('Total cases: {cases:,} '.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["total_cases"]) + ' - Total vaccinated: {vaccinated:,}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["people_fully_vaccinated"]), style=TEXT_INFO_STYLE),
                html.Br(),
                dcc.Graph(figure=switzerland_plot_cases,id='graph_switzerland_cases'),
                html.H3('Israel', style=TEXT_INFO_STYLE),
                html.H5('Total cases: {cases:,} '.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["total_cases"]) + ' - Total vaccinated: {vaccinated:,}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["people_fully_vaccinated"]), style=TEXT_INFO_STYLE),
                html.Br(),
                dcc.Graph(figure=israel_plot_cases,id='graph_israel_cases')
            ]),
            dcc.Tab(label='Flights Comparison', children=[
                html.Br(),
                html.H5('Select the country of your choice using the dropdown menu. You can filter the displayed years in the graph by clicking on the specific year in the right legend.', style=TEXT_INFO_STYLE),
                html.Div([
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[
                            {"label": row[0], "value": row[0]}
                            for index, row in country_df.iterrows()
                        ],
                        value='Germany'
                    )
                ],
                style=FILTER_STYLE,),
                dcc.Graph(id='graph_1', style = {'display':'none'}),
                dcc.Graph(id='graph_2', style = {'display':'none'}),
                dcc.Graph(id='graph_3', style = {'display':'none'})
            ]),
            dcc.Tab(label='Covid vs Flights', children=[
                html.Br(),
                html.H5('Select the country of your choice using the dropdown menu. You can filter the displayed years in the graph by clicking on the specific year in the right legend.', style=TEXT_INFO_STYLE),
                html.Div([
                    dcc.Dropdown(
                        id='country-dropdown-tab3',
                        options=[
                            {"label": row[0], "value": row[0]}
                            for index, row in country_df.iterrows()
                        ],
                        value='Germany'
                    )
                ],
                style=FILTER_STYLE,),
                dcc.Graph(id='graph_5', style = {'display':'none'}),
                dcc.Graph(id='graph_vaccinations_switzerland', style = {'display':'none'}),
                dcc.Graph(id='graph_6', style = {'display':'none'}),
                dcc.Graph(id='graph_vaccinations_germany', style = {'display':'none'}),
                dcc.Graph(id='graph_7', style = {'display':'none'}),
                dcc.Graph(id='graph_vaccinations_israel', style = {'display':'none'})
            ]),
            dcc.Tab(label='Predictions', children=[
                #dcc.Graph(id='graph_3')
            ]),
        ])
    )
])

content = html.Div(
    [
        html.H2('Air Traffic and Covid Dashboard', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
    ],
    style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])

# callbacks section

@app.callback(
    Output('graph_1', 'figure'),
    [Input('country-dropdown', 'value')],
    )
def update_graph_1(dropdown_value):
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
    [Input('country-dropdown', 'value')],
    )
def update_graph_2(dropdown_value):
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
    [Input('country-dropdown', 'value')],
)
def update_graph_3(dropdown_value):
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

germanyVaccinations = pd.read_sql_query('''SELECT iso_code, date ,people_fully_vaccinated FROM vaccinations WHERE iso_code = 'DEU' ''',db_conn)
switzerlandVaccinations = pd.read_sql_query('''SELECT iso_code, date ,people_fully_vaccinated FROM vaccinations WHERE iso_code = 'CHE' ''',db_conn)
israelVaccinations = pd.read_sql_query('''SELECT iso_code, date ,people_fully_vaccinated FROM vaccinations WHERE iso_code = 'ISR' ''',db_conn)

@app.callback(
    Output('graph_vaccinations_switzerland', 'figure'),
    [Input('country-dropdown', 'value')],
)
def update_graph_vaccinations_switzerland(dropdown_value):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=switzerlandVaccinations.date, y=switzerlandVaccinations.people_fully_vaccinated, name='total_vaccinations',
                        line = dict(color='blue', width=2)))
    fig.update_xaxes(dtick="M1", tickformat="%d %B")
    fig.update_layout(title='Switzerland',
                   xaxis_title='Year 2021',
                   yaxis_title='Vaccinated people per day')
    return fig

@app.callback(
    Output('graph_vaccinations_germany', 'figure'),
    [Input('country-dropdown', 'value')],
)
def update_graph_vaccinations_germany(dropdown_value):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=germanyVaccinations.date, y=germanyVaccinations.people_fully_vaccinated, name='total_vaccinations',
                        line = dict(color='blue', width=2)))
    fig.update_xaxes(dtick="M1", tickformat="%d %B")
    fig.update_layout(title='Germany',
                   xaxis_title='Year 2021',
                   yaxis_title='Vaccinated people per day')
    return fig

@app.callback(
    Output('graph_vaccinations_israel', 'figure'),
    [Input('country-dropdown', 'value')],
)
def update_graph_vaccinations_israel(dropdown_value):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=israelVaccinations.date, y=israelVaccinations.people_fully_vaccinated, name='total_vaccinations',
                        line = dict(color='blue', width=2)))
    fig.update_xaxes(dtick="M1", tickformat="%d %B")
    fig.update_layout(title='Israel',
                   xaxis_title='Year 2021',
                   yaxis_title='Vaccinated people per day')
    return fig


@app.callback(
    Output('graph_4', 'figure'),
    [Input('country-dropdown', 'value')]
    )
def update_graph_4(dropdown_value):
   
    df_map_cases = pd.DataFrame({
    'iso_code': ['DEU', 'CHE','ISR'],
    'country':['Germany','Switzerland','Israel'],
    'total_cases':['{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["total_cases"]),'{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["total_cases"]),'{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["total_cases"])],
    'total_deaths':['{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["total_deaths"]),'{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["total_deaths"]),'{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["total_deaths"])],
    'people_fully_vaccinated':['{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["people_fully_vaccinated"]),'{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["people_fully_vaccinated"]),'{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["people_fully_vaccinated"])],
    'people_fully_vaccinated_in_percentage':[
        '{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["people_fully_vaccinated_in_percentage"] ) ,
        '{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["people_fully_vaccinated_in_percentage"]), 
        '{cases:,}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["people_fully_vaccinated_in_percentage"])
        ]

    #'today_cases':['{cases:,}'.format(cases = germany.iloc[-1]["Cases"]),'{cases:,}'.format(cases = switzerland.iloc[-1]["Cases"]),'{cases:,}'.format(cases = israel.iloc[-1]["Cases"])]
    })

    fig = px.choropleth(df_map_cases, 
                        locations='iso_code', 
                        color = 'country', 
                        hover_data = ['total_cases','total_deaths','people_fully_vaccinated','people_fully_vaccinated_in_percentage'],
                        projection = "mercator",
                        color_continuous_scale = px.colors.sequential.Plasma
                        )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    return fig

@app.callback(
    Output('graph_5', 'figure'),
    [Input('country-dropdown-tab3', 'value')],)
def update_graph_5(dropdown_value):   
    #normalized_che_flights = preprocessing.normalize(df_che_2021.Flights)
    #normalized_che_vacc = preprocessing.normalize(df_vacc_che.people_fully_vaccinated)
    #fig = px.scatter(dfinal, x=dfinal.people_fully_vaccinated_in_percentage, y=dfinal.Flights, color='Entity',title='Sample')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dfinal_che.people_fully_vaccinated_in_percentage*100, y=dfinal_che.Flights, name='Flights', mode='markers', marker_color='blue'))
    #fig.update_yaxes(type="log")
    fig.update_layout(title='Switzerland',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Flights per day')
    return fig

@app.callback(
    Output('graph_6', 'figure'),
    [Input('country-dropdown-tab3', 'value')],)
def update_graph_6(dropdown_value):      
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dfinal_ger.people_fully_vaccinated_in_percentage*100, y=dfinal_ger.Flights, name='Flights', mode='markers', marker_color='red'))
    fig.update_layout(title='Germany',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Flights per day')
    return fig


@app.callback(
    Output('graph_7', 'figure'),
    [Input('country-dropdown-tab3', 'value')],)
def update_graph_7(dropdown_value):  
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dfinal_isr.people_fully_vaccinated_in_percentage*100, y=dfinal_isr.Flights, name='Flights', mode='markers', marker_color='green'))
    #fig.add_trace(go.Scatter(x=df_isr_2021.Day, y=df_isr_2021.Flights*10000, name='Flights', mode='markers'))
    #fig.add_trace(go.Scatter(x=df_isr_2021.Day, y=df_vacc_isr.people_fully_vaccinated, name='Vaccinations',
                        #line = dict(color='red', width=2)))
    fig.update_layout(title='Israel',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Flights per day')
    return fig

#Callbacks that display a graph depending on the country selected in the dropdown

@app.callback(
    Output("graph_1", "style"),
    [Input("country-dropdown", "value")],
)

def update_chart_switzerland(country):
    if country == "Switzerland":
        return {'display':'block'}
    else :
        return {'display':'none'}

@app.callback(
    Output("graph_2", "style"), 
    [
        Input("country-dropdown", "value")
    ],
)

def update_chart_germany(country):
    if country == "Germany":
        return {'display':'block'}
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
        return {'display':'block'}
    else :
        return {'display':'none'}


# Callbacks for the dropdown on 3rd tab

@app.callback([
    Output("graph_5", "style"),
    Output("graph_vaccinations_switzerland", "style")],
    [Input("country-dropdown-tab3", "value")],
)

def update_chart_switzerland_tab3(country):
    if country == "Switzerland":
        return {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}

@app.callback([
    Output("graph_6", "style"),
    Output("graph_vaccinations_germany", "style")],
    [
        Input("country-dropdown-tab3", "value")
    ],
)

def update_chart_germany_tab3(country):
    if country == "Germany":
        return {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}

@app.callback([
    Output("graph_7", "style"),
    Output("graph_vaccinations_israel", "style")],
    [
        Input("country-dropdown-tab3", "value")
    ],
)

def update_chart_israel_tab3(country):
    if country == "Israel":
        return {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}


if __name__ == '__main__':
    app.run_server(host="0.0.0.0")