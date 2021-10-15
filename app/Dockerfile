FROM python:latest
WORKDIR /code
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py app.py
EXPOSE 8050
CMD ["python", "-u", "app.py"]

