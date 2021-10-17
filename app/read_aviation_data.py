import pandas as pd
from sqlalchemy import create_engine
#2020
filepath20 = "data/flights/2020-States-Flights.csv"

flight_data_2020 = pd.read_csv(filepath20,
                               sep=";",
                               header=0,
                               parse_dates= ['Day'],
                               usecols=['Entity','Week','Day','Flights','Flights (7-day moving average)','Day 2019','Flights 2019 (Reference)','% vs 2019 (Daily)','% vs 2019 (7-day Moving Average)'])
#filter by counttry
filtered = flight_data_2020[(flight_data_2020['Entity'].isin(['Germany','Switzerland','Israel']))]

#filter by start of aviation in countries
deu_flights20_data = filtered[(filtered['Day']>='2020-01-01') & (filtered['Entity'].isin(['Germany']))]
che_flights20_data = filtered[(filtered['Day']>='2020-01-01') & (filtered['Entity'].isin(['Switzerland']))]
isr_flights20_data = filtered[(filtered['Day']>='2020-01-01') & (filtered['Entity'].isin(['Israel']))]

#2021
filepath21 = "data/flights/2021-States-Flights.csv"


flight_data_2021 = pd.read_csv(filepath21,
                               sep=";",
                               header=0,
                               parse_dates= ['Day'],
                               usecols=['Entity','Week','Day','Flights','Flights (7-day moving average)','Day 2019','Flights 2019 (Reference)','% vs 2019 (Daily)','% vs 2019 (7-day Moving Average)', 'Day Previous Year', 'Flights Previous Year'])
#filter by counttry
filtered21 = flight_data_2021[(flight_data_2021['Entity'].isin(['Germany','Switzerland','Israel']))]

#filter by start of aviation in countries
deu_flights21_data = filtered21[(filtered21['Day']>='2021-01-01') & (filtered21['Entity'].isin(['Germany']))]
che_flights21_data = filtered21[(filtered21['Day']>='2021-01-01') & (filtered21['Entity'].isin(['Switzerland']))]
isr_flights21_data = filtered21[(filtered21['Day']>='2021-01-01') & (filtered21['Entity'].isin(['Israel']))]

#merge the processed data into one dataframe
flights_data_processed = deu_flights20_data.append(che_flights20_data)
flights_data_processed = flights_data_processed.append(isr_flights20_data)
flights_data_processed = flights_data_processed.append(deu_flights21_data)
flights_data_processed = flights_data_processed.append(che_flights21_data)
flights_data_processed = flights_data_processed.append(isr_flights21_data)

db_conn = create_engine("postgresql://username:secret@db:5432/database")

flights_data_processed.to_sql('aviation', db_conn, if_exists='replace')

