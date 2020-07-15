import os
import csv
import json
import slacker
from getYoutubePlaylistItems import get_youtube_playlist_as_URL_list
from getYoutubePlaylistItems import what_videos_remain
import numpy as np 
import random

def list_in_dot_txt(filedir, type="r", input_iter=['read']):
    """ Automating large portion of this code doing simple I/O """
    if type == "r":
        with open(filedir, 'r+') as file:
            input_iter = file.read().split(',')
        return input_iter
    if type == "w":
        with open(filedir, 'w') as outfile:
            outfile.write(','.join(input_iter))
        return ["succeeful write"]

def get_playlist_items(creds_dir, token_dir, playlistID):
    """ retrieve from YouTube all the videos in a playlist using given creds and token """
    #try:
    playlist = get_youtube_playlist_as_URL_list(creds_dir, token_dir, playlistID)
    print(f"returned youtube playlist of {len(playlist)} items: {playlist}")
    return playlist
    #except:
    #    print("couldn't connect, oh well") #internet is weird, ensure action continues even if error
    #    return []

def add_any_new_vids_to_archive(vid_id_list, used, archive):
    """ take list of video IDs being accessed, compare with archive and add anything new """
    #archive is a dict that identifies used and "iterating" videos to avoid repeat plays, grab used first
    used_vids = list(set([x.strip() for x in used])) #[] if archive['used'] == None else archive['used'] 
    #make a master list so we can check if the video has already been captured
    combo = used_vids + archive #archive['iter']
    #make list of any videos in given list that aren't anywhere in the archive
    new_vids = list(set([x.strip() for x in vid_id_list if x not in combo])) #first thing has to have the new things

    #add any new vids to the "iterating" section
    print(f"adding new vids: {new_vids}")
    iter_vids = archive + new_vids #archive['iter'] + new_vids
    iter_vids = list(set([x.strip() for x in iter_vids if len(x.strip()) > 7]))
    return used_vids, iter_vids

def grab_next_video(archive, used, yt_playlist, mode="all"):
    """ use saved archive of video IDs, take the next one off the top to play it and ensure it's not played again """
    print("grabbing the next video")
    #create archive if it doesn't exist, otherwise grab used and iterating lists 
    if os.path.exists(archive):
        archive_used = list_in_dot_txt(used, type="r")
        archive_iter = list_in_dot_txt(archive, type="r")
        archive_used, archive_iter = add_any_new_vids_to_archive(yt_playlist, archive_used, archive_iter)
    else:
        archive_iter = yt_playlist
        archive_used = [] 
    
    _ = list_in_dot_txt(archive, type="w", input_iter=archive_iter)

    if mode in ["all", "post new"]:
        rand = random.randint(0, len(archive_iter) - 1) #pick random number in range of length of iter list
        curr_vid = archive_iter.pop(rand) #grab item n from iterating list
        archive_used.append(curr_vid) #add it to the used list
        print(f"archive updated, popped vid {curr_vid}")
        return curr_vid    #return currently active video ID
    elif mode in [ "add only"]:
        return "added"

def post_msg_to_slack(slack_secrets, message_otd, channel_otd):
    """ use Kip's slackbot to post whatever given message to a specific channel in Chez Dungeness """
    with open(slack_secrets) as f: 
        creds = json.load(f)
    token = creds["botuserOAuthAccessToken"]
    slack = slacker.Slacker(token)
    # Send a message to #general channel
    slack.chat.post_message(channel_otd, message_otd)

def remove_played_vids(iter_list, used_list, dothedeed):
    print(f"open em up")
    archive_iter = list_in_dot_txt(iter_list, type="r")
    archive_used = list_in_dot_txt(used_list, type="r")

    print(f"{len(archive_iter)} items in archive_iter before making a set")
    archive_iter = set(archive_iter)
    print(f"{len(archive_iter)} items in archive_iter after making a set")

    print(f"{len(archive_used)} items in archive_used before making a set")
    archive_used = set(archive_used)
    print(f"{len(archive_used)} items in archive_used after making a set")

    print(f'get em out')
    print(f"{len(archive_iter)} items in archive_iter before cleaning")
    AI = archive_iter.copy()
    for x in archive_iter: 
        if x in archive_used:
            AI.discard(x)
    archive_iter = AI.copy()
    print(f"{len(archive_iter)} items in archive_iter after")
    print(f'haul em out')
    if dothedeed:
        _ = list_in_dot_txt(iter_list, type="w", input_iter=archive_iter)
    print(f'rawhide')

def put_back_in_iter(ytID_list, iter_list, used_list):
    ytID_list = set(ytID_list)
    print(f"ytID_list has {len(ytID_list)} members")
    archive_iter = list_in_dot_txt(iter_list, type="r")
    print(f"archive_iter has {len(archive_iter)} unique members")
    archive_iter = archive_iter.union(ytID_list)
    print(f"archive_iter now has {len(archive_iter)} unique members")
    _ = list_in_dot_txt(iter_list, type="w", input_iter=archive_iter)

    archive_used = list_in_dot_txt(used_list, type="r")
    print(f"archive_used has {len(archive_used)} members")
    archive_used = set(archive_used)
    print(f"archive_used has {len(archive_used)} unique members")
    archive_used = archive_used - ytID_list
    print(f"archive_used now has {len(archive_used)} unique members")
    _ = list_in_dot_txt(used_list, type="w", input_iter=archive_used)

if __name__ == "__main__":
    used_dir = r"D:\Git\Slack-Video-of-the-Day\used.txt"
    iterating_yt_video_list = r"D:\Git\Slack-Video-of-the-Day\slack_archive_BLM.txt"

    ##Management Options##
    # put_back_in_iter(['zein2Bq8ymI', 'V-jEjoliaA0', 'AB-S8wL-AKY'], iterating_yt_video_list, used_dir)
    # remove_played_vids(iterating_yt_video_list, used_dir, True)
    # YTls = list_in_dot_txt(iterating_yt_video_list, type='r')
    # what_videos_remain(YTls)

    run_daily_routine = [True, "add only"] #"all", "post new", "add only"

    if run_daily_routine[0]:
        playlist_items = get_playlist_items(r"D:\Secrets\youtube.json", r"D:\Secrets\youtubetoken.json", "PLrmB8yjf5C3wJ-FcDMzMCjjoqw16oosPa")
        #PLrmB8yjf5C3wJ-FcDMzMCjjoqw16oosPa ; PLrmB8yjf5C3xiyWqPsBYpDRMAdBjVvikP
        vid = grab_next_video(iterating_yt_video_list, used_dir, playlist_items, run_daily_routine[1]) 
        msg = r"Kip's music video of the day! Black Lives Matter. Don't forget to vote. " + \
                "Help your neighbor. https://www.youtube.com/watch?v=" + vid.strip()

        print(msg)
        if vid != "added":
            post_msg_to_slack(r"D:\Secrets\slack.json", msg, '#audiophilia')
