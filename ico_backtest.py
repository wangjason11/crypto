# Market data extraction via R 
#>install.packages("crypto", dependencies = TRUE)
#>devtools::install_github("jessevent/crypto") 
#>library(crypto)
#>coins = getCoins()
#>setwd("~/codingproj/cryptos")
#>write.csv(coins[,c('slug', 'symbol', 'name', 'date', 'ranknow', 'open', 'high', 'low', 'close', 'market')], 'coins_historical.csv')
#>write.csv(coins, 'coins_historical.csv')
#>python -i ico_backtest_v3.py

# MAKE SURE TO CHANGE NAME IN COIN_HISTORICAL TO LOWER CASE!!!
# MAKE SURE TO AVERAGE PRICES!!!
from __future__ import division
import collections
import numpy as np   
import csv 
import pandas as pd
import itertools
import sys
#import operator
import pprint
from operator import itemgetter
import json
import datetime
import random 
import re

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.cm as cm
from matplotlib import colors as mcolors


# DATA PULLING & CLEANING 
dfico = pd.read_csv('ico_list_v2.csv')
dfico.date = pd.to_datetime(dfico.date, infer_datetime_format =True)
dfico.fst_exchange_date = pd.to_datetime(dfico.fst_exchange_date, infer_datetime_format =True)
#print dfico.dtypes
#print dfico.index

ico_list = [{'ico': str(dfico.loc[id, 'ICO']).lower(), 'symbol': str(dfico.loc[id, 'symbol']).upper(), 'ico_usd': dfico.loc[id, 'exchange_rate_USD'], 'ico_btc': dfico.loc[id, 'Exchange_rate_BTC'],
	'ico_date': dfico.loc[id, 'date'], 'ico_quarter': str(dfico.loc[id, 'date'].to_period('Q')), 'exc_date': dfico.loc[id, 'fst_exchange_date'], 'days_to_ex': dfico.loc[id, 'days_to_exchange'], 'raised': dfico.loc[id, 'raised'],
    'hardcap': dfico.loc[id, 'hardcap'], 'exchange_score': dfico.loc[id, 'Exchange_score'], 'team': dfico.loc[id, 'team'], 'advisor_investor': dfico.loc[id, 'advisor_investor'], 
    'use_case': dfico.loc[id, 'use_case']} for id in dfico.index]

#pprint.pprint(ico_list)

ico_names = [ico_list[id]['ico'] for id in xrange(len(ico_list))]
#print ico_names
#print ico_list[0]['ico']
ico_names.append('bitcoin')
#print ico_names
#sys.exit()

df = pd.read_csv('coins_historical_20180429.csv')
df.volume = df.volume.astype(float)
df.date = pd.to_datetime(df.date, infer_datetime_format =True)
#print df.dtypes

#print df.index

df = df[df['name'].isin(ico_names)]
dfhistorical = df[~df['slug'].isin(['enigma'])]
#print len(df.index)
#print len(dfhistorical.index)
#sys.exit()

coin_history = [
    {'name': dfhistorical.loc[id, 'name'],'date': dfhistorical.loc[id, 'date'], 'price': dfhistorical.loc[id, 'average'], 'volume': dfhistorical.loc[id, 'volume']
    , 'market': dfhistorical.loc[id, 'market'], 'btc_price': dfhistorical.loc[df[np.logical_and(df['date'] == dfhistorical.loc[id, 'date'], df['name'] == 'bitcoin')].index[0], 'average']
	, 'sats': dfhistorical.loc[id, 'average']/dfhistorical.loc[df[np.logical_and(df['date'] == dfhistorical.loc[id, 'date'], df['name'] == 'bitcoin')].index[0], 'average']}
	for id in dfhistorical.index]

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
 
json = json.dumps(coin_history, default = myconverter)
f = open('coin_history.json', 'w')
f.write(json)
f.close()

#with open('data.json', 'r') as fp:
#    data = json.load(fp)

#coin_history = data
#pprint.pprint(coin_history)
#print test
#sys.exit()

ico_d = collections.defaultdict(list)	
for id in coin_history:
    ico_d[id['name']].append({key: value for key, value in id.items() if key <> 'name'})

#pprint.pprint(coin_d, indent = 4, depth = 6)
#print coin_d['ETH']['date']

ico_list = [coin for coin in ico_list if ico_d[coin['ico']] <> []]

