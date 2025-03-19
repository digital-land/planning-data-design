![build](https://github.com/digital-land/planning-data-design/actions/workflows/run-tests.yml/badge.svg)

# Planning data design
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

## Deployment

The application is deployed to Heroku and is called `planning-data-design`. [Go to app](https://design.planning.data.gov.uk/)


### Environment variables required
DATABASE_URL:         [set from deployment env]]
FLASK_APP:            application.wsgi:app
FLASK_CONFIG:         application.config.Config
GITHUB_CLIENT_ID:     [available from github app settings]
GITHUB_CLIENT_SECRET: [available from github app settings]
SECRET_KEY:           [set from deployment env]
SAFE_URLS:            [domains that auth process can redirect users to after login]
AUTHENTICATION_ON:    [turn login required on/off]

### DNS

DNS for this application is managed between Digital Land route 53 and Heroku. Configuration is managed on the Heroku side on the `/apps/planning-data-design/settings` page of the dashboard.

## Monitoring

The application is monitored via Sentry - accessible through the Heroku dashboard page for this application on the resources tab.

## Authentication

The application uses GitHub OAuth for authentication. Only members of the `digital-land` GitHub organization can log in to the application. The authentication flow:

1. Users are redirected to GitHub to authorize the application
2. After authorization, the application checks if the user is a member of the `digital-land` organization
3. If they are a member, they are logged in
4. If they are not a member:
   * Their OAuth token is revoked
   * They are redirected back to the index page with an error message

For local development authentication, set the following in DevelopmentConfig:

```env
AUTHENTICATION_ON = True

# Add these to .env file (do not commit to GitHub)
GITHUB_CLIENT_ID=[client id]
GITHUB_CLIENT_SECRET=[secret]
```

## Automated Tasks

The following tasks should be run regularly to maintain the application data:

1. `flask consider load-data`
   * Updates the local database with the latest production data

2. `flask consider load-questions`
   * Updates question sets in the database
   * Questions are defined in `application/question_sets.py`

3. `flask consider check-questions`
   * Validates question configurations before loading
   * Checks for valid slug references between questions

4. `flask consider check-dataset-links`
   * Validates and updates dataset URLs and metadata

5. `flask consider generate-performance`
   * Generates performance metrics for considerations

## GitHub Actions

The repository uses GitHub Actions for continuous integration and automated backups:

### CI Workflow
* Runs on every push and pull request to the main branch
* Installs Python dependencies
* Runs flake8 for linting
* Runs pytest for testing

### Download and Commit Considerations CSV
* Runs daily at midnight UTC
* Downloads the latest planning considerations CSV from the design site
* Saves to `data/planning-considerations.csv`
* Automatically commits and pushes changes if the file has been updated

### Database Backup
* Runs daily at 1am UTC
* Downloads the latest database backup from Heroku using `pg:backups:download`
* Saves to `data/latest_backup.dump`
* Automatically commits and pushes changes if the backup has been updated
* Requires Heroku authentication via `HEROKU_OAUTH_TOKEN` secret
