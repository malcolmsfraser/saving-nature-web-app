<<<<<<< HEAD
# saving-nature-web-app
=======
# Saving Nature Upload Interface

Contents:
- requirements.txt : contains all the required packages needed to run the application
- app.py : the application file for the upload application
- auth_settings.py : configuration file for the basic app authentication
- dropbox_utils.py : helper functions for uploading data to DropBox
- utils.py : helper functions for updating DynamoDB and sending data to S3
- templates/ : contains any html templates redered in the application
- static/ : contains all static resources used in the web app

## Function
This app sends material to the saving-nature-uploads S3 bucket to kickstart the prediciton process
This app also sends the raw video to DropBox for persisted storage
S3 upload permissions are obtained through a requests to the getPresignedURL Lambda Function
DropBox permissions are obtained via a refresh token from an previously generated OAuth2 offline key

## Deployment requirements
Since this app fetches permissions with each upload call it can be deployed locally or in any cloud environment

## Security
Currently there is basic user authentication (different from a user login). Test credentials can be found in auth_settings.py
>>>>>>> e22b73a (initial commit)
