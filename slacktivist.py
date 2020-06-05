import os
import json
import slacker
from getYoutubePlaylistItems import get_youtube_playlist_as_URL_list
import numpy as np 
import random

def add_any_new_vids_to_archive(vid_id_list, archive):
    """ take list of video IDs being accessed, compare with archive and add anything new """
    #archive is a dict that identifies used and "iterating" videos to avoid repeat plays, grab used first
    used_vids = [] if archive['used'] == None else archive['used'] 
    #make a master list so we can check if the video has already been captured
    combo = used_vids + archive['iter']
    #make list of any videos in given list that aren't anywhere in the archive
    new_vids = np.setdiff1d(vid_id_list, combo, assume_unique=True).tolist() #first thing has to have the new things
    #add any new vids to the "iterating" section
    print("adding new vids: {}".format(new_vids))
    iter_vids = archive['iter'] + new_vids
    return used_vids, iter_vids

def get_playlist_items(creds_dir, token_dir, playlistID):
    """ retrieve from YouTube all the videos in a playlist using given creds and token """
    #try:
    playlist = get_youtube_playlist_as_URL_list(creds_dir, token_dir, playlistID)
    print("returned youtube playlist: {}".format(playlist))
    return playlist
    #except:
    #    print("couldn't connect, oh well") #internet is weird, ensure action continues even if error
    #    return []

def grab_next_video(archive, yt_playlist):
    """ use saved archive of video IDs, take the next one off the top to play it and ensure it's not played again """
    #create archive if it doesn't exist, otherwise grab used and iterating lists 
    if os.path.exists(archive):
        with open(archive, 'r+') as file:
            arch = json.loads(file.read())
            archive_used, archive_iter = add_any_new_vids_to_archive(yt_playlist, arch)
    else:
        archive_iter = yt_playlist
        archive_used = [] 
    
    rand = random.randint(0, len(archive_iter) - 1) #pick random number in range of length of iter list
    curr_vid = archive_iter.pop(rand) #grab item n from iterating list
    archive_used.append(curr_vid) #add it to the used list
    
    with open(archive, 'w+') as outfile: #save updated lists to the archive
        json.dump({"used": archive_used, "iter": archive_iter}, outfile)
        print("archive updated, popped vid {}".format(curr_vid))

    return curr_vid    #return currently active video ID

def post_msg_to_slack(slack_secrets, message_otd, channel_otd):
    """ use Kip's slackbot to post whatever given message to a specific channel in Chez Dungeness """
    with open(slack_secrets) as f: 
        creds = json.load(f)
    token = creds["botuserOAuthAccessToken"]
    slack = slacker.Slacker(token)
    # Send a message to #general channel
    slack.chat.post_message(channel_otd, message_otd)

if __name__ == "__main__":

    #playlist_items = get_playlist_items(r"D:\Secrets\youtube.json", r"D:\Secrets\youtubetoken.json", "PLrmB8yjf5C3xiyWqPsBYpDRMAdBjVvikP")
    #vid = grab_next_video(r"C:\Users\kipmc\Documents\PyScripts\slack_archive.json", playlist_items)
    #msg = r"Kip's music video of the day! https://www.youtube.com/watch?v=" + vid

    playlist_items = get_playlist_items(r"D:\Secrets\youtube.json", r"D:\Secrets\youtubetoken.json", "PLrmB8yjf5C3wJ-FcDMzMCjjoqw16oosPa")
    vid = grab_next_video(r"C:\Users\kipmc\Documents\PyScripts\slack_archive_BLM.json", playlist_items)
    msg = r"Black Lives Matter. https://www.youtube.com/watch?v=" + vid

    print(msg)
    post_msg_to_slack(r"D:\Secrets\slack.json", msg, '#audiophilia')