for coin in ico_list:
    #print pd.isnull(coin['exc_date'])
    coin['first_day'] = min([item['date'] for item in ico_d[coin['ico']]])


# ANALYSIS 
def ifnull(entered, pulled):
    if pd.isnull(entered) or entered < pulled: 
        return pulled
    else:
        return entered

        
sat_return = collections.defaultdict(list)	
for coin in ico_list:
    for datapoint in sorted(ico_d[coin['ico']], key=itemgetter('date')):
        sat_return[coin['ico']].append((coin['ico_quarter'], datapoint['date'], int((datapoint['date'] - ifnull(coin['exc_date'], coin['first_day'])).days), datapoint['sats']/coin['ico_btc']-1))

#sys.exit()
#usd_return = collections.defaultdict(list)	
#for coin in ico_list:
#    for datapoint in sorted(ico_d[coin['ico']], key=itemgetter('date')):
#        usd_return[coin['ico']].append((int((datapoint['date'] - coin['exc_date']).days), datapoint['price']/coin['ico_usd']-1))


real_return = collections.defaultdict(list)	
for coin in ico_list:
    prev_price = 0.0
    prev_btc = 0.0
    for rk, datapoint in enumerate(sorted(ico_d[coin['ico']], key=itemgetter('date'))):
        if rk == 0:
            real_price = coin['ico_btc']*(datapoint['sats']/coin['ico_btc'] - datapoint['btc_price']/ico_d['bitcoin'][next((index for (index, d) in enumerate(ico_d['bitcoin']) if d['date'] == coin['ico_date']), None)]['price'] + 1)
            real_return[coin['ico']].append((coin['ico_quarter'], datapoint['date'], int((datapoint['date'] - ifnull(coin['exc_date'], coin['first_day'])).days), real_price/coin['ico_btc']-1))
            prev_price = real_price
            prev_btc = datapoint['btc_price']
            prev_sat = datapoint['sats']
        else:
            real_price = prev_price*(datapoint['sats']/prev_sat - datapoint['btc_price']/prev_btc + 1)
            real_return[coin['ico']].append((coin['ico_quarter'], datapoint['date'], int((datapoint['date'] - ifnull(coin['exc_date'], coin['first_day'])).days), real_price/coin['ico_btc']-1))
            prev_price = real_price
            prev_btc = datapoint['btc_price']
            prev_sat = datapoint['sats']


max_return = {}
max_return = {key: sorted(value, key=itemgetter(3), reverse = True)[0] for key, value in real_return.items() if key <> 'bitcoin'}

best_entry = {}
best_entry = {key: sorted(value, key=itemgetter(3))[0] for key, value in real_return.items() if key <> 'bitcoin'}

max_satreturn = {}
max_satreturn = {key: sorted(value, key=itemgetter(3), reverse = True)[0] for key, value in sat_return.items() if key <> 'bitcoin'}

best_satentry = {}
best_satentry = {key: sorted(value, key=itemgetter(3))[0] for key, value in sat_return.items() if key <> 'bitcoin'}

#max_return_tup = [(key, value[1], value[2]) for key, value in max_return.items()]
#max_satreturn_tup = [(key, value[1], value[2]) for key, value in max_satreturn.items()]
#best_entry_tup = [(key, value[1], value[2]) for key, value in best_entry.items()]
#best_satentry_tup = [(key, value[1], value[2]) for key, value in best_satentry.items()]

#with open('returns.csv','wb') as out:
#    csv_out=csv.writer(out)
#    csv_out.writerow(['name_ar', 'maxdays_ar', 'max_ar', 'name_sr', 'maxdays_sr', 'max_sr', 'name_bear', 'bedays_ar', 'be_ar', 'name_besr', 'bedays_sr', 'be_sr'])
#    for row in zip(sorted(max_return_tup, key=itemgetter(0)), sorted(max_satreturn_tup, key=itemgetter(0)), sorted(best_entry_tup, key=itemgetter(0)), sorted(best_satentry_tup, key=itemgetter(0))):
#        clean_row = row[0] + row[1] + row[2] + row[3]
#        csv_out.writerow(clean_row)

#max_return = dict()
#for key, value in real_return.items():
#    print key, sorted(value, key=itemgetter(1), reverse = True)[0]
    #pprint.pprint(max_return)
    
sys.exit()


