# Replatforming notes

## Environment variables required

```
    DATABASE_URL:         [deployment env secrets]
    FLASK_APP:            application.wsgi:app
    FLASK_CONFIG:         application.config.Config
    GITHUB_CLIENT_ID:     [deployment env secrets]
    GITHUB_CLIENT_SECRET: [deployment env secrets]
    SECRET_KEY:           [deployment env secrets]
    SAFE_URLS:            [domains that auth process can redirect users to after login]
    AUTHENTICATION_ON:    [turn login required on/off]
    SENTRY_DSN: [deployment env secrets - see monitoring]
```

## DNS

The current domain for the application is: https://design.planning.data.gov.uk/

## Monitoring

The application is can be monitored using Sentry if the SENTRY_DSN environment variable is set

## Authentication

The application uses GitHub OAuth for authentication. Only members of the `digital-land` GitHub organization can log in to the application. The authentication flow:

1. Users are redirected to GitHub to authorize the application
2. After authorization, the application checks if the user is a member of the `digital-land` organization
3. If they are a member, they are logged in
4. If they are not a member:
   * Their OAuth token is revoked
   * They are redirected back to the index page with an error message

The configuration env variables for authenication are:

    GITHUB_CLIENT_ID=[client id]
    GITHUB_CLIENT_SECRET=[secret]

The values for the the Github login secrets can be obtained here:

https://github.com/organizations/digital-land/settings/apps/planning-considerations

Note that In the case of a new deployment it would be necessary to create a new client client secret (GITHUB_CLIENT_SECRET) for this application as it is not visible on the settings page for this application.

## Automated Tasks

The following tasks should be run daily to maintain the application data:

1. `flask consider check-dataset-links`
   * Validates and updates dataset URLs and metadata

GitHub Actions are used for two other automated tasks, which are database backups and generating csv files for the planning data platform pipelines.

In a new environment, e.g. AWS the database backup can be managed in another way. Likewise the csv files used for data collection pipelines can be moved to S3? Platform team should be kept informed about any changes on that front.

Therefore alternatives for these should be replaced with alternatives on the replatformed version of this application.

### Database Backup
* Runs daily at 1am UTC
* Downloads the latest database backup from Heroku using `pg:backups:download`
* Saves to `data/latest_backup.dump`
* Automatically commits and pushes changes if the backup has been updated
* Requires Heroku authentication via `HEROKU_OAUTH_TOKEN` secret

### Download and Commit Considerations CSV
* Runs daily at midnight UTC
* Downloads the latest planning considerations CSV from the design site
* Saves to `data/planning-considerations.csv`
* Automatically commits and pushes changes if the file has been updated
