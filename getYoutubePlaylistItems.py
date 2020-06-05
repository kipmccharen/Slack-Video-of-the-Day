# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import google.oauth2.credentials as gcred
import google.auth.transport.requests
import google_auth_oauthlib.flow
from google_auth_oauthlib.flow import InstalledAppFlow 
import googleapiclient.discovery
import googleapiclient.errors
import json
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
import datetime

ytscopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_youtube_playlist_as_URL_list(creds_json_dir, token_txt_dir, playlist_id):

    if not os.path.exists(token_txt_dir):
        flow = InstalledAppFlow.from_client_secrets_file(creds_json_dir, scopes=["https://www.googleapis.com/auth/youtube.readonly"], redirect_uri=r"http://localhost/")

        oathcreds = flow.run_local_server()

        with open(token_txt_dir, 'w+') as f:
            json.dump({"refresh_token": oathcreds._refresh_token, "expiry": oathcreds.expiry, \
                        "token": oathcreds.token, "id_token": oathcreds.id_token}, f, indent=4, sort_keys=True, default=str)
    else:
        temp = json.loads(open(token_txt_dir, 'r').read())
        mysecret = json.loads(open(creds_json_dir, 'r').read())['installed']
        oathcreds = gcred.Credentials(
            temp['token'],
            refresh_token=temp['refresh_token'],
            id_token=temp['id_token'],
            token_uri=mysecret['token_uri'],
            client_id=mysecret['client_id'],
            client_secret=mysecret['client_secret'],
            scopes=ytscopes,
        )
        tmpexpiry = temp['expiry'].split('.')[0]
        oathcreds.expiry = datetime.datetime.strptime(tmpexpiry,'%Y-%m-%d %H:%M:%S')
        request = google.auth.transport.requests.Request()
        if oathcreds.expired:
            oathcreds.refresh(request)

    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=oathcreds) #credentials)

    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=100,
        playlistId=playlist_id
    )
    response = request.execute()
    #print(response)
    output_list = [item['contentDetails']['videoId'] for item in response['items']]
    return output_list

if __name__ == "__main__":
    list = get_youtube_playlist_as_URL_list(r"D:\Secrets\youtube.json", r"D:\Secrets\youtubetoken.json", "PLrmB8yjf5C3zZ2QLqcGQYQD20qu_OMA8f")
    print(list)