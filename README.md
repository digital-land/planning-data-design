![build](https://github.com/digital-land/dluhc-planning-considerations/actions/workflows/python-app.yml/badge.svg)

# dluhc-planning-considerations
Manage planning considerations through standards process


## Requirements

    python 3.10
    node 18
    postgresql


## Running the app locally with docker

### First time setup or when you need to rebuild assets

    docker compose run --rm assets-build

### Regular development (starts everything)

    docker compose up

### When you need to restore the database

    docker compose down -v
    docker compose up


## To run the app locally without docker

    createdb dluhc-planning-considerations
    make init

### Apply db migrations
    flask db upgrade


### For loading data into db you'll need the heroku-cli

    heroku-cli

[heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)


### Load/update consideration data

    flask consider load-data

### Load/update questions

Questions are [here](application/question_sets.py)

    flask consider load-questions

To add/edit a question make changes [here](application/question_sets.py) then run

    flask consider check-questions

Fix any errors then run the load command above

### Run app locally

    flask run


### To test authentication in local development

Set the following in DevelopmentConfig

    AUTHENTICATION_ON = True

The below is needed for local development and must not be committed to github. Therefore
add to a file called ```.env``` which is gitignored.

    GITHUB_CLIENT_ID=[client id]
    GITHUB_CLIENT_SECRET=[secret]
