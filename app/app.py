# Main class where the dashboard is built

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
import prediction
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from sklearn import preprocessing

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, requests_pathname_prefix='/app/')

db_conn = create_engine("postgresql://username:secret@db:5432/database")

app.logger.info(db_conn.connect())

#data frames for aviation data
df_aviation_data = pd.read_sql_query('SELECT * FROM aviation',db_conn)
df_1 = df_aviation_data.filter(['Entity','Day','Flights'], axis=1)
df_2 = df_aviation_data.filter(['Entity','Day 2019', 'Flights 2019 (Reference)'], axis=1)
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
dfinal = df_aviation_data.merge(df_vacc, how='inner', left_on=['Day','Entity'], right_on=['date','location'])
dfinal_ger = dfinal[dfinal['Entity']=='Germany']
dfinal_che = dfinal[dfinal['Entity']=='Switzerland']
dfinal_isr = dfinal[dfinal['Entity']=='Israel']

#Data frames for api data
germany = pd.read_sql_query("""SELECT * FROM "apiCases" WHERE "Country" = 'Germany' AND "Cases" > 0 ORDER BY "Date" ASC """,db_conn)
israel = pd.read_sql_query("""SELECT * FROM "apiCases" WHERE "Country" = 'Israel' AND "Cases" > 0 ORDER BY "Date" ASC """,db_conn)
switzerland = pd.read_sql_query("""SELECT * FROM "apiCases" WHERE "Country" = 'Switzerland' AND "Cases" > 0 ORDER BY "Date" ASC """,db_conn)

#Vacination data used for prediction
germanyVaccinationsPred = pd.read_sql_query('''SELECT date ,people_fully_vaccinated_in_percentage FROM vaccinations 
WHERE iso_code = 'DEU' AND people_fully_vaccinated_in_percentage > 0 ''',db_conn)
israelVaccinationsPred = pd.read_sql_query('''SELECT date ,people_fully_vaccinated_in_percentage FROM vaccinations 
WHERE iso_code = 'ISR' AND people_fully_vaccinated_in_percentage > 0 ''',db_conn)
switzerlandVaccinationsPred = pd.read_sql_query('''SELECT date ,people_fully_vaccinated_in_percentage FROM vaccinations 
WHERE iso_code = 'CHE' AND people_fully_vaccinated_in_percentage > 0 ''',db_conn)

#Flights data used for prediction
germanyFlights = pd.read_sql_query("""SELECT "Day", "Flights" FROM "aviation" WHERE "Entity" = 'Germany' AND EXTRACT(YEAR from "Day")='2021' """,db_conn)
israelFlights = pd.read_sql_query("""SELECT "Day", "Flights" FROM "aviation" WHERE "Entity" = 'Israel' AND EXTRACT(YEAR from "Day")='2021' """,db_conn)
switzerlandFlights = pd.read_sql_query("""SELECT "Day", "Flights" FROM "aviation" WHERE "Entity" = 'Switzerland' AND EXTRACT(YEAR from "Day")='2021' """,db_conn)


# the style definitions for the different html elements in the dashboard

SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    }

LABEL_STYLE_INCREASE_CASES = {
    'textAlign': 'left'
    }

TEXT_STYLE_INCREASE_CASES = {
    'textAlign': 'left',
    'color': '#82b74b'
}

TEXT_STYLE_DECREASE_CASES = {
    'textAlign': 'left',
    'color': '#c94c4c'
}

TEXT_INFO_STYLE = {
    'textAlign': 'lefrt',
}

TEXT_INFO_STYLE_VACCINATIONS = {
    'textAlign': 'center',
    'display': 'none'
}

FILTER_STYLE = {
    'textAlign': 'Left',
    'margin-right': '65%',
    'margin-top': '5%',
    'margin-bottom': '2%',
    'padding': '20px 10p'
}

DIV_IMG_STYLE = {
    'display': 'inline-block',
    'width': '100%'
}



