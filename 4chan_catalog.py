from __future__ import print_function
import basc_py4chan
import sys
from coinmarketcap import Market
import json
import re
from operator import itemgetter
import pprint

# retrieve all coinmarketcap coin names
coinmarketcap = Market()
summary = coinmarketcap.ticker()
coins = [[summary[i]['name'], summary[i]['symbol'], summary[i]['id'], summary[i]['rank'], summary[i]['market_cap_usd']] for i in xrange(len(summary))]
#sys.exit()
sorted_coins = sorted(coins, key=lambda tup: tup[3]) 


# get the board 4chan board /biz/
board = basc_py4chan.Board('biz')

# create list of all threads
all_thread_ids = board.get_all_thread_ids()
#first_thread_id = all_thread_ids[0]
#a_post = basc_py4chan.post(all_thread_ids[1], 'comment')
threads = [board.get_thread(all_thread_ids[i]) for i in xrange(len(all_thread_ids))]

# create list of all posts
thread_posts = [threads[i].all_posts for i in xrange(len(threads))]

posts = list()
for thread in thread_posts:
    for post in thread:
        posts.append(post)

#posts = [post for thread in thread_posts for post in thread]
#print(posts[1:10])
#sys.exit()

# retrieve all post titles, comments, and filenames
posts_data = [(posts[i].subject if posts[i].subject is not None else '') 
	+ '; ' + (posts[i].text_comment if posts[i].text_comment is not None else '') 
	+ '; ' + (posts[i].filename if posts[i].filename is not None else '') for i in xrange(len(posts))]
    
posts_data = [posts_data[i] for i in xrange(len(posts_data)) 
    if len(re.findall('pbc', posts_data[i].lower())) > 0
        #or len(re.findall('pajeet', posts_data[i].lower())) > 0
		or len(re.findall('teeka', posts_data[i].lower())) > 0
        or len(re.findall('palm', posts_data[i].lower())) > 0
        or len(re.findall('beach', posts_data[i].lower())) > 0
        or len(re.findall('confidential', posts_data[i].lower())) > 0
        or len(re.findall('tiwari', posts_data[i].lower())) > 0]

pprint.pprint(posts_data)
sys.exit()
	
#comments = [posts[i].text_comment for i in xrange(len(posts))]
#subjects = [posts[i].subject for i in xrange(len(posts))]
#print(comments[1])
#print(all_posts[0].subject)
#filenames = [all_posts[i].filename for i in xrange(len(posts))]
#file_thumbnail_url = [all_posts[i].thumbnail_url for i in xrange(len(all_posts))]
#print(file_thumbnail_url[0])

#pprint.pprint(sorted_coins[-100:])
#pprint.pprint(comments[-100:])
#pprint.pprint(posts_data[-100:])
#sys.exit()

mentions_word = [
	[sorted_coins[x][0], sum(
		[1 if len(re.findall(r"\b" + sorted_coins[x][0].lower() + r"\b", posts_data[i].lower())) > 0 
			or len(re.findall(r"\b" + sorted_coins[x][2].lower() + r"\b", posts_data[i].lower())) > 0
			or len(re.findall(r"\b" + sorted_coins[x][1].lower() + r"\b", posts_data[i].lower())) > 0
		else 0 for i in xrange(len(posts_data))]
	)] 
	for x in xrange(len(sorted_coins))
]
#sys.exit()

mentions_all = [
	[sorted_coins[x][0], sum(
		[1 if len(re.findall(sorted_coins[x][0].lower(), posts_data[i].lower())) > 0 
			or len(re.findall(sorted_coins[x][2].lower(), posts_data[i].lower())) > 0
			or len(re.findall(sorted_coins[x][1].lower(), posts_data[i].lower())) > 0
		else 0 for i in xrange(len(posts_data))]
	)] 
	for x in xrange(len(sorted_coins))
]

mentions_best = [
	[sorted_coins[x][0], sum(
		[1 if len(re.findall(r"\b" + sorted_coins[x][0].lower() + r"\b", posts_data[i].lower())) > 0 
			or len(re.findall(r"\b" + sorted_coins[x][2].lower() + r"\b", posts_data[i].lower())) > 0
			or len(re.findall(sorted_coins[x][1].lower(), posts_data[i].lower())) > 0
		else 0 for i in xrange(len(posts_data))]
	)] 
	for x in xrange(len(sorted_coins))
]

coin_words = [list(coin) + [mention[1]] for coin, mention in zip(sorted_coins, mentions_word)]
coin_all = [list(coin) + [mention[1]] for coin, mention in zip(coin_words, mentions_all)]
coin_mentions = [list(coin) + [mention[1]] for coin, mention in zip(coin_all, mentions_best)]
sig_mentions = [coin for coin in coin_mentions if coin[5] > 0 or coin[6] > 0 or coin[7] > 0]
mentions_sorted = sorted(sig_mentions, key=lambda tup: tup[5], reverse = True)
pprint.pprint(mentions_sorted) 

	



