#################
####### This file contains two functions to support migrating from pickled objects to a database backend
#################


####
# This block of code runs on the database side
####
from typing import Optional, Dict, NewType, Tuple
class User(object):
    """
    A representation of a telegram_user
    """
    id :int
    __karma: int
    first_name: Optional[str]
    last_name: Optional[str]
    username : Optional[str]

##
#to dump the state of the dictionary into a csv using pandas
#
def dump_database(csv_filename: str):
    import pickle
    ChatToKarmaDict = NewType('ChatToKarmaDict', Dict[int, Dict[int, User]])
    #dict of chat_id: int -> Karma_dictionary (which is user_id: int -> user: User)
    chat_to_karma_dictionary : ChatToKarmaDict = dict()
    chat_to_karma_filename = "chat_to_karma_dictionary.p"

    # open the dictionary using pickle to deserialize the file
    try:
        with open(chat_to_karma_filename, "rb") as backupfile:
            chat_to_karma_dictionary: ChatToKarmaDict = pickle.load(backupfile)
    except FileNotFoundError as fnfe:
        print("Chat to Karma dictionary not found. Creating one")
        #this is commented out so we don't accidentally overwrite anything
        """ with open(chat_to_karma_filename, "wb") as backupfile:
            pickle.dump(chat_to_karma_dictionary, backupfile) """

    print(chat_to_karma_dictionary)

    import pandas as pd
    #Create pandas dataframe with columns
    df = pd.DataFrame(columns=['user_id','chat_id','username','karma'])
    for chat_id, userdict in chat_to_karma_dictionary.items():
        for id,user in userdict.items():
            karma = None
            #some user objects dont have the _User__karma property
            try:
                karma = user._User__karma
            except AttributeError as ae:
                karma=0
            if user.id is None:
                break
            else:
                row = {'user_id' :user.id, 'chat_id' : chat_id, 'username' : user.username, 'karma' : karma, 'first_name' : user.first_name, 'last_name' : user.last_name}
                df = df.append(row,ignore_index=True)
                print("id: "+ str(user.id) +  " chat: " + str(chat_id) +  " username: " + str(user.username) + " karma: " + str(karma))

    #float by default; I want to write them as ints in the csv format
    convert_cols = ['user_id','chat_id','karma']
    for col in convert_cols:
        df[col] = df[col].astype(int)
    print(df.head())
    #save to csv with tab seperation
    df.to_csv(csv_filename, sep='\t')


####
# This block of code runs on the server side
####
def load_database(csv_filename: str):
    ##
    # Create a database connection with postgres
    ##
    conn = None
    import time
    import psycopg2
    while conn is None:
        try:
            conn = psycopg2.connect(host="postgres", database="karmabot", user="test_user", password="test_pass")
        except psycopg2.OperationalError as oe:
            print(oe)
            time.sleep(1)

    #Create SQL statement descriptions with place for paramaeters to be injected
    insert_chat = "INSERT INTO telegram_chat VALUES (%s,%s) ON CONFLICT (chat_id) DO UPDATE SET chat_name=EXCLUDED.chat_name"
    insert_user = "INSERT INTO telegram_user (user_id, username, first_name, last_name) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING"
    insert_uic = "INSERT INTO user_in_chat(user_id,chat_id, karma) VALUES (%s,%s,%s) ON CONFLICT (user_id,chat_id) DO UPDATE SET karma=EXCLUDED.karma"

    #open the pandas dataframe from a file
    import pandas as pd
    df = pd.read_csv(csv_filename,sep='\t')

    ##
    # Create a connection to the database then run a bunch of SQL inserts to populate the database
    ##
    with conn:
        with conn.cursor() as crs:
            #loop over every row in the dataframe
            for index, row in df.iterrows():
                #set 3 variables all on one line in python by seperating with ','
                user_id = row['user_id'], chat_id =row['chat_id'], username = row['username'], first_name = row['first_name'], last_name = row['last_name'], karma = row['karma']
                #insert telegram_user
                crs.execute(insert_user,[user_id, username, first_name, last_name])
                #insert telegram_chat
                crs.execute(insert_chat,[chat_id,'default_chat_name'])
                #insert telegram_user_in_chat
                crs.execute(insert_uic,[user_id, chat_id, karma])