FROM python:latest
WORKDIR /code
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py app.py
COPY data/covid/owid-covid-data.csv data/covid/owid-covid-data.csv
COPY data/flights/2020-States-Flights.csv data/flights/2020-States-Flights.csv
COPY data/flights/2021-States-Flights.csv data/flights/2021-States-Flights.csv
EXPOSE 8050
CMD ["python", "-u", "app.py"]

