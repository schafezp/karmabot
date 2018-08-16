# Karma Bot
The goal is to make a bot which is able to track user karma 

For architecture I was imaging using some type of database server to correlate usernames to karma; perhaps sqlite or redis. I want persistance in case it shuts down.


## Actions
Users should be able to reply to another users post with a short message indicating if they give or take away karma. This message could be plain text like "+1" or a command like "/+1"