rainbow = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name) for name, color in rainbow.items())
colors = [name for hsv, name in by_hsv]
colors = [name for name in colors if not re.findall('white', name) and not re.findall('grey', name) and not re.findall('light', name)
    and name not in ['snow', 'azure', 'ivory', 'mintcream', 'aliceblue', 'w', 'lightyellow', 'beige', 'aliceblue', 'seashell', 'honeydew', 'linen', 'lavenderblush', 'oldlace', 'cornsilk'
    , 'lemonchiffon', 'lavender', 'lightcyan', 'papayawhip', 'gainsboro', 'paleturquoise', 'mistyrose', 'salmon', 'blanchedalmond', 'pink', 'powderblue', 'palegoldenrod', 'thistle']]

colors = random.sample(colors, len(ico_list))

ico_colors = {key: value for key, value in zip([coin['ico'] for coin in ico_list], colors)}

# (EDIT: now working) real return for all icos plot not working for some retarded reason 
# Groupings: <2017, 2017Q1-2, 2017Q3, 2017Q4, 2018Q1
#plt.axis([0, 550, -2, 20])
#plt.axis([0, 450, -2, 20])
plt.axis([0, 350, -2,  20])
#plt.axis([0, 250, -2, 20])
#plt.axis([0, 150, -2, 20])
ax = plt.axes()
#ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
for key, value in sat_return.items():
    w, x, y, z = zip(*value)
    #if w[0] in ('2015Q3', '2015Q4', '2016Q1', '2016Q2', '2016Q3', '2016Q4'):
    #if w[0] in ('2017Q1', '2017Q2'):
    if w[0] in ('2017Q3'):
    #if w[0] in ('2017Q4'):
    #if w[0] in ('2018Q1'):
        plt.plot(y,z, label = key, color = ico_colors[key])

for key, value in max_satreturn.items():
    #if value[0] in ('2015Q3', '2015Q4', '2016Q1', '2016Q2', '2016Q3', '2016Q4'):
    #if value[0] in ('2017Q1', '2017Q2'):
    if value[0] in ('2017Q3'):
    #if value[0] in ('2017Q4'):
    #if value[0] in ('2018Q1'):
        plt.plot(value[2], value[3], '+', color = ico_colors[key], mew=3, ms=6)

for key, value in best_satentry.items():
    #if value[0] in ('2015Q3', '2015Q4', '2016Q1', '2016Q2', '2016Q3', '2016Q4'):
    #if value[0] in ('2017Q1', '2017Q2'):
    if value[0] in ('2017Q3'):
    #if value[0] in ('2017Q4'):
    #if value[0] in ('2018Q1'):
        plt.plot(value[2], value[3], 'x', color = ico_colors[key],mew=3, ms=6)

plt.legend(loc=4)
plt.xlabel('days since exchange listing')
plt.ylabel('sat return multiple')
#plt.title('2015Q3 - 2016Q4')
#plt.title('2017Q1 - 2017Q2')
plt.title('2017Q3')
#plt.title('2017Q4')
#plt.title('2018Q1')
plt.grid()
#plt.yscale('log')
plt.show()


# Plotting coins under different conditions (negative returns)
test_return = {}
test_return = {key: value for key, value in sat_return.items() if key in [x.lower() for x in ['zilliqa', 'Coinfi', 'GatCoin', 'SelfKey'
    , 'Trinity', 'The Key', 'Origin Trail', 'Bluzelle', 'Odyssey', 'WePower', 'datawallet', 'Fusion']]}

plt.axis([0, 50, -3, 35])
ax = plt.axes()
ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
for key, value in test_return.items():
    x, y = zip(*value)
    plt.plot(x,y, label = key, #color = ico_colors[key]
    )

for key, value in max_satreturn.items():
    if key in [x.lower() for x in ['zilliqa', 'Coinfi', 'GatCoin', 'SelfKey'
    , 'Trinity', 'The Key', 'Origin Trail', 'Bluzelle', 'Odyssey', 'WePower', 'datawallet', 'Fusion']]:
        plt.plot(value[0], value[1], '+', #color = ico_colors[key], 
        mew=3, ms=6)

for key, value in best_satentry.items():
    if key in [x.lower() for x in ['zilliqa', 'Coinfi', 'GatCoin', 'SelfKey'
    , 'Trinity', 'The Key', 'Origin Trail', 'Bluzelle', 'Odyssey', 'WePower', 'datawallet', 'Fusion']]:
        plt.plot(value[0], value[1], 'x', #color = ico_colors[key],
        mew=3, ms=6)