# calculation of the growth/decay of positive cases 
germany_cases_increase = germany.iloc[-1]["Cases"] - germany.iloc[-2]["Cases"]
switzerland_cases_increase = switzerland.iloc[-1]["Cases"] - switzerland.iloc[-2]["Cases"]
israel_cases_increase = israel.iloc[-1]["Cases"] - israel.iloc[-2]["Cases"]

# method that load different contents if the growth of the cases is positive or negative
def load_growth_cases_germany():
    if germany_cases_increase >= 0 :
        return html.Div([html.H5('Increased by: {cases:,.0f}'.format(cases = germany_cases_increase), style=TEXT_STYLE_INCREASE_CASES)], style=DIV_IMG_STYLE),
    else :
        return html.Div([html.H5('Decreased by: {cases:,.0f}'.format(cases = germany_cases_increase), style=TEXT_STYLE_DECREASE_CASES)], style=DIV_IMG_STYLE),

def load_growth_cases_switzerland():
    if switzerland_cases_increase >= 0 :
        return html.Div([html.H5('Increased by: {cases:,.0f}'.format(cases = switzerland_cases_increase), style=TEXT_STYLE_INCREASE_CASES)], style=DIV_IMG_STYLE),
    else :
        return html.Div([html.H5('Decreased by: {cases:,.0f}'.format(cases = switzerland_cases_increase), style=TEXT_STYLE_DECREASE_CASES)], style=DIV_IMG_STYLE),

def load_growth_cases_israel():
    if israel_cases_increase >= 0 :
        return html.Div([html.H5('Increased by: {cases:,.0f}'.format(cases = israel_cases_increase), style=TEXT_STYLE_INCREASE_CASES)], style=DIV_IMG_STYLE),
    else :
        return html.Div([html.H5('Decreased by: {cases:,.0f}'.format(cases = israel_cases_increase), style=TEXT_STYLE_DECREASE_CASES)], style=DIV_IMG_STYLE),

# composition of sidebar's live data
sidebar = html.Div(
    [
        html.Br(),
        html.H2('Live Data', style=TEXT_STYLE),
        html.Br(),
        html.Hr(),
        html.Br(),
        html.H3('Germany', style=TEXT_STYLE),
        html.H5('Cases on '+ germany.iloc[-1]["Date"].date().strftime('%d.%m.%Y') + ": {cases:,.0f}".format(cases = germany.iloc[-1]["Cases"]), style=LABEL_STYLE_INCREASE_CASES),
        html.Div(children=load_growth_cases_germany(), id='germany_cases_increase'),
        html.Br(),
        html.Hr(),
        html.Br(),
        html.H3('Switzerland', style=TEXT_STYLE),
        html.H5('Cases on '+ switzerland.iloc[-1]["Date"].date().strftime('%d.%m.%Y') + ": {cases:,.0f}".format(cases = switzerland.iloc[-1]["Cases"]), style=LABEL_STYLE_INCREASE_CASES),
        html.Div(children=load_growth_cases_switzerland(), id='switzerland_cases_increase'),
        html.Br(),
        html.Hr(),
        html.Br(),
        html.H3('Israel', style=TEXT_STYLE),
        html.H5('Cases on '+ israel.iloc[-1]["Date"].date().strftime('%d.%m.%Y') + ": {cases:,.0f}".format(cases = israel.iloc[-1]["Cases"]), style=LABEL_STYLE_INCREASE_CASES),
        html.Div(children=load_growth_cases_israel(), id='israel_cases_increase'),
        html.Br(),
        html.Hr()
    ],
    style=SIDEBAR_STYLE,
)

# create list of countries for the dropdown menu
country_df = pd.read_sql_query('SELECT distinct "Entity" FROM aviation',db_conn) 

# germany dataframe for the cases over time and graph
germanyCases = pd.read_sql_query("""SELECT "Date", "Cases" FROM "apiCases" WHERE "Country" = 'Germany' AND "Cases" > '0'""",db_conn)

