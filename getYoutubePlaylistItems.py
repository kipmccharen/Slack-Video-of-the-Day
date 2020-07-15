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
from bs4 import BeautifulSoup
import requests

def get_goog_oathcreds(token_txt_dir, creds_json_dir):
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
            scopes=["https://www.googleapis.com/auth/youtube.readonly"],
        )
        tmpexpiry = temp['expiry'].split('.')[0]
        oathcreds.expiry = datetime.datetime.strptime(tmpexpiry,'%Y-%m-%d %H:%M:%S')
        request = google.auth.transport.requests.Request()
        if oathcreds.expired:
            oathcreds.refresh(request)
    return oathcreds

def create_yt_instance(oathcreds):
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=oathcreds) #credentials)
    return youtube

def get_youtube_playlist_as_URL_list(creds_json_dir, token_txt_dir, playlist_id):
    
    oathcreds = get_goog_oathcreds(token_txt_dir, creds_json_dir)
    youtube = create_yt_instance(oathcreds)

    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=100,
        playlistId=playlist_id)
        
    response = request.execute()

    output_list = [item['contentDetails']['videoId'] for item in response['items']]

    return output_list

def get_YT_title(yt_ID):
    html = requests.get(f"http://www.youtube.com/watch?v={yt_ID}").text
    soup = BeautifulSoup(html, "lxml") #enter your youtube url here
    try:
        video_title = soup.find('title').text
        return video_title.replace(' - YouTube', '')
    except:
        return "error"

def what_videos_remain(iter_list):
    names = [(il, get_YT_title(il)) for il in iter_list]
    for name in names:
        print(name)

if __name__ == "__main__":
    # list = get_youtube_playlist_as_URL_list(r"D:\Secrets\youtube.json", r"D:\Secrets\youtubetoken.json", "PLrmB8yjf5C3zZ2QLqcGQYQD20qu_OMA8f")
    # print(list)
    yt_ID_list = ['5GtncsFR1Yg', 'jhvUqV3qeC0', 'myzNf5kW1kQ', 'uVp8JlT1oo0', '4PIMR_oGRcU', 'Z4IEdV7ILAA', 'CMaJoUfPxnw', 's6j-s86Ep3s', 'HMUDVMiITOU', 'ngFDy52eCZY', 'AB-S8wL-AKY', 'g_PxQCqebQw', 'ZmUENUZx2w0', 'hGnrvffEFio', 'IxEIQQkhyeI', 'V-jEjoliaA0', '--tFFz44zvc', '0ijLRVqTzZI', 'Ozd2ja7mAgM', 'GYJ03MIPoIk', 'HqW7eYX5IG4']
    what_videos_remain(yt_ID_list)