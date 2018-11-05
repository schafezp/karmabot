CREATE CONSTRAINT ON (user:User) ASSERT user.id IS UNIQUE
CREATE CONSTRAINT ON (message:Message) ASSERT message.id IS UNIQUE

//clear db
MATCH (n) detach delete n

CREATE (user1:User {id : "1", username: "@user1", karma:5})
CREATE (user2:User {id : "2", username: "@user2", karma:3})
CREATE (user3:User {id : "3", username: "@user3", karma:-1})

CREATE (chat1:Chat {id: "1", name: "A fun chat"})
CREATE (user1)-[:USER_IN_CHAT]->(chat1)
CREATE (user3)-[:USER_IN_CHAT]->(chat1)
CREATE (message1:Message {id: "1", text: "message 1 text by user1"})
CREATE (message4:Message {id: "4", text: "+1 message 4 replied to message 1"})
CREATE (message5:Message {id: "5", text: "-1 message 5 replied to message 1"})
CREATE (message4)-[:REPLIED_TO {vote: 1}]->(message1)
CREATE (message5)-[:REPLIED_TO {vote: 1}]->(message1)
CREATE (user1)-[:AUTHORED_MESSAGE]->(message1)
CREATE (user3)-[:AUTHORED_MESSAGE]->(message4)
CREATE (user3)-[:AUTHORED_MESSAGE]->(message5)
CREATE (message1)-[:WRITTEN_IN_CHAT]->(chat1)
CREATE (message4)-[:WRITTEN_IN_CHAT]->(chat1)
CREATE (message5)-[:WRITTEN_IN_CHAT]->(chat1)

CREATE (chat2:Chat {id: "2", name: "A random chat"})
CREATE (user2)-[:USER_IN_CHAT]->(chat2)
CREATE (user3)-[:USER_IN_CHAT]->(chat2)
CREATE (message2:Message {id: "2", text: "message 2 text by user2"})
CREATE (message3:Message {id: "3", text: "message 3 text by user3"})
CREATE (user2)-[:AUTHORED_MESSAGE]->(message2)
CREATE (user3)-[:AUTHORED_MESSAGE]->(message3)
CREATE (message2)-[:WRITTEN_IN_CHAT]->(chat2)
CREATE (message3)-[:WRITTEN_IN_CHAT]->(chat2)


//witty response

CREATE (wr1:WittyResponse {text : "USER_FIRSTNAME don't upvote yourself"})
CREATE (wr2:WittyResponse {text : "USER_FIRSTNAME bad manners"});

MATCH (n:User) RETURN n

MATCH (n:Chat) RETURN n

//TODO: find all users in chat
//TODO: find all messages in chat
//TODO: find all messages written by user
//TODO: determine how to manage karma

//TODO: compare storing karma on user object with aggregating replies

//Put karma both through relationship and update property values


//get all user karma
MATCH (n:User) return n.id, n.username, n.karma

//get all user for chat with id 1
MATCH (n:User)-->(chat:Chat)
where chat.id="1"
return n

return 

//get all messages in chat with id 1

MATCH (n:Message)-[:WRITTEN_IN_CHAT]->(chat:Chat)
where chat.id="1"
return n

//find all replies
MATCH (message1:Message)-[r:REPLIED_TO]->(message2:Message)
return message1, r, message2

//findout how many upvotes a user has received
MATCH (message1:Message)-[r:REPLIED_TO]->(message2:Message)<-[:AUTHORED_MESSAGE]-(user:User)
where user.id="1"
return user, sum(r.vote)

//findout how many upvotes a user has given
MATCH (user:User)-[:AUTHORED_MESSAGE]->(message1:Message)-[r:REPLIED_TO]->(message2:Message)
where user.id="2"
return user, sum(r.vote)

//clear chat with bot 
MATCH (user:User)-->(chat:Chat)
where user.id="1"//param1
and chat.id="1"
return user, chat
//detach delete user

//TODO use tdd 


//get random witty response
MATCH(wr:WittyResponse)
with wr, rand() as r
ORDER BY r limit 1
return wr;



MATCH (user:User)-[:AUTHORED_MESSAGE]->(message:Message)-[r:REPLIED_TO]->(message_replied_to:Message)
where user.id="3"
RETURN user, message, message_replied_to;


MATCH (user:User)-[:AUTHORED_MESSAGE]->(message:Message)-[r:REPLIED_TO]->(message_replied_to:Message)
MATCH (message:Message)-[:WRITTEN_IN_CHAT]->(chat:Chat)
where user.id="3"
//and chat.id="2"
return r.vote
ORDER BY r.vote;

//RETURN user, message, message_replied_to, chat

MATCH (user:User)-[:AUTHORED_MESSAGE]->(message:Message)-[r:REPLIED_TO {vote: -1}]->(message_replied_to:Message)
MATCH (message:Message)-[:WRITTEN_IN_CHAT]->(chat:Chat)
where user.id="3" and chat.id="2"
return r;


MATCH (user:User)-[:AUTHORED_MESSAGE]->(message:Message)-[r:REPLIED_TO]->(message_replied_to:Message)
MATCH (message:Message)-[:WRITTEN_IN_CHAT]->(chat:Chat)
where user.id="3"
//and chat.id="2"
return distinct(r.vote) as vote_type, count(r.vote) as vote_count
order by vote_type asc;


