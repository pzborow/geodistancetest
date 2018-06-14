#!/bin/sh
# Run Server operations
# Based on:
# https://github.com/geo-data/openstreetmap-tiles-docker/blob/master/run.sh


help () {
    cat /usr/local/share/doc/run/help.txt
}


runserver () {
    migrate
    echo "Running developer server"
    cd /srv
    exec ./manage.py runserver 0:8000
}


makemigrations() {
    echo "Make migrations"
    cd /srv
    ./manage.py makemigrations
}


migrate() {
    echo "Migrate database"
    cd /srv
    ./manage.py migrate
}


runtest() {
    echo "Run tests"
    cd /srv
    ./manage.py test
}


cli () {
    echo "Running bash"
    cd /srv
    exec bash
}


if [ $# -eq 0 ] # If no arguments supplied
then
    if [ "$DEFAULT_RUN_COMMAND" ]
    then # Try execute command from environment DEFAULT_RUN_COMMAND
        ${DEFAULT_RUN_COMMAND}
    else # Else display help
        help
    fi
else # If commands supplied execute the specified command sequence
    for arg
    do
        $arg;
    done
fi