germany_plot_cases = go.Figure()
germany_plot_cases.add_trace(go.Scatter(x=germanyCases.Date, y=germanyCases.Cases, name='germany_cases_over_time',line = dict(color='blue', width=2)))
germany_plot_cases.update_xaxes(dtick="M1", tickformat="%d %B")
germany_plot_cases.update_layout(title='Covid cases in Germany',xaxis_title='Month',yaxis_title='Cases per day')

# switzerland dataframe for the cases over time and graph
switzerlandCases = pd.read_sql_query("""SELECT "Date", "Cases" FROM "apiCases" WHERE "Country" = 'Switzerland' AND "Cases" > '0'""",db_conn)

switzerland_plot_cases = go.Figure()
switzerland_plot_cases.add_trace(go.Scatter(x=switzerlandCases.Date, y=switzerlandCases.Cases, name='switzerland_cases_over_time',line = dict(color='red', width=2)))
switzerland_plot_cases.update_xaxes(dtick="M1", tickformat="%d %B")
switzerland_plot_cases.update_layout(title='Covid cases in Switzerland',xaxis_title='Month',yaxis_title='Cases per day')

# israel dataframe for the cases over time and graph
israelCases = pd.read_sql_query("""SELECT "Date", "Cases" FROM "apiCases" WHERE "Country" = 'Israel' AND "Cases" > '0'""",db_conn)

israel_plot_cases = go.Figure()
israel_plot_cases.add_trace(go.Scatter(x=israelCases.Date, y=israelCases.Cases, name='israel_cases_over_time',line = dict(color='green', width=2)))
israel_plot_cases.update_xaxes(dtick="M1", tickformat="%d %B")
israel_plot_cases.update_layout(title='Covid cases in Israel',xaxis_title='Month',yaxis_title='Cases per day')

#Convert Date of total_cases data to datetime[ns] for merging data frames
total_cases_germany_converted = pd.read_sql_query("""SELECT "Date", "Cases", "Country"  FROM "apiCases" WHERE "Country" = 'Germany' AND "Cases" > '0'""",db_conn)
total_cases_germany_converted['Date'] = total_cases_germany_converted['Date'].dt.tz_convert(None)
total_cases_israel_converted = pd.read_sql_query("""SELECT "Date", "Cases", "Country" FROM "apiCases" WHERE "Country" = 'Israel' AND "Cases" > '0'""",db_conn)
total_cases_israel_converted['Date'] = total_cases_israel_converted['Date'].dt.tz_convert(None)
total_cases_switzerland_converted = pd.read_sql_query("""SELECT "Date", "Cases", "Country" FROM "apiCases" WHERE "Country" = 'Switzerland' AND "Cases" > '0'""",db_conn)
total_cases_switzerland_converted['Date'] = total_cases_switzerland_converted['Date'].dt.tz_convert(None)

#Merged data frames of cases and vaccinations on date and countries
cases_vacc_ger = df_vacc_ger.merge(total_cases_germany_converted, how='inner', left_on=['date','location'], right_on=['Date','Country'])
cases_vacc_che = df_vacc_che.merge(total_cases_switzerland_converted, how='inner', left_on=['date','location'], right_on=['Date','Country'])
cases_vacc_isr = df_vacc_isr.merge(total_cases_israel_converted, how='inner', left_on=['date','location'], right_on=['Date','Country'])

