import google.oauth2.credentials
import google.auth.transport.requests
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

import os
import json
import datetime

API_SCOPE = ['https://mail.google.com/',]
JSON_FILE = "test_server_client_json.json"
JSON_PATH = os.path.join(os.getcwd(),"<folder_name>",JSON_FILE)

def save_credentials(manager,credentials,valid=True):
    #this is the function that should be called to save the various tokens.
    #credentials is a google.oauth2.credentials.Credentials() object.
    #this saves it in a format that is easy to turn back 
    #into the same type of object in load_credentials(manager).
    #valid is, for the most part, always going to be true, but if for some reason its not
    #make sure to set that flag.
    #this returns the credentials as a dict (ignores the valid flag)
    #---------------------------------------
    #first we get or create the correct DB object
    # try:
    #     creds = Gmail_Connection_Token.objects.get(manager=manager)
    # except Gmail_Connection_Token.DoesNotExist:
    #     creds = Gmail_Connection_Token()
    #     creds.manager = manager
    #now we turn the passed in credentials obj into a dicts obj
    #note the expiry formatting
    temp = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'id_token':credentials.id_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry':datetime.datetime.strftime(credentials.expiry,'%Y-%m-%d %H:%M:%S')
    }
    #now we save it as a json_string into the creds DB obj
    creds.json_string = json.dumps(temp)
    #update the valid flag.
    creds.valid = valid
    #and save everythign in the DB
    creds.save()
    #and finally, return the dict we just created.
    return temp

def load_credentials(manager,ignore_valid=False):
    #this is the function that should be called to load a credentials object     from the database.
    #it loads, refreshes, and returns a     google.oauth2.credentials.Credentials() object.
    #raises a value error if valid = False 
    #------
    #NOTE: if 'ignore_valid' is True:
    #will NOT raise a value error if valid == False
    #returns a Tuple formated as (Credentails(),valid_boolean)
    #======================================
    try:
        creds = Gmail_Connection_Token.objects.get(manager=manager)
    except: 
        #if something goes wrong here, we want to just raise the error
        #and pass it to the calling function.
        raise #yes, this is proper syntax! (don't want to lose the stack     trace)
    #is it valid? do we raise an error?
    if not ignore_valid and not creds.valid:
        raise ValueError('Credentials are not valid.')
    #ok, if we get to here we load/create the Credentials obj()
    temp = json.loads(creds.json_string)
    credentials = google.oauth2.credentials.Credentials(
        temp['token'],
        refresh_token=temp['refresh_token'],
        id_token=temp['id_token'],
        token_uri=temp['token_uri'],
        client_id=temp['client_id'],
        client_secret=temp['client_secret'],
        scopes=temp['scopes'],
    )
    expiry = temp['expiry']
    expiry_datetime = datetime.datetime.strptime(expiry,'%Y-%m-%d %H:%M:%S')
    credentials.expiry = expiry_datetime
    #and now we refresh the token   
    #but not if we know that its not a valid token.
    if creds.valid:
        request = google.auth.transport.requests.Request()
        if credentials.expired:
            credentials.refresh(request)
    #and finally, we return this whole deal
    if ignore_valid:
        return (credentials,creds.valid)
    else:
        return credentials
    