import os
import json
import dotenv
import requests
import pandas as pd
import datetime
import numpy as np

thisdir = os.path.dirname(os.path.abspath(__file__)) + "\\"
dotenv.load_dotenv()
pd.set_option("display.max_colwidth", 10000)

def post_msg_to_slack(message_otd):
    """ use Kip's slackbot to post whatever given message to whats-due-next in UVA MSDS """
    webhook = os.getenv('WhatsDueNextWebhook')
    x = requests.post(webhook, 
        data = json.dumps(message_otd),
        headers={'Content-Type': 'application/json'}
        )
    print(x.text)

def df_to_col_limit(df, max_len):
    copydf = df.copy()
    measurer = np.vectorize(len)
    lengths = dict(zip(copydf,measurer(copydf.values.astype(str)).max(axis=0)))
    lengths.pop("Date", None)
    for col in lengths.keys():
        len_srcs = [max_len, lengths[col]]
        correct_len = min(len_srcs)
        if max(len_srcs) != correct_len:
            copydf[col] = copydf[col].apply(lambda x: x[:correct_len])
        copydf[col] = copydf[col].str.pad(width=correct_len,side='right', fillchar=' ')
        #print(copydf.head(5))
    out_txt = copydf.to_string(justify="left", index=False)
    return out_txt

def make_txt_from_assignment_tbl(in_df):
    next_x_days = 5 #always show assignments in the next this many days
    #OR
    #next_x_items = 1 #always show the next 5 items

    df = in_df.copy() #copy so it's not a chain reaction
    df.Name = df.Name.fillna(value="unknown") #"unknown" if no ass. title
    df.Due = df.Due.astype('datetime64[ns]')  #make date 
    df = df.sort_values(by=['Due', 'Name']) #sort by due

    nowdt = pd.to_datetime("now").round("D") #create comparison datevalue
    df['DaysLeft'] = df.Due - nowdt #add dates left
    df['DaysLeft'] = df['DaysLeft'].apply(lambda x: x.days) #only include integer
    df = df[df.Due >= nowdt].reset_index() #save original index

    #set aside current index to remove from document later
    df = df.rename(columns={'index':'og_index'}).reset_index()

    #filter to items due X days from now
    #df = df[(df.Due <= nowdt + pd.DateOffset(next_x_days)) | (df.index <= next_x_items)]
    df = df[df.Due == nowdt + pd.DateOffset(next_x_days)]
    #gather the original index values of items to remove from the list
    removeme = list(df.og_index.values)

    if len(df.index) == 0:
        print("There are no new records in the next 5 days")
        return "None", []
    else:

        #create text date, and join together class identifiers
        df['textdate'] = df.Due.apply(lambda x: x.strftime('%a %b %d')) 
        df['profclasstxt'] = df[['Class', 'Registry', 'Tchr']].agg('-'.join, axis=1)
        #limit to, then rename relevant columns better
        df = df[['textdate', 'profclasstxt', 'Type', 'Name']]
        df.columns = ['Date', 'Class', 'Type', 'Assignment']
        
        formatted_txt = df_to_col_limit(df, 50)
        headers = "*Date               Class                                    Type   Assignment*\n"
        first_row = formatted_txt.find("\n")
        formatted_txt = headers + formatted_txt[first_row+1:]
        return formatted_txt, removeme

if __name__ == "__main__":
    csv_src = thisdir + "fall_whatsduenext.csv"

    do_it = True #True = overwrite document & post
                  #False = test and print out results

    #grab current dataset
    df = pd.read_csv(csv_src, encoding="latin-1")
    
    #convert relevant data to text, also list of rows to remove
    txt_df, removeme = make_txt_from_assignment_tbl(df)

    if txt_df != "None":
        if do_it:
            #remove listed rows from df
            # df = df.drop(df.index[removeme])
            
            #create json payload for posting
            myobj = {
        "channel": "whats-due-next",
        "text": txt_df
        }
            #save df minus rows posted
            # df.to_csv(csv_src, encoding="latin-1", index=False)
            
            #post payload to slack
            post_msg_to_slack(myobj)
        else:
            print(removeme)
            print(txt_df)
            # with open("out.txt","w", encoding="latin-1") as f:
            #     f.write(txt_df)
