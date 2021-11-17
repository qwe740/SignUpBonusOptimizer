from flask import Flask, request
import json
import numpy as np
from bonusOptimization import HelperFunctions, BonusOptimizer

app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    return {"message": "Sign up bonus base path"}

@app.route('/calculations/VigCalculator',methods=['GET'])
def calculateVig():
    params = json.loads(request.args['json'])
    odds1,odds2 = (int(i) for i in params['odds'])
    vig = HelperFunctions.calculateVig(odds1,odds2)
    return vig

@app.route('/calculations/oddsConverter', methods=['GET'])
def convertOdds():
    params = json.loads(request.args)
    odds = params['odds']
    if params['format'] == 'american':
        new_odds = HelperFunctions.americanToFractional(odds)
    else:
        new_odds = HelperFunctions.fractionalToAmerican(odds)
    return new_odds

if __name__ == '__main__':
    app.run()
