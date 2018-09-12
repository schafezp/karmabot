# Karma Bot
The goal is to make a bot which is able to track user karma 

The architecture uses a telegram bot wrapper 'python-telegram-bot' which stores its data in a locally hosted Postgresql database.
Docker-compose is used to manage the project and push incremental builds to testing and production.

## Actions
The Karma bot will track each user in the telegram group it is a member of and keep track of a score for that individual. 
Reply to a user's post with a message that starts with "+1" or "-1" to give or subtract from the global score of that user.
Use the command /showkarma to view show the karma for all users. Use the command,
```
/userinfo [username]
```
to give information on the history of the user with that username in the current chat.

Still to be added:
There should be a way to check the score of posts perhaps by replying to the post with another command like /checkscore.
There should be advanced analytics including time analysis and per post analysis. 

## Install guide
Install docker, set up a user with docker so you don't use "root" to run docker-compose.
The server_setup.sh file includes commands for installing docker and docker-compose on an ubuntu machine. To install, run
```
sudo server_setup.sh
```

To run the actual code the docker-compose tool is used to start two containers, one that runs a python server for the telegram bot and the other that 
When developing run the following command in the git project 
```
sh run.sh ENV_VAR_FILENAME
```
where ENV_VAR_FILENAME is a file in the format of test_env_vars.sh. Change the parameters are applicable to modify the run.


Change token value environment variable as applicable to each bot. If you want to play around with this code then please use BotFather to create a seperate bot to use when testing.

## Setup guide

A docker-compose.yml and Dockerfile are provided for this project. That means to run the project, install Docker and docker-compose and then run
```
docker-compose build
docker-compose up
```

From there for debugging to propogate a change to running containers do,
```
docker-compose build && docker-compose up -d --no-deps && docker-compose logs bot
```

Postgres exposes port 5432 to the localhost so to connect from your localhost you can do
```
psql -h localhost -p 5432 karmabot test_user
```

## TODO: These are tasks to be accomplished. Feel free to submit pull requests.

### Server (python):
*Features*
- [ ] reply to a message with /showpostkarma (or similar) to do a print out of -the karma of a post
- [ ] Create icon for the karmabot bot and add it through the BotFather
- [ ] Allow you to +1 yourself only in your chat 1 on 1 with the bot. Useful for testing.
- [ ] Create integrated testing environment (possibly using telegram client api?) for making sure the bot works
- [ ] Offer support for users to set a personal flag associated with themselves.
- [ ] Have /userinfo show the rank of a user relative to others
- [ ] Show deltas on /showkarma from most recent /showkarma
- [ ] Create decorator to update chatname, username, etc
- [ ] Add firstname and lastname (maybe even id?) to /userinfo 
- [ ] Create support for testing performance of calls (perhaps using decorators)
- [ ] Create menu for 1 on 1 interaction with karma bot to allow users to check the karma of chars they are in https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#build-a-menu-with-buttons

*Bug fixes*
- [ ] add bug fixes here

### Databases:
- [ ] Create database indexs for performance
- [ ] Make sure transactions are used properly throughout to rollback faulty partial data (bot.py, dbhelper.py)

### Devops (CI/CD):
- [ ] Change deploy script to use rsync instead of zip/unzip every time
- [ ] Create ansible script as alternative to the current janky build system.
- [ ] Clean up project folder structure (mkdir src) and verify that it still works.
- [ ] Create a mechanism to regularly make incremental backups of the database.
- [ ] Verify that docker volume is never accidentally destroyed
- [ ] Create network proxy https://github.com/python-telegram-bot/python-telegram-bot/wiki/Working-Behind-a-Proxy


## DONE: These tasks are finished
- [x] Make a user unable to +1 or -1 themselves
- [x] Don't show the bot on /showkarma
- [x] Seperate karma by chatid so bot can be run for seperate chats (added in database integration)
- [x] Add table to track when users do /showkarma (command_used added )
- [x] Add time field to telegram_message (also time field added to command_used)
- [x] Fix bug: currently users without usernames cannot receive karma. (users get karma but /showkarma still does not display properly)
- [x] Handle bot tokens being passed in as environment variables (including with docker-compose support)
- [x] Fix users without username being reported as "NaN"  or "None" (in showkarma or userinfo)
- [x] Use ON CONFLICT UPDATE SET to not allow users to +1 a single post multiple times
- [x] add /plus1 and /minus1 (or similar) commands as alternative to +1 or -1 for faster mobile usage
