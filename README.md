# Karma Bot
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Karma bot tracks a karma score for each user. Use the bot with your friends to see who gets the most upvotes!

## Using the Bot
To use the bot first add it to your telegram group chat. Currently the bot uses the username [@PlusMinusKarmaBot](http://t.me/PlusMinusKarmaBot).
The karma bot tracks a karma score for each user in the chat it is added to. Reply to a message with a message starting with "+1" or "-1" to add or remove a karma point from the author of that message. 

There are also various bot commands that can be used to interact with the bot as listed below.

### Bot commands

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

## Architecture
The architecture uses a telegram bot wrapper 'python-telegram-bot' which stores its data in a locally hosted Postgresql database.
Docker-compose is used to manage the project and push incremental builds to testing and production.

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

### Connecting to the database

Docker exposes postgres through port 5432 to the localhost so to connect from your localhost you can run the command
```
psql -h localhost -p 5432 karmabot test_user
```

### Admin Maintenence

When a user tries to +1 themselves they receive a "witty response" that tells them not to +1 themselves.
To modify the list of random witty respones:
Modify the attempted_self_plus_one_response.csv to add or remove responses as desired.

Then run the following script to update the database.

```sh
sh scripts/db_admin_update.sh prod_env_vars.sh
```