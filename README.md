# dluhc-planning-considerations
Manage planning considerations through standards process


## Requirements

    python 3.10
    node 18
    postgresql

For loading data into db:

    heroku-cli

[heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)


## Get started

    createdb dluhc-planning-considerations
    make init

## Apply db migrations
    flask db upgrade


## Load/update consideration data

    flask consider load-data

## Load/update questions

Questions are [here](application/question_sets.py)

    flask consider load-questions

## Run app locally

    flask run


## To test authentication in local development

Set the following in DevelopmentConfig

    AUTHENTICATION_ON = True

The below is needed for local development and must not be committed to github. Therefore
add to a file called ```.env``` which is gitignored.

    GITHUB_CLIENT_ID=[client id]
    GITHUB_CLIENT_SECRET=[secret]
