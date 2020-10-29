import slacker
from dotenv import load_dotenv 
from pprint import pprint
import pandas as pd
import os
import csv
import json

def list_conversations(slack, match=None):
    """Return channel object to match given name,
    or print out list of channels with their IDs."""
    response = slack.conversations
    response = response.list()
    channels = response.body['channels']
    if match:
        channel = [x for x in channels if x['name'] == match]
        return channel
    for channel in channels:
        print(channel['id'], channel['name'])
    return channels

def list_convo_hist(slack, channel_ID, saveas=None):
    """Return conversation history of given channelID,
    or save as JSON if filepath given as .json type."""
    response = slack.conversations.history(channel_ID)
    
    js = json.loads(response.raw)
    if saveas and ".json" in saveas:
        with open(saveas, 'w') as outfile:
            json.dump(js, outfile)
    return response.body
    #pprint(js)

def get_userlist(slack, userid=None):
    """Return full list of users in slack object 
    for traversal."""
    userlist = slack.users.list() #profile.get(userid)
    userlist = userlist.body['members']
    if userid:
        findme = [x for x in userlist if x['id'] == userid][0]
        return findme
    return userlist

def get_user_emails_from_ids(slack, userids):
    """Return list of users and their emails 
    given a user ID list."""
    email_list = {} #empty email dict to fill
    userlist = get_userlist(slack) #get full userlist

    #userIDs are a flat list
    #userlist is a list of dicts, could convert to df

    #left join userIDs to userlist
    #df to dict of ["email", "real_name"]

    #find match for each individual userid
    for x in userids:
        user = [u for u in userlist if u['id'] == x][0]
        email = user['profile']['email'] 
        username = user['profile']['real_name']
        email_list[username] = email
    return email_list

def find_convo_in_channel(channelname, findtext):
    """Find conversation object given channel name and 
    a string to find in the message text."""
    #get list of all channels to retrieve channel ID
    channel_ID = list_conversations(slack, channelname)
    #use channel ID to get message history in channel
    hist = list_convo_hist(slack, channel_ID[0]["id"])
    hist = hist['messages'] 
    #find the single message containing given string
    right_convo = [x for x in hist if findtext in x['text']][0]
    return right_convo

if __name__ == "__main__":
    #get all convos from slack channel

    # channel = "events"
    # findtext = "Dean Bourne wants to have lunch with us! (Zoom tbd)"
    # right_convo = find_convo_in_channel(channel, findtext)
    # react_list = right_convo['reactions'][0]['users']
    # email_list = get_user_emails_from_ids(slack, react_list)   
    # pprint(email_list)
    load_dotenv() 
    oathaccesstoken = os.getenv("oathaccesstoken")
    slack = slacker.Slacker(oathaccesstoken)
    
    channels = list_conversations(slack)
    df = pd.json_normalize(channels)
    print(df)