# building of the main content of the dashboard
tabs_content = dbc.Row([
    dbc.Col(
        dcc.Tabs(id="tabs-example-graph", value='General', children=[
            # general tab
            dcc.Tab(label='General', value = 'General', children=[
                dcc.Graph(id='graph_4'),
                html.Br(),
                html.H3('Germany', style=TEXT_INFO_STYLE),
                html.H5('Total cases: {cases:,.0f} '.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["total_cases"]) + ' - Total vaccinated: {vaccinated:,.0f}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["people_fully_vaccinated"]), style=TEXT_INFO_STYLE),
                html.Br(),
                dcc.Graph(figure=germany_plot_cases,id='graph_germany_cases'),
                html.H3('Switzerland', style=TEXT_INFO_STYLE),
                html.H5('Total cases: {cases:,.0f} '.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["total_cases"]) + ' - Total vaccinated: {vaccinated:,.0f}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["people_fully_vaccinated"]), style=TEXT_INFO_STYLE),
                html.Br(),
                dcc.Graph(figure=switzerland_plot_cases,id='graph_switzerland_cases'),
                html.H3('Israel', style=TEXT_INFO_STYLE),
                html.H5('Total cases: {cases:,.0f} '.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["total_cases"]) + ' - Total vaccinated: {vaccinated:,.0f}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["people_fully_vaccinated"]), style=TEXT_INFO_STYLE),
                html.Br(),
                dcc.Graph(figure=israel_plot_cases,id='graph_israel_cases')
            ]),
            # tab for the comparison of flights over the years
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
            # tab for analysing the impact of vaccines over air traffic 
            dcc.Tab(label='Covid vs Flights', children=[
                html.Br(),
                html.H5('Select the country of your choice using the dropdown menu.', style=TEXT_INFO_STYLE),
                html.H6('The first graph shows the correlation between the daily flights numbers and vaccination rate of each country.' , style=TEXT_INFO_STYLE),
                html.H6('If you hover over the points, you can see the flights and the vaccination rate on a specific date.' , style=TEXT_INFO_STYLE),
                html.Br(),
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
                html.Br(),
                html.H5('Total vaccinated: {vaccinated:,.0f}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["people_fully_vaccinated"]), id="switzerland_vaccines_label", style=TEXT_INFO_STYLE_VACCINATIONS),
                dcc.Graph(id='graph_5', style = {'display':'none'}),
                dcc.Graph(id='graph_vaccinations_switzerland', style = {'display':'none'}),
                html.H5('Total vaccinated: {vaccinated:,.0f}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["people_fully_vaccinated"]), id="germany_vaccines_label",style=TEXT_INFO_STYLE_VACCINATIONS),
                dcc.Graph(id='graph_6', style = {'display':'none'}),
                dcc.Graph(id='graph_vaccinations_germany', style = {'display':'none'}),
                html.H5('Total vaccinated: {vaccinated:,.0f}'.format(vaccinated = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["people_fully_vaccinated"]), id="israel_vaccines_label",style=TEXT_INFO_STYLE_VACCINATIONS),
                dcc.Graph(id='graph_7', style = {'display':'none'}),
                dcc.Graph(id='graph_vaccinations_israel', style = {'display':'none'})
            ]),
            # tab for analysing the impact of vaccines over positive cases
            dcc.Tab(label='Cases and Vaccines', children=[
                html.Br(),
                html.H5('Select the country of your choice using the dropdown menu.', style=TEXT_INFO_STYLE),
                html.H6('The graph shows the correlation between the daily cases and vaccination rate of each country.' , style=TEXT_INFO_STYLE),
                html.H6('If you hover over the line, you can see the daily case numbers and the vaccination rate on a specific date.' , style=TEXT_INFO_STYLE),
                html.Br(),
                html.Div([
                    dcc.Dropdown(
                        id='country-dropdown-tab5',
                        options=[
                            {"label": row[0], "value": row[0]}
                            for index, row in country_df.iterrows()
                        ],
                        value='Germany'
                    )
                ],
                style=FILTER_STYLE,),
                dcc.Graph(id='graph_cases_vacc_ger', style = {'display':'none'}),
                dcc.Graph(id='graph_cases_vacc_che', style = {'display':'none'}),
                dcc.Graph(id='graph_cases_vacc_isr', style = {'display':'none'})
            ]),
            # tab for the predictions of the number of flights for the next month
            dcc.Tab(label='Predictions', children=[
                html.Br(),
                html.H5('Select the country of your choice using the dropdown menu.', style=TEXT_INFO_STYLE),
                html.Div([
                    dcc.Dropdown(
                        id='country-dropdown-tab4',
                        options=[
                            {"label": row[0], "value": row[0]}
                            for index, row in country_df.iterrows()
                        ],
                        value='Germany'
                    )
                ],
                style=FILTER_STYLE,),
                dcc.Graph(id='graph_pred_flights_ger', style = {'display':'none'}),
                dcc.Graph(id='graph_pred_vaccinations_ger', style = {'display':'none'}),
                dcc.Graph(id='graph_pred_flights_sw', style = {'display':'none'}),
                dcc.Graph(id='graph_pred_vaccinations_sw', style = {'display':'none'}),
                dcc.Graph(id='graph_pred_flights_isr', style = {'display':'none'}),
                dcc.Graph(id='graph_pred_vaccinations_isr', style = {'display':'none'}),
            ]),
        ])
    )
])

# building of the main part of the dashboard
content = html.Div(
    [
        html.Br(),
        html.H2('Air Traffic and Covid Dashboard', style=TEXT_STYLE),
        html.Br(),
        html.Hr(),
        tabs_content,
    ],
    style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])

# callbacks section

# graphs for flights comparison of years for each country
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

# query to get vaccinations data
germanyVaccinations = pd.read_sql_query('''SELECT iso_code, date ,people_fully_vaccinated FROM vaccinations WHERE iso_code = 'DEU' ''',db_conn)
switzerlandVaccinations = pd.read_sql_query('''SELECT iso_code, date ,people_fully_vaccinated FROM vaccinations WHERE iso_code = 'CHE' ''',db_conn)
israelVaccinations = pd.read_sql_query('''SELECT iso_code, date ,people_fully_vaccinated FROM vaccinations WHERE iso_code = 'ISR' ''',db_conn)

# graphs for the vaccination rate of each country
@app.callback(
    Output('graph_vaccinations_switzerland', 'figure'),
    [Input('country-dropdown', 'value')],
)
def update_graph_vaccinations_switzerland(dropdown_value):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=switzerlandVaccinations.date, y=switzerlandVaccinations.people_fully_vaccinated, name='',
                        line = dict(color='red', width=2), hovertemplate =
    '<br>Fully vaccinated people: %{y}<br>'+
    'Date: %{x}<br>',))
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
    fig.add_trace(go.Scatter(x=germanyVaccinations.date, y=germanyVaccinations.people_fully_vaccinated, name='',
                        line = dict(color='blue', width=2), hovertemplate =
    '<br>Fully vaccinated people: %{y}<br>'+
    'Date: %{x}<br>',))
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
    fig.add_trace(go.Scatter(x=israelVaccinations.date, y=israelVaccinations.people_fully_vaccinated, name='',
                        line = dict(color='green', width=2), hovertemplate =
    '<br>Fully vaccinated people: %{y}<br>'+
    'Date: %{x}<br>',))
    fig.update_xaxes(dtick="M1", tickformat="%d %B")
    fig.update_layout(title='Israel',
                   xaxis_title='Year 2021',
                   yaxis_title='Vaccinated people per day')
    return fig

