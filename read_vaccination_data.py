import pandas as pd

filepath = "data/covid/owid-covid-data.csv"

rows_to_keep = ['AFG']
vaccination_data = pd.read_csv(filepath,
                               sep=",",
                               header=0,
                               parse_dates= ['date'],
                               usecols=['iso_code','location','date','total_cases','total_vaccinations','people_vaccinated','people_fully_vaccinated','total_boosters','new_vaccinations','new_vaccinations_smoothed','total_vaccinations_per_hundred','people_vaccinated_per_hundred','people_fully_vaccinated_per_hundred','total_boosters_per_hundred','new_vaccinations_smoothed_per_million'])
#filter by country
filtered = vaccination_data[(vaccination_data['iso_code'].isin(['USA','DEU','CHE','ISR']))]

#filter by start of vaccination in countries
## USA vaccination data has lots of missing values in columns "total_vaccinations" and "people_vaccinated" but no missing values 
## in column "new_vaccinations_smoothed"
usa_vaccination_data = filtered[(filtered['date']>'2020-12-19') & (filtered['iso_code'].isin(['USA']))]
deu_vaccination_data = filtered[(filtered['date']>'2020-12-26') & (filtered['iso_code'].isin(['DEU']))]
che_vaccination_data = filtered[(filtered['date']>'2020-12-21') & (filtered['iso_code'].isin(['CHE']))]
isr_vaccination_data = filtered[(filtered['date']>'2020-12-18') & (filtered['iso_code'].isin(['ISR']))]

#filling missing values with mean
usa_vaccination_data['people_fully_vaccinated'].fillna((usa_vaccination_data['people_fully_vaccinated'].mean()), inplace=True)
deu_vaccination_data['people_fully_vaccinated'].fillna((deu_vaccination_data['people_fully_vaccinated'].mean()), inplace=True)
che_vaccination_data['people_fully_vaccinated'].fillna((che_vaccination_data['people_fully_vaccinated'].mean()), inplace=True)
isr_vaccination_data['people_fully_vaccinated'].fillna((isr_vaccination_data['people_fully_vaccinated'].mean()), inplace=True)

print(usa_vaccination_data.isnull().sum())
print(deu_vaccination_data.isnull().sum())
print(che_vaccination_data.isnull().sum())
print(isr_vaccination_data.isnull().sum())