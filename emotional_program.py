#!/usr/bin/env python3
import os
import time
import praw
import requests
import re
import random
import json

def login2reddit():
    print("Logging into reddit . . .")

    try:
        CLIENT_ID = os.environ.get('client_id')
        CLIENT_SECRET = os.environ.get('client_sec')
        USERNAME = os.environ.get('username')
        PASSWORD = os.environ.get('password')

        r = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                            password=PASSWORD,
                            user_agent="Marvin-The-Paranoid-Bot",
                            username=USERNAME)

        print("Successfully logged in!")
    except:
        print("Failed to log in.")

    return r

def json_dump_and_load(file_name, request):
    with open(file_name, "w+") as fp:
        # Serialize obj as a JSON formatted stream to fp (a .write()-supporting file-like object | fp = file pointer
        # params: obj, file stream obj, sort_keys, ensure_ascii (chars output as-is), indent (spaces)
        json.dump(request.json(), fp, sort_keys = True, ensure_ascii = False, indent = 4)
    with open(file_name) as fp:
        # Deserialize fp (a .read()-supporting text file or binary file containing a JSON document) to a Python object 
        data = json.load(fp)
    return data

def reply_to_comment(r, comment_id, comment_reply, comment_subreddit, comment_author, comment_body):
    try:
        # reply to a comment using its comment ID
        comment_to_be_replied_to = r.comment(id=comment_id)
        comment_to_be_replied_to.reply(comment_reply)
        print (f"\nReply details:\nSubreddit: r/{comment_subreddit}\nComment:\"{comment_body}\"\nUser: u/{comment_author}\a")

    # exception handler in case limits are placed on comment frequency due to low karma
    except Exception as err:
        time_remaining = 15
        if (str(err).split()[0] == "RATELIMIT:"):
            for i in str(err).split():
                if (i.isdigit()):
                    time_remaining = int(i)
                    break
            if (not "seconds" or not "second" in str(err).split()):
                time_remaining *= 60

        print (str(err.__class__.__name__) + ": " + str(err))
        for i in range(time_remaining, 0, -5):
            print ("Retrying in", i, "seconds..")
            time.sleep(5)

def marvin_reply(r, responses_data):
    # Universal Time Coordinated (UTC) - variable corresponding to the time a comment was last replied to - 24-hour time standard format
    recent_utc = 0

    with open("utc.txt", "r") as fp:
        recent_utc = fp.readline()
        utc_readable = int(recent_utc)
        print("\nLast invocation found on: " + time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime(utc_readable)))

    try:
        # Quickly search reddit comments using the Pushshift API
        comment_search_results = "https://api.pushshift.io/reddit/search/comment/?q=marvin_thinks&sort_type&sort=desc&size=50&fields=author,body,created_utc,id,subreddit&after=" + recent_utc
        
        parsed_comment_json = json_dump_and_load("comment_data.json", requests.get(comment_search_results))

        if (len(parsed_comment_json["data"]) > 0):
            recent_utc = parsed_comment_json["data"][0]["created_utc"]
            # write the most recent utc used
            with open("utc.txt", "w") as fp:
                fp.write(str(recent_utc))

        for comment in parsed_comment_json["data"]:

            comment_author = comment["author"]
            comment_body = comment["body"]
            comment_id = comment["id"]
            comment_subreddit = comment["subreddit"]
            comment_reply = ""

            if ((re.search("marvin_thinks", comment_body, re.IGNORECASE)) and comment_author != "emotional_marvin"):
                print ("\n\nFound a comment invoking marvin!")
                comment_reply = "Marvin The Paranoid Android: " + random.choice(responses_data['responses'])

                comment_reply += ("\n\n\n\n---\n\n^(I'm a bot. If there are any issues, contact my) [Creator](https://www.reddit.com/message/compose/?to=emotional_program&subject=/u/emotional_marvin).")
                print(comment_body, comment_reply)
                reply_to_comment(r, comment_id, comment_reply, comment_subreddit, comment_author, comment_body)

                print ("\nFetching new comments . . .")


    except Exception as err:
        print(str(err.__class__.__name__) + ": " + str(err))

def main():
   #while True:
        try:
            reddit = login2reddit()
            responses_data = {}

            with open('responses.json', 'r') as fp:
                responses_data = json.load(fp)

            marvin_reply(reddit, responses_data)

        except Exception as err:
            print(str(err.__class__.__name__) + ": " + str(err))
            time.sleep(15)

if __name__ == "__main__":
    main()