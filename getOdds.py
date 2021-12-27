import requests
import json
from datetime import datetime
import pandas as pd
import numpy as np
from bonusOptimization import HelperFunctions, BonusOptimizer

API_KEY = '40d34a48ad1e319afa1275787cab0c61'
baseurl = 'https://api.the-odds-api.com'
sport = 'americanfootball_ncaaf'
regions = 'us,eu'
oddsFormat = 'american'
markets = 'h2h'
getsports_url = f'/v4/sports/{sport}/odds?regions={regions}&oddsFormat={oddsFormat}&markets={markets}&apiKey={API_KEY}'
response = json.loads(requests.request(method='GET',url=baseurl+getsports_url).text)

outer_list = []
book_list = ['FanDuel','draftkings','betmgm','wynnbet','pinnacle','betrivers','twinspires','barstool','pointsbetus','williamhill_us']
for resp in response:
    home_team = resp['home_team']
    away_team = resp['away_team']
    common_keys = ({
        'id': resp['id'],
        'commence_time': datetime.strptime(resp['commence_time'],'%Y-%m-%dT%H:%M:%SZ'),
        'sport_title': resp['sport_title'],
        'home_team': resp['home_team'],
        'away_team': resp['away_team'],
        'bookmaker': 'barstool',
        'odds_home': 350,
        'odds_away': -200
    })
    for book in resp['bookmakers']:
        if book['key'] in book_list:
            row = common_keys.copy()
            row['bookmaker'] = book['key']
            row['odds_home'] = book['markets'][0]['outcomes'][0]['price'] if book['markets'][0]['outcomes'][0]['name'] == home_team else book['markets'][0]['outcomes'][1]['price']
            row['odds_away'] = book['markets'][0]['outcomes'][1]['price'] if book['markets'][0]['outcomes'][1]['name'] == away_team else book['markets'][0]['outcomes'][0]['price']
            row['dog_odds'] = max(row['odds_home'],row['odds_away'])
            row['fav_odds'] = min(row['odds_home'],row['odds_away'])
            row['dog_team'] = home_team if row['odds_home'] > row['odds_away'] else away_team
            row['fav_team'] = home_team if row['odds_home'] < row['odds_away'] else away_team
            outer_list.append(row)

main = pd.DataFrame(outer_list)
pinnacle = main[main.bookmaker == 'pinnacle'].copy()
pinnacle['dog_fairodds'] = pinnacle.apply(lambda x: HelperFunctions.fairOdds(x.dog_odds,x.fav_odds)['odds1'],axis=1)
pinnacle['fav_fairodds'] = pinnacle.apply(lambda x: HelperFunctions.fairOdds(x.dog_odds,x.fav_odds)['odds2'],axis=1)
pinnacle.head()

def get_dogFairOdds(x):
    if x.id in pinnacle.id.values:
        dog_fairodds = float(pinnacle[pinnacle.id==x.id].dog_fairodds.values)
    else:
        dog_fairodds = np.nan
    return dog_fairodds
def get_favFairOdds(x):
    if x.id in pinnacle.id.values:
        fav_fairodds = float(pinnacle[pinnacle.id == x.id].fav_fairodds.values)
    else:
        fav_fairodds = np.nan
    return fav_fairodds
main['dog_fairodds'] = main.apply(lambda x: get_dogFairOdds(x),axis=1)
main['fav_fairodds'] = main.apply(lambda x: get_favFairOdds(x),axis=1)
main.dropna(inplace=True)
main['dog_ev'] = main.apply(lambda x: HelperFunctions.EVgivenFairOdds(x.dog_odds,x.dog_fairodds),axis=1)
main['fav_ev'] = main.apply(lambda x: HelperFunctions.EVgivenFairOdds(x.fav_odds,x.fav_fairodds),axis=1)
main.reset_index(inplace=True,drop=True)

rows_final = []
for index,row in main.iterrows():
    row1 = ({
        'id': row['id'],
        'game_name': f"{row['home_team']} @ {row['away_team']}",
        'commence_time': row['commence_time'],
        'sport_title': row['sport_title'],
        'betname': f"{row['dog_team']} {row['dog_odds']}",
        'bookmaker': row['bookmaker'],
        'team': row['dog_team'],
        'odds': row['dog_odds'],
        'fairodds': row['dog_fairodds'],
        'ev': row['dog_ev']
    })
    row2 = ({
        'id': row['id'],
        'game_name': f"{row['home_team']} @ {row['away_team']}",
        'commence_time': row['commence_time'],
        'sport_title': row['sport_title'],
        'betname': f"{row['fav_team']} {row['fav_odds']}",
        'bookmaker': row['bookmaker'],
        'team': row['fav_team'],
        'odds': row['fav_odds'],
        'fairodds': row['fav_fairodds'],
        'ev': row['fav_ev']
    })
    rows_final.append(row1)
    rows_final.append(row2)
betdf = pd.DataFrame(rows_final)