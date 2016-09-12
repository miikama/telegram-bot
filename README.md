# telegram-bot

This bot is written in python, packages required are: google-api-python-client, poster
can be installed with 

pip install --upgrade google-api-python-client

Instructions for setting up the google client for the calendar can be found here
https://developers.google.com/google-apps/calendar/quickstart/python

Things to do for a new user
1. register your application in the google developers console as a new project
2. make a oauth2 token for the project.
3. Download this token as client_secret.json on the same directory with the source code.
 
The telegram part uses json formattef http GET and POST methods from the httplib2 package. Telegram API can be found at 
https://core.telegram.org/bots/api
