import numpy as np
from scipy import optimize
class HelperFunctions:

    @staticmethod
    def americanToFractional(odds):
        if odds < 0:
            fodds = -100/odds
        else:
            fodds = odds/100
        return fodds

    @staticmethod
    def fractionalToAmerican(fodds):
        if fodds < 1:
            odds = -100/fodds
        else:
            odds = fodds*100
        return odds

    @classmethod
    def calculateVig(cls,odds1,odds2):
        fodds1 = cls.americanToFractional(odds1)
        fodds2 = cls.americanToFractional(odds2)
        winperc1 = 1/(fodds1+1)
        winperc2 = 1/(fodds2+2)
        vig = winperc1+winperc2-1
        return vig

    @classmethod
    def otherOddsGivenVig(cls,odds,vig):
        fodds = cls.americanToFractional(odds)
        winperc = 1/(fodds+1)
        winperc2 = vig - winperc + 1
        fodds2 = (1 / winperc2) - 1
        odds2 = cls.fractionalToAmerican(fodds2)
        return round(odds2)

class BonusOptimizer:
    
    @staticmethod
    def RFBetEV(stake,odds1,odds2,freebetconversion=0.65):
        fodds1 = HelperFunctions.americanToFractional(odds1)
        fodds2 = HelperFunctions.americanToFractional(odds2)
        def ifloss(stake2,*args):
            fodds2 = args[0]
            stake = args[1]
            freebetconversion = args[2]
            return (stake2*fodds2 - stake + stake*freebetconversion)
        stake2 = optimize.newton(ifloss,100,args=(fodds2,stake,freebetconversion))
        ifwin = stake*fodds1 - stake2
        percwin = 1/(fodds1+1)
        ev = percwin*ifwin
        return {"hedge_size": stake2, "expected_value": ev}
    
    @staticmethod
    def BonusMatchEV(stake,odds1,odds2,freebetconversion=0.65):
        fodds1 = HelperFunctions.americanToFractional(odds1)
        fodds2 = HelperFunctions.americanToFractional(odds2)
        def ifloss(stake2,*args):
            fodds2 = args[0]
            stake = args[1]
            freebetconversion = args[2]
            return (stake2*fodds2 - stake + stake*freebetconversion)
        stake2 = optimize.newton(ifloss,100,args=(fodds2,stake,freebetconversion))
        ifwin = stake*fodds1 + stake*freebetconversion - stake2
        percwin = 1/(fodds1+1)
        ev = percwin*ifwin
        return {"hedge_size": stake2, "expected_value":ev}