# percentage calculation of new vaccinated people 
germany_vaccinated_percentage = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["people_fully_vaccinated_in_percentage"] * 100
switzerland_vaccinated_percentage = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["people_fully_vaccinated_in_percentage"] * 100
israel_vaccinated_percentage = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["people_fully_vaccinated_in_percentage"] * 100

# map for the main page
@app.callback(
    Output('graph_4', 'figure'),
    [Input('country-dropdown', 'value')]
    )
def update_graph_4(dropdown_value):
   
    df_map_cases = pd.DataFrame({
    'iso_code': ['DEU', 'CHE','ISR'],
    'country':['Germany','Switzerland','Israel'],
    'total_cases':[' {cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["total_cases"]),'{cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["total_cases"]),'{cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["total_cases"])],
    'total_deaths':[' {cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["total_deaths"]),'{cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["total_deaths"]),'{cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["total_deaths"])],
    'people_fully_vaccinated':[' {cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_germany.iloc[-1]["people_fully_vaccinated"]),'{cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_switzerland.iloc[-1]["people_fully_vaccinated"]),'{cases:,.0f}'.format(cases = read_vaccination_data.df_total_vaccinated_and_cases_israel.iloc[-1]["people_fully_vaccinated"])],
    'people_fully_vaccinated_in_percentage':[
        ' {cases:.1f}'.format(cases = germany_vaccinated_percentage) + '%',
        ' {cases:.1f}'.format(cases = switzerland_vaccinated_percentage) + '%', 
        ' {cases:.1f}'.format(cases = israel_vaccinated_percentage) + '%'
        ]
    })
    df_map_cases = df_map_cases.rename(columns={'total_cases': 'Total cases ', 'total_deaths': 'Total deaths ', 'people_fully_vaccinated': 'Total vaccinated ', 'people_fully_vaccinated_in_percentage': 'Vaccinated in percentage '})
    fig = px.choropleth(df_map_cases, 
                        locations='iso_code', 
                        color = 'country', 
                        hover_data = ['Total cases ','Total deaths ','Total vaccinated ','Vaccinated in percentage '],
                        projection = "mercator",
                        color_continuous_scale = px.colors.sequential.Plasma
                        )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    return fig


#graphs for flights and vaccination rate comparison of the countries
@app.callback(
    Output('graph_5', 'figure'),
    [Input('country-dropdown-tab3', 'value')],)
def update_graph_5(dropdown_value):   
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dfinal_che.people_fully_vaccinated_in_percentage*100, y=dfinal_che.Flights, name='Flights', mode='markers', marker_color='red', text=dfinal['Day'], hovertemplate =
    '<br>Flights: %{y}<br>'+
    '% Vaccination Rate: %{x:.2f}%<br>'+
    'Date: %{text}',))
    fig.update_layout(title='Switzerland',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Flights per day')
    return fig

@app.callback(
    Output('graph_6', 'figure'),
    [Input('country-dropdown-tab3', 'value')],)
def update_graph_6(dropdown_value):      
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dfinal_ger.people_fully_vaccinated_in_percentage*100, y=dfinal_ger.Flights, name='Flights', mode='markers', marker_color='blue', text=dfinal['Day'], hovertemplate =
    '<br>Flights: %{y}<br>'+
    '% Vaccination Rate: %{x:.2f}%<br>'+
    'Date: %{text}',))
    fig.update_layout(title='Germany',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Flights per day')
    return fig


@app.callback(
    Output('graph_7', 'figure'),
    [Input('country-dropdown-tab3', 'value')],)
def update_graph_7(dropdown_value):  
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dfinal_isr.people_fully_vaccinated_in_percentage*100, y=dfinal_isr.Flights, name='Flights', mode='markers', marker_color='green', text=dfinal['Day'], hovertemplate =
    '<br>Flights: %{y}<br>'+
    '% Vaccination Rate: %{x:.2f}%<br>'+
    'Date: %{text}',))
    fig.update_layout(title='Israel',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Flights per day')
    return fig

#graphs for the comparison of daily cases with the vaccination rate
@app.callback(
    Output('graph_cases_vacc_ger', 'figure'),
    [Input('country-dropdown-tab5', 'value')],)
def update_graph_cases_vacc_ger(dropdown_value):  
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cases_vacc_ger.people_fully_vaccinated_in_percentage*100, y=cases_vacc_ger.Cases, name='', fill='tozeroy', mode='lines', line_color='blue', text=cases_vacc_ger['date'], hovertemplate =
    '<br>Cases: %{y}<br>'+
    'Vaccination Rate: %{x:.2f}%<br>'+
    'Date: %{text}',))
    fig.update_layout(title='Germany',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Cases per day')
    return fig

@app.callback(
    Output('graph_cases_vacc_che', 'figure'),
    [Input('country-dropdown-tab5', 'value')],)
def update_graph_cases_vacc_che(dropdown_value):  
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cases_vacc_che.people_fully_vaccinated_in_percentage*100, y=cases_vacc_che.Cases, name='', fill='tozeroy', mode='lines', line_color='red', text=cases_vacc_ger['date'], hovertemplate =
    '<br>Cases: %{y}<br>'+
    '% Vaccination Rate: %{x:.2f}%<br>'+
    'Date: %{text}',))
    fig.update_layout(title='Switzerland',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Cases per day')
    return fig

@app.callback(
    Output('graph_cases_vacc_isr', 'figure'),
    [Input('country-dropdown-tab5', 'value')],)
def update_graph_cases_vacc_isr(dropdown_value):  
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cases_vacc_isr.people_fully_vaccinated_in_percentage*100, y=cases_vacc_isr.Cases, name='', fill='tozeroy', mode='lines', line_color='green', text=cases_vacc_ger['date'], hovertemplate =
    '<br>Cases: %{y}<br>'+
    '% Vaccination Rate: %{x:.2f}%<br>'+
    'Date: %{text}',))
    fig.update_layout(title='Israel',
                   xaxis_title='Vaccination rate in %',
                   yaxis_title='Cases per day')
    return fig

#prediction
#flights
@app.callback(
    Output('graph_pred_flights_ger', 'figure'),
     [Input('country-dropdown-tab4', 'value')],)
def update_graph_pred_flights(dropdown_value):  
    fig = go.Figure()
    xVal,yVal = prediction.predictFlights(germanyFlights, 31)
    fig.add_trace(go.Scatter(x=xVal, y=yVal, name='Flights prediction', line = dict(color='blue', width=2)))
    fig.update_layout(title='Germany',
                   xaxis_title='Date',
                   yaxis_title='Flights per day')
    fig.update_layout(hovermode='x unified')
    return fig

@app.callback(
    Output('graph_pred_flights_sw', 'figure'),
     [Input('country-dropdown-tab4', 'value')],)
def update_graph_pred_flights(dropdown_value):  
    fig = go.Figure()
    xVal,yVal = prediction.predictFlights(switzerlandFlights, 31)
    fig.add_trace(go.Scatter(x=xVal, y=yVal, name='Flights prediction', line = dict(color='red', width=2)))
    fig.update_layout(title='Switzerland',
                   xaxis_title='Date',
                   yaxis_title='Flights per day')
    fig.update_layout(hovermode='x unified')
    return fig

@app.callback(
    Output('graph_pred_flights_isr', 'figure'),
     [Input('country-dropdown-tab4', 'value')],)
