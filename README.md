[![Build Status](https://travis-ci.org/FUB-HCC/ACE-Research-Library.svg?branch=master)](https://travis-ci.org/FUB-HCC/ACE-Research-Library)
[![Coverage Status](https://coveralls.io/repos/github/FUB-HCC/ACE-Research-Library/badge.svg?branch=master)](https://coveralls.io/github/FUB-HCC/ACE-Research-Library?branch=master)

# ACE Research Library

## Development Install

It should be sufficient to just run:

    sudo aptitude install python3-dev libpq-dev g++ libxml2-dev libxslt1-dev postgresql postgresql-contrib
    python3.7 -m pip install --user -U poetry
    poetry install
    sudo -u postgres psql -f db_create.sql
    poetry run ./manage.py migrate
    poetry run ./manage.py collectstatic -l
    poetry run ./manage.py update_index

Please install PyLint and Black on your computer and in your code editor to make sure your code is well readable.

## Staging/Production Deployment

The same as above (on Debian-based systems), but you can call Poetry like so to avoid installing the dev dependencies:

    poetry install --no-dev

## Starting the Server

This project uses [Supervisor](https://pypi.python.org/pypi/supervisor). Start the server with:

    poetry run supervisord -c supervisord.conf

Restart with:

    poetry run supervisorctl restart all

## Tests

    poetry run ./manage.py test researchlibrary

The acerl user needs to have the `createdb` permission:

    alter user acerl with createdb;

## Documentation

To build:

    cd docs/ && make html

To view, open `/docs/html/index.html` in a browser.
