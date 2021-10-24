# DSTeamProject
github repository for a team project at Data Science Course

## Installation
In order to run the program you need to have Docker installed.

run first ```bash docker-compose build ``` in your terminal inside the project directory.

In order to import database (which includes all data collected) use the following command:
```bash
cat db_dump.sql | docker exec -i your-db-container_id psql -U username
``` 
where db_dump represents the location of dumped .sql file

Then run ```bash docker-compose up ```.

You can now navigate the Dashboard by opening your browser and using the url ```localhost:8050```

## For developers:

To export db run following command:
```bash
docker exec -t docker_database_id  pg_dumpall -c -U username > db_dump.sql
```
https://stackoverflow.com/questions/24718706/backup-restore-a-dockerized-postgresql-database