def update_graph_pred_flights(dropdown_value):  
    fig = go.Figure()
    xVal,yVal = prediction.predictFlights(israelFlights, 31)
    fig.add_trace(go.Scatter(x=xVal, y=yVal, name='Flights prediction', line = dict(color='green', width=2)))
    fig.update_layout(title='Israel',
                   xaxis_title='Date',
                   yaxis_title='Flights per day')
    fig.update_layout(hovermode='x unified')
    return fig

#vaccinations
@app.callback(
    Output('graph_pred_vaccinations_ger', 'figure'),
     [Input('country-dropdown-tab4', 'value')],)
def update_graph_pred_flights(dropdown_value):  
    fig = go.Figure()
    xVal,yVal = prediction.predictVaccinations(germanyVaccinationsPred, 31, 40)
    fig.add_trace(go.Scatter(x=xVal, y=yVal, name='Vaccinations prediction', line = dict(color='blue', width=2)))
    fig.update_layout(title='Germany',
                   xaxis_title='Date',
                   yaxis_title='Vaccination rate in %')
    fig.update_layout(hovermode='x unified')
    return fig

@app.callback(
    Output('graph_pred_vaccinations_sw', 'figure'),
     [Input('country-dropdown-tab4', 'value')],)
def update_graph_pred_flights(dropdown_value):  
    fig = go.Figure()
    xVal,yVal = prediction.predictVaccinations(switzerlandVaccinationsPred, 31, 30)
    fig.add_trace(go.Scatter(x=xVal, y=yVal, name='accinations prediction', line = dict(color='red', width=2)))
    fig.update_layout(title='Switzerland',
                   xaxis_title='Date',
                   yaxis_title='Vaccination rate in %')
    fig.update_layout(hovermode='x unified')
    return fig

