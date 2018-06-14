# GeoDjango and Postgis test project

## Description

This project show basic setup and usage geographic operations using database. It uses PostGis, GeoDjango.
It consists of two models: City with area and center, and flat described by its location.
Model City has ability to return objects with distances to given flat. In order from closest to farthest.
If flat is placed in city area then uses distance to center of the city otherwise uses distance between flat and closest
point or edge of city border. Flat has two methods, one for returning closest city, second for distance between them.


## Folder structure 

Project is divided into two directories. `basic` directory contains only two files, one for models and one for manager. It is intended
to show quick overview, how to query postgres with postgis from django project. `geodistancetest` directory contains all necessary files for
django application, with tests and docker's files to simplify start-up.


## Installation and test

Project provides docker-compose file to simplify start-up. It provides postgres container with installed postgis and web container with
python and django.

To startup project simple execute (you should have installed docker and docker-compose)

    :::bash
    cd geodistancetest
    docker-compose up

This command start database, django application and migrate data.

You may also run tests

    :::bash
    docker-compose run web runtest


## Knowing issues

At first run application can't connect to database. Application container tries connect to database but database isn't started yet. Rerun
`docker-compose up` temporary solve problem.
