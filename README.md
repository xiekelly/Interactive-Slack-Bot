# Interactive-Slack-Bot
Creates an interactive bot on Slack web app that retrieves and displays data from NYT Top Stories database :: Using Python and MySQL

## 1. How to interact with ‘NewsBot’:

	ASK “@user_id bot what is the latest news on XXXXX”
	NOTE: the query is not case sensitive, i.e. “Trump”, “trump”, “tRuMP” should return the same results


## 2. Two python notebooks:
	
	SlackBot_FetchFromDatabase.ipynb
	SlackBot_FetchFromURL.ipynb
 
The first notebook fetches data from MySQL 'NYT_TopStories' database from host (34.199.88.98). 
This is the one that is running in the background. The second notebook fetches data directly from the API url.


(c) Kelly Xie, PPDS Spring 2017