@app.callback(
    Output('graph_pred_vaccinations_isr', 'figure'),
     [Input('country-dropdown-tab4', 'value')],)
def update_graph_pred_flights(dropdown_value):  
    fig = go.Figure()
    xVal,yVal = prediction.predictVaccinations(israelVaccinationsPred, 31, 100)
    fig.add_trace(go.Scatter(x=xVal, y=yVal, name='accinations prediction', line = dict(color='green', width=2)))
    fig.update_layout(title='Israel',
                   xaxis_title='Date',
                   yaxis_title='Vaccination rate in %')
    fig.update_layout(hovermode='x unified')
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
    Output("switzerland_vaccines_label", "style"),
    Output("graph_vaccinations_switzerland", "style")],
    [Input("country-dropdown-tab3", "value")],
)

def update_chart_switzerland_tab3(country):
    if country == "Switzerland":
        return {'display':'block'}, {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}, {'display':'none'}

@app.callback([
    Output("graph_6", "style"),
    Output("germany_vaccines_label", "style"),
    Output("graph_vaccinations_germany", "style")],
    [
        Input("country-dropdown-tab3", "value")
    ],
)

def update_chart_germany_tab3(country):
    if country == "Germany":
        return {'display':'block'}, {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}, {'display':'none'}

@app.callback([
    Output("graph_7", "style"),
    Output("israel_vaccines_label", "style"),
    Output("graph_vaccinations_israel", "style")],
    [
        Input("country-dropdown-tab3", "value")
    ],
)

def update_chart_israel_tab3(country):
    if country == "Israel":
        return {'display':'block'}, {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}, {'display':'none'}

#Callbacks for the dropdown in tab 4
@app.callback(
    Output("graph_cases_vacc_che", "style"),
    [Input("country-dropdown-tab5", "value")],
)

def update_chart_switzerland_tab5(country):
    if country == "Switzerland":
        return {'display':'block'}
    else :
        return {'display':'none'}

@app.callback(
    Output("graph_cases_vacc_ger", "style"), 
    [
        Input("country-dropdown-tab5", "value")
    ],
)

def update_chart_germany_tab5(country):
    if country == "Germany":
        return {'display':'block'}
    else :
        return {'display':'none'}


@app.callback(
    Output("graph_cases_vacc_isr", "style"),
    [
        Input("country-dropdown-tab5", "value")
    ],
)

def update_chart_israel_tab5(country):
    if country == "Israel":
        return {'display':'block'}
    else :
        return {'display':'none'}

#Callbacks for the graphs in tab 5
@app.callback([
    Output("graph_pred_flights_sw", "style"),
    Output("graph_pred_vaccinations_sw", "style")],
    [
        Input("country-dropdown-tab4", "value")
    ],
)

def update_chart_switzerland_tab4(country):
    if country == "Switzerland":
        return {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}

@app.callback([
    Output("graph_pred_flights_ger", "style"),
    Output("graph_pred_vaccinations_ger", "style")], 
    [
        Input("country-dropdown-tab4", "value")
    ],
)

def update_chart_germany_tab4(country):
    if country == "Germany":
        return {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}


@app.callback([
    Output("graph_pred_flights_isr", "style"),
    Output("graph_pred_vaccinations_isr", "style")], 
    [
        Input("country-dropdown-tab4", "value")
    ],
)

def update_chart_israel_tab4(country):
    if country == "Israel":
        return {'display':'block'}, {'display':'block'}
    else :
        return {'display':'none'}, {'display':'none'}

app.title = "AirCovid"

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")