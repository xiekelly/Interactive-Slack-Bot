#!/usr/bin/python3



import time
import re
import requests



def message_matches(user_id, message_text):
    
    '''
    Check if the username and the word 'bot' appears in the text
    '''
    
    regex_expression = '.*@' + user_id + '.*bot.*'
    regex = re.compile(regex_expression)
   
    # Check if the message text matches the regex above
    match = regex.match(message_text)
    
    # returns true if the match is not None (if the regex had a match)
    return match != None 



def extract_topic(message_text):
    
    '''
    Extract topic. The regex relies on the question having a specific form
    '''
    
    regex_expression = 'what is the latest news on (.+)'
    regex = re.compile(regex_expression, re.IGNORECASE)
    matches = regex.finditer(message_text)
    
    for match in matches:
        return match.group(1)
    
    # if there were no matches, return None
    return None



import MySQLdb as mdb
import sys


def get_latest_news(topic):
    
    '''
    Returns a list of dictionaries with the article title and information
    for all articles that match the given topic
    '''
    
    host = '34.199.88.98'
    username = 'root'
    password = 'dwdstudent2015'
    database = 'NYT_TopStories'

    # Connect to MySQL database
    con = mdb.connect(host, username, password, database, 
                    charset='utf8', use_unicode=True);
    with con:
    
        sql_query = "SELECT * FROM article_info LIMIT 500"

        cur = con.cursor(mdb.cursors.DictCursor) # use dictionary cursor
        cur.execute(sql_query)
        data = cur.fetchall()
    
        # Create a list of dictionaries. 
        # Each dictionary has entries for article title, section, author, and abstract
        result = [ {"title": entry["Title"], "section": entry["Section"], "author": entry["Author"],\
                    "abstract": entry["Abstract"]} 
                for entry in data if topic.lower() in entry["Title"].lower()] 
    
    con.close()

    return result



def create_message(username, topic):
    
    '''
    This function takes as input the username of the user that asked the question,
    and the station_name that we managed to extract from the question (potentially it can be None)
    We check the NYTimes API and respond with the status of the NYTimes.
    '''
    
    if topic != None:
        
        # We want to address the user with the username. Potentially, we can also check
        # if the user has added a first and last name, and use these instead of the username
        message = "Thank you @{u} for asking. "            .format(u=username, t=topic)

        # Let's get the data from the NYTimes API
        matching_articles = get_latest_news(topic)
        
        # If we cannot find any matching articles
        if len(matching_articles) == 0:
            message += "Sorry, I could not find any articles about '{t}'.\n".format(t=topic)
            
        # If there are one or more matching articles
        if len(matching_articles) >= 1:
            message += "Here's your daily digest on '{t}':\n\n".format(t=topic)
            
        # Add the information for each article
        count = 1
        for article in matching_articles:
            
            # limit number of articles to 5
            if count >= 5:
                break
                
            title = article['title']
            section = article['section']
            au = article['author']
            author = au[3:].title() # format string
            if " And " in author:
                author = author.replace(" And ", " and ")
            ab = article['abstract']
            abstract = ab[:1].lower() + ab[1:] # format string
            
            # string it all together
            if " and " in author:
                message += "{c}. In {s} news, '{t}'. {a} discuss how {b}\n\n"\
                .format(c=count, s=section, t=title, a=author, b=abstract)
            else:
                message += "{c}. In {s} news, '{t}'. {a} discusses how {b}\n\n"\
                .format(c=count, s=section, t=title, a=author, b=abstract)
                
            count += 1
   
    else: # error
        
        message =  "Thank you @{u} for asking. ".format(u=username)
        message += "Unfortunately, I did not understand your query.\n"
        message += "Try asking me `what is the latest news on XXXXX`"
        
    return message



# Read the access token from the file and create the Slack Client
import json

secrets_file = 'slack_secret.json'
f = open(secrets_file, 'r') 
content = f.read()
f.close()

auth_info = json.loads(content)
auth_token = auth_info["access_token"]
bot_user_id = auth_info["user_id"]

from slackclient import SlackClient
sc = SlackClient(auth_token)




# Connect to the Real Time Messaging API of Slack and process the events

if sc.rtm_connect():
   
    # Continuously monitor Slack API for recent events
    while True:
        
        # Wait 1 second between monitoring attempts
        time.sleep(1)
        
        # If there are any new events, we will get a response. 
        # If there are no events, the response will be empty
        response = sc.rtm_read()
        
        for item in response:
            
            # Check that the event is a message. 
            # If not, ignore and proceed to the next event.
            if item.get("type") != 'message':
                continue
                
            # Check that the message comes from a user. 
            # If not, ignore and proceed to the next event.
            if item.get("user") == None:
                continue
            
            # Check that the message is asking the bot to do something. 
            # If not, ignore and proceed to the next event.
            message_text = item.get('text')
            if not message_matches(bot_user_id, message_text):
                continue
                
            # Get the username of the user who asked the question
            response = sc.api_call("users.info", user=item["user"])
            username = response['user'].get('name')
            
            # Extract topic from the user's message
            topic = extract_topic(message_text)

            # Prepare the message that we will send back to the user
            message = create_message(username, topic)

            # Post a response to the appropriate channel
            sc.api_call("chat.postMessage", channel="#assignment2_bots", text=message)




