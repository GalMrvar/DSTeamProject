# Methods definitions for prediction's calculations

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, time, timedelta
from sqlalchemy import create_engine, inspect, Table
from statsmodels.tsa.ar_model import AutoReg
from sklearn.metrics import mean_squared_error
from math import sqrt
##DB conn
db_conn = create_engine("postgresql://username:secret@db:5432/database")

def predictFlights(flights, number_of_days):
    flights = flights.set_index('Day')
    # split dataset
    X = flights.values
    train = X[0:len(X)-1]
    # train autoregression/create mode
    model = AutoReg(train, lags=31)
    model_fit = model.fit()
    # make predictions to desired day
    predictions = model_fit.predict(start=len(train), end=len(train)-1+number_of_days, dynamic=False)
    #create a new list of dates
    newDays = pd.date_range(flights.index[len(X)-1], periods=number_of_days+1, freq='D')
    # return
    return newDays[1:],predictions

def predictVaccinations(vaccinations, number_of_days, lags_var):
    # split dataset
    vaccinations = vaccinations.set_index('date')
    X = vaccinations.values
    train = X[0:len(X)-1]
    # train autoregression/create model
    model = AutoReg(train, lags=lags_var)
    model_fit = model.fit()
    # make predictions to desired day
    predictions = model_fit.predict(start=len(train), end=len(train)-1+number_of_days, dynamic=False)
    #create a new list of dates
    newDays = pd.date_range(vaccinations.index[len(X)-1], periods=number_of_days+1, freq='D')
    # return
    return newDays[1:],predictions