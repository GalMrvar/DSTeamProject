# DSTeamProject
Github repository for a team project for the Data Science and Society course at Utrecht University

## Installation
In order to run the program you need to have Docker installed.

run first ```bash docker-compose build ``` in your terminal inside the project directory.

Then run ```bash docker-compose up ```.

You can now navigate the Dashboard by opening your browser and using the url ```localhost:8050```

## (Optional!) Installation in case of api not being accessible:
After you run ```bash docker-compose build``` command you have to import dumped database with following these next steps:

In order to import database (which includes all data collected) use the following command (windows powershell or linux command prompt):
```bash
cat <path_to_dump_on_pc> | docker exec -i <db_docker_container_id> psql -d database -U username
``` 
where <path_to_dump_on_pc> represents the location of dumped.sql file

In order to find your running docker container ID use: 

```bash
docker ps
``` 

Then you can run ```bash docker-compose up ```

## For developers:

To export db run following command:
```bash
docker exec -t docker_database_id  pg_dumpall -c -U username > db_dump.sql
```
https://stackoverflow.com/questions/24718706/backup-restore-a-dockerized-postgresql-database


