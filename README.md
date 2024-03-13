# dluhc-planning-considerations
Manage planning considerations through standards process


## Requirements

    python 3.10
    node 18
    postgresql


## Get started

    createdb dluhc-planning-considerations
    make init

## Run app locally

    flask run


## To test authentication in local development

Set the following in DevelopmentConfig

    AUTHENTICATION_ON = True

The below is needed for local development and must not be committed to github. Therefore
add to a file called ```.env``` which is gitignored.

    GITHUB_APP_ID=[app id]
    GITHUB_CLIENT_ID=[client id]
    GITHUB_CLIENT_SECRET=[secret]
