# Karma Bot
The goal is to make a bot which is able to track user karma 

The architecture uses a telegram bot wrapper 'python-telegram-bot' which stores its data in a locally hosted Postgresql database.
Docker-compose is used to manage the project and push incremental builds to testing and production.

## Actions
The Karma bot will track each user in the telegram group it is a member of and keep track of a score for that individual. 
Reply to a user's post with a message that starts with "+1" or "-1" to give or subtract from the global score of that user.

Use the command,
```
/showkarma 
```
to show the karma for all users in the current chat.

Use the command,
```
/userinfo [username]
```
to give information on the history of the user with that username in the current chat.

Use the command,
```
/chatinfo
```
to display information about the current chat.

Use the command,
```
/showversion
```
to check what version of bot is currently running.

Use the command,
```
/checkchatkarmas
```
to view the karma rankings for any chat you've participated in (given or received a +1 in)
This command can be used in a 1 on 1 conversation with the bot so that other users aren't affected.


## Setup guide
Install docker, set up a user with docker so you don't use "root" to run docker-compose.
The scripts/server_setup.sh file includes commands for installing docker and docker-compose on an ubuntu machine. To install, run
```
sudo server_setup.sh
```

The docker-compose tool is used to run the project. It creates two containers, one that runs a python server for the telegram bot and another that runs a postgresql database instance.

When developing to test changes run the following command
```
sh run.sh ENV_VAR_FILENAME
```
where ENV_VAR_FILENAME is a file in the format of test_env_vars.sh. Change the parameters as applicable to modify the run.


Change BOT_TOKEN value environment variable based on the token given by the BotFather.

### connecting to the database

Postgres exposes port 5432 to the localhost so to connect from your localhost you can run the command
```
psql -h localhost -p 5432 karmabot test_user
```