plt.legend()
plt.xlabel('days since exchange listing')
plt.ylabel('sat return multiple')
plt.grid()
plt.show()

# best entry below 1x 
test_return = {}
test_return = {key: value for key, value in sat_return.items() if key in [keym for keym, valuem in best_satentry.items() if valuem[1] < 1]}
test_msatreturn = {key: value for key, value in max_satreturn.items() if key in [keym for keym, valuem in best_satentry.items() if valuem[1] < 1]}
test_bsatentry = {key: value for key, value in best_satentry.items() if key in [keym for keym, valuem in best_satentry.items() if valuem[1] < 1]}

plt.axis([0, 75, -2, 20])
ax = plt.axes()
ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
for key, value in test_return.items():
    x, y = zip(*value)
    plt.plot(x,y, label = key, #color = ico_colors[key]
    )

for key, value in test_msatreturn.items():
    plt.plot(value[0], value[1], '+', #color = ico_colors[key], 
    mew=3, ms=6)

for key, value in test_bsatentry.items():
    plt.plot(value[0], value[1], 'x', #color = ico_colors[key],
    mew=3, ms=6)

plt.legend()
plt.xlabel('days since exchange listing')
plt.ylabel('sat return multiple')
plt.grid()
plt.show()


# Plotting Specific lines in different ways as a way to spot check fit 
plt.axis([0, 200, -1, 15])
ax = plt.axes()
ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
for key, value in real_return.items():
    if key in [#real_return better: '0x', 'grid+', 'iexec rlc', 'melon', 'ripio credit network'
    #debatable: 'dragonchain', 'gifto', 'monetha', 'mothership', 'neblio', 'po.et', 'populous', 'wabi', 'wings'
    #sat_return better: 'quantstamp', 'red pulse'
    ]:
        x, y = zip(*value)
        plt.plot(x,y, label = key)
        

for key, value in max_return.items():
    if key in ['0x']:
        plt.plot(value[0], value[1], '+', mew=5, ms=10)


for key, value in sat_return.items():
    if key in [#real_return better: '0x', 'grid+', 'iexec rlc', 'melon', 'ripio credit network'
    #debatable: 'dragonchain', 'gifto', 'monetha', 'mothership', 'neblio', 'po.et', 'populous', 'wabi', 'wings'
    #sat_return better: 'quantstamp', 'red pulse'
    ]:
        x, y = zip(*value)
        plt.plot(x,y, label = key)

        
for key, value in max_satreturn.items():
    if key in ['0x']:
        plt.plot(value[0], value[1], '+', mew=5, ms=10)
        

plt.legend()
plt.xlabel('days since exchange listing')
plt.ylabel('calculated real return multiple')
plt.show()

# Free Plot 
rreturn = {}
rreturn = {key: value for key, value in real_return.items() #if key in [keym for keym, valuem in max_return.items() if valuem[1] >= 4]
}

rtest = collections.defaultdict(list)	
for key, value in rreturn.items():
    #min_reach = max([min([item[0] for item in value if item[1] >= 4]), 10])
    for item in value:
        if item[0] <= 10: 
        #min_reach
            rtest[key].append(item)            

            
local_max = {}
local_max = {key: sorted(value, key=itemgetter(1), reverse = True)[0] for key, value in rtest.items() if key <> 'bitcoin'}
plt.axis([0, 15, -1, 30])
ax = plt.axes()
ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
for key, value in rtest.items():
    #min_reach = max([item[0] for item in value])
    #if min_reach > 30:
    #not in [#outside of 50:
    #'wings', 'cindicator', 'request network', 'red pulse', 'po.et'
    #outside of 30:
    #, 'adex', 'quantstamp', 'decision token'
    #outside of 10:
    #'civic', 'po.et'
    #]:
    x, y = zip(*value)
    plt.plot(x,y, label = key)
    #else:
    #    x, y = zip(*value)
    #    plt.plot(x,y, label = key)
        

for key, value in local_max.items():
    plt.plot(value[0], value[1], '+', mew=5, ms=10)

for key, value in max_return.items():
    plt.plot(value[0], value[1], '+', mew=5, ms=10)
    
plt.legend(loc=4)
plt.xlabel('days since exchange listing')
plt.ylabel('calculated real return multiple')
plt.show()
