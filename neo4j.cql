CREATE CONSTRAINT ON (user:User) ASSERT user.userid IS UNIQUE
CREATE CONSTRAINT ON (message:Message) ASSERT message.messageid IS UNIQUE

//clear db
MATCH (n) detach delete n

CREATE (user1:User {userid : "123", username: "@user1", karma:5}) 
CREATE (user2:User {userid : "984", username: "@user2", karma:3}) 
CREATE (user3:User {userid : "518", username: "@user3", karma:-1}) 

CREATE (chat1:Chat {chatid: "1", name: "A fun chat"})
CREATE (user1)-[:USER_IN_CHAT]->(chat1)
CREATE (user3)-[:USER_IN_CHAT]->(chat1)
CREATE (message1:Message {messageid: "1", text: "message 1 text by user1"})
CREATE (message4:Message {messageid: "4", text: "+1 message 4 replied to message 1"})
CREATE (message5:Message {messageid: "5", text: "-1 message 5 replied to message 1"})
CREATE (message4)-[:REPLIED_TO {vote: 1}]->(message1)
CREATE (message5)-[:REPLIED_TO {vote: 1}]->(message1)
CREATE (user1)-[:AUTHORED_MESSAGE]->(message1)
CREATE (user3)-[:AUTHORED_MESSAGE]->(message4)
CREATE (user3)-[:AUTHORED_MESSAGE]->(message5)
CREATE (message1)-[:WRITTEN_IN_CHAT]->(chat1)
CREATE (message4)-[:WRITTEN_IN_CHAT]->(chat1)
CREATE (message5)-[:WRITTEN_IN_CHAT]->(chat1)

CREATE (chat2:Chat {chatid: "2", name: "A random chat"})
CREATE (user2)-[:USER_IN_CHAT]->(chat2)
CREATE (user3)-[:USER_IN_CHAT]->(chat2)
CREATE (message2:Message {messageid: "2", text: "message 2 text by user2"})
CREATE (message3:Message {messageid: "3", text: "message 3 text by user3"})
CREATE (user2)-[:AUTHORED_MESSAGE]->(message2)
CREATE (user3)-[:AUTHORED_MESSAGE]->(message3)
CREATE (message2)-[:WRITTEN_IN_CHAT]->(chat2)
CREATE (message3)-[:WRITTEN_IN_CHAT]->(chat2)


//witty response

CREATE (wr1:WittyResponse {text : "USER_FIRSTNAME don't upvote yourself"})
CREATE (wr2:WittyResponse {text : "USER_FIRSTNAME bad manners"})

MATCH (n:User) RETURN n

MATCH (n:Chat) RETURN n

//TODO: find all users in chat
//TODO: find all messages in chat
//TODO: find all messages written by user
//TODO: determine how to manage karma

//TODO: compare storing karma on user object with aggregating replies

//Put karma both through relationship and update property values


//get all user karma
MATCH (n:User) return n.userid, n.username, n.karma

//get all user for chat with id 1
MATCH (n:User)-->(chat:Chat)
where chat.chatid="1"
return n

return 

//get all messages in chat with id 1

MATCH (n:Message)-[:WRITTEN_IN_CHAT]->(chat:Chat)
where chat.chatid="1"
return n

//find all replies
MATCH (message1:Message)-[r:REPLIED_TO]->(message2:Message)
return message1, r, message2



//findout how many upvotes a user has received
MATCH (message1:Message)-[r:REPLIED_TO]->(message2:Message)<-[:AUTHORED_MESSAGE]-(user:User)
where user.userid="123"
return user, sum(r.vote)

//findout how many upvotes a user has given
MATCH (user:User)-[:AUTHORED_MESSAGE]->(message1:Message)-[r:REPLIED_TO]->(message2:Message)
where user.userid="518"
return user, sum(r.vote)

//get random witty response
MATCH(wr:WittyResponse)
with wr, rand() as r
ORDER BY r limit 1
return wr