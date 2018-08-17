# Karma Bot
The goal is to make a bot which is able to track user karma 

For architecture I was imaging using some type of database server to correlate usernames to karma; perhaps sqlite or redis. I want persistance in case it shuts down.


## Actions
The Karma bot will track each user in the telegram group it is a member of and keep track of a score for that individual. Anyone in the chat can use the command /plus1 to add one total score to that user/post or /minus1 to remove a score point.

There should be a way to check the score of posts perhaps by replying to the post with another command like /checkscore.

There should be a /showscores command which shows all users scores. If arguments are passed such as,

```
/showscore username
```

Then only that username's score is shown.

It would be fun to add pretty html5 representations since that is supported by telegram api bot.


TODO:

[ ] Seperate karma by chatid so bot can be run for seperate chats
[ ] fix /plus1 and /minus1 being parsed by reply handler
[ ] reply to a message with /showpostkarma (or similar) to do a print out of the karma of a post 
