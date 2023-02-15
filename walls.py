from binance.client import Client
import json
from operator import itemgetter
import sys
import pprint
from ratelimit import *
import requests

client = Client('Uu2BWKl1G9xrRIrR8NYSC4XrQMwqIJU3PdojdeI81VqYxjHVAc8zogIGLjpTZGP6', 'Cny5NyLbyUxe33ggIg77i4XsyDXGJh2SqEj0MACkqMDkNpGfHh1S5DarbqELf88b')

# get all tickers and prices
prices = client.get_all_tickers()
#pairs = json.dumps(prices, indent=4)
#print pairs
#pairs = [prices[i] for i in xrange(len(prices)) if prices[i]['symbol'][:3] in ('BTC') or prices[i]['symbol'][-3:] in ('BTC')]
pairs = [prices[i] for i in xrange(len(prices)) if prices[i]['symbol'][-3:] in ('BTC')]
#print pairs[0]['symbol']
#print pairs[1]['symbol']
#print pairs[2]['symbol']
#sys.exit()
#depth = client.get_open_orders(symbol = 'ETHBTC', limit = '500')

MINUTE = 60
@rate_limited(1200, MINUTE)
# creating list of all trading pairs and sell wall ratio 
def SellWallRatio(ticker, low, high):
	if low <= ticker+1 <= high: 
# get market depth 
		depth = client.get_order_book(symbol = pairs[ticker]['symbol'], limit = 500, requests_params={'timeout': 0.5})
		#print depth 
		book = json.dumps(depth, indent=4)
		#print book

	# calculate bid area
		sorted_bids = sorted(depth['bids'], key=itemgetter(0), reverse = True) 
		#print sorted_bids
		bid_distance = [float(pairs[ticker]['price']) - float(x[0]) for x in sorted_bids]
		#print price_distance
		#index_test = [price_distance.index(x) for x in price_distance]
		#print index_test
		bid_interval = [x - y for x, y in zip(bid_distance, [0] + bid_distance)]
		#print bid_interval
		bid_size = [float(x[1]) for x in sorted_bids]
		#print bid_size
		bid_area = sum(x * y for x, y in zip(bid_interval, bid_size))
		#print bid_area 

	# calculate sell area
		sorted_asks = sorted(depth['asks'], key=itemgetter(0)) 
		ask_distance = [float(x[0]) - float(pairs[ticker]['price']) for x in sorted_asks]
		ask_interval = [x - y for x, y in zip(ask_distance, [0] + ask_distance)]
		ask_size = [float(x[1]) for x in sorted_asks]
		ask_area = sum(x * y for x, y in zip(ask_interval, ask_size))
		#print ask_area
		
	# calculate sell wall ratio
		if ask_area == 0 or bid_area == 0:
			ratio = 0 
		else:
			ratio = float(ask_area)/float(bid_area)
		return ratio
		#print ratio

wall_screens = [[pairs[x]['symbol'],SellWallRatio(x,1,10)] for x in xrange(len(pairs))]
wall_screens_sorted = sorted(wall_screens, key=itemgetter(1), reverse = True) 
pprint.pprint(wall_screens_sorted)
