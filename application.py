from flask import Flask, app, request
from flask_cors import CORS
import json
from bonusOptimization import HelperFunctions, BonusOptimizer

application = Flask(__name__)
CORS(application)

@application.route('/',methods=['GET'])
def index():
    return {"message": "Sign up bonus base path"}


'''
Available calculations on /calculations path:

Calculate Vig: Determine how much the sportsbook/s are witholding from a given bet. If using two different books for a bet, this can be negative. 

Convert Odds: Currently only converts between American and Fractional. American's are used to seeing odds in American format, but fractional
              is the easiest to work with.

Calculate Fair odds: Determine what the "fair" odds are for a given bet. By taking the Pinnacle odds, and removing the vig, we can determine 
                     what Pinnacle (assumed best sportsbook) thinks the actual probability of an event occuring is. 

Calculate other odds given vig: This calculation is useful for optimizing the expected value of a Risk Free or Bonus Match Sportsbook Sign-up bonus

Calculate EV given fair odds: This calculation returns the expected value (based on a $1 bet) of a given bet relative to the fair odds (the actual
                                the actual implied probability of winning the bet)
'''

@application.route('/calculations/calculateVig', methods=['GET'])
def calculateVig():
    params = request.args['odds']
    params = params.split(',')
    odds1,odds2 = (int(i) for i in params)
    vig = HelperFunctions.calculateVig(odds1,odds2)
    return {"value": vig}

@application.route('/calculations/convertOdds', methods=['GET'])
def convertOdds():
    params = request.args
    if params['format'] == 'american':
        odds = int(params['odds'])
        new_odds = HelperFunctions.americanToFractional(odds)
    else:
        odds = float(params['odds'])
        new_odds = HelperFunctions.fractionalToAmerican(odds)
    return {"value":new_odds}

@application.route('/calculations/calculateFairOdds', methods=['GET'])
def calculateFairOdds():
    params = request.args['odds']
    params = params.split(',')
    odds1,odds2 = (int(i) for i in params)
    fair_odds = HelperFunctions.fairOdds(odds1,odds2)
    return {"value": fair_odds}

@application.route('/calculations/calculateOtherOddsGivenVig', methods=['GET'])
def calculateOtherOddsGivenVig():
    params = request.args
    odds = int(params['odds'])
    vig = float(params['vig'])
    return {"value": HelperFunctions.otherOddsGivenVig(odds,vig)}

@application.route('/calculations/calculateEVGivenFairOdds', methods=['GET'])
def calculateEVGivenFairOdds():
    params = request.args
    odds = int(params['odds'])
    fairOdds = int(params['fairOdds'])
    return {"value": HelperFunctions.EVgivenFairOdds(odds,fairOdds)}

@application.route('/betOptimizer/RiskFreeBet', methods=['GET'])
def getRFBetEV():
    params = request.args
    stake = float(params['stake'])
    odds1 = int(params['odds1'])
    odds2 = int(params['odds2'])
    try:
        freeBetConversion = float(params['freeBetConversion'])
    except:
        freeBetConversion = 0.65
    return BonusOptimizer.RFBetEV(stake, odds1, odds2, freeBetConversion)

@application.route('/betOptimizer/BonusMatch', methods=['GET'])
def getBonusMatchEV():
    params = request.args
    stake = float(params['stake'])
    odds1 = int(params['odds1'])
    odds2 = int(params['odds2'])
    try:
        freeBetConversion = float(params['freeBetConversion'])
    except:
        freeBetConversion = 0.65

    return BonusOptimizer.BonusMatchEV(stake, odds1, odds2, freeBetConversion)

if __name__ == '__main__':
    application.run(debug=True)
