import pandas as pd
from sqlalchemy import create_engine

filepath = "data/covid/owid-covid-data.csv"

rows_to_keep = ['AFG']
vaccination_data = pd.read_csv(filepath,
                               sep=",",
                               header=0,
                               parse_dates= ['date'],
                               usecols=['iso_code','location','date','total_cases','total_vaccinations','people_vaccinated','people_fully_vaccinated','total_boosters','new_vaccinations','new_vaccinations_smoothed','total_vaccinations_per_hundred','people_vaccinated_per_hundred','people_fully_vaccinated_per_hundred','total_boosters_per_hundred','new_vaccinations_smoothed_per_million', 'population'])
#filter by country
filtered = vaccination_data[(vaccination_data['iso_code'].isin(['DEU','CHE','ISR']))]

#filter by start of vaccination in countries
deu_vaccination_data = filtered[(filtered['date']>'2020-12-26') & (filtered['iso_code'].isin(['DEU']))]
che_vaccination_data = filtered[(filtered['date']>'2020-12-21') & (filtered['iso_code'].isin(['CHE']))]
isr_vaccination_data = filtered[(filtered['date']>'2020-12-18') & (filtered['iso_code'].isin(['ISR']))]

#calculate the percentage of vaccinated people by country
isr_vaccination_data.loc[:, ['people_fully_vaccinated_in_percentage']] = isr_vaccination_data['people_fully_vaccinated']/isr_vaccination_data['population']
deu_vaccination_data.loc[:, ['people_fully_vaccinated_in_percentage']] = deu_vaccination_data['people_fully_vaccinated']/deu_vaccination_data['population']
che_vaccination_data.loc[:, ['people_fully_vaccinated_in_percentage']] = che_vaccination_data['people_fully_vaccinated']/che_vaccination_data['population']

#merge the processed data into one dataframe
vaccination_data_processed = che_vaccination_data.append(deu_vaccination_data)
vaccination_data_processed = vaccination_data_processed.append(isr_vaccination_data)
print(vaccination_data_processed)

'''db_conn = create_engine("postgresql://username:secret@db:5432/database")
vaccination_data_processed.to_sql('vaccinations', db_conn, if_exists='replace')
df2 = pd.read_sql_query('SELECT iso_code, people_fully_vaccinated_in_percentage FROM vaccinations',db_conn)'''
