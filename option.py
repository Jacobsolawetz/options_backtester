#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 15:27:20 2019
an options class thanks to Fischer and Myron
@author: jacobsolawetz
"""

import math
from scipy.stats import norm
import pandas as pd
from datetime import date
import numpy as np
from utils import *
#%matplotlib inline
'''
EXAMPLE
S = 2584.96
K = 2530
T = 30/365
#time until expiration expressed as a portion of a year
#252
r = .0278819
sigma = .1497
#get_implied_vol('C', K, S, VIX, 0)
o = Option('BUY', 'P', S, K, T, price = None, rf = 0.028, vol = sigma,
                 div = .0)
o.get_price_delta()
o.delta
'''

class Option:
    """
    This class will group the different black-shcoles calculations for an option
    """
    def __init__(self, buy_sell, right, s, k, t, price = None, rf = 0.01, vol = 0.3,
                 div = 0):
        self.k = float(k)
        self.s = float(s)
        self.rf = float(rf)
        self.vol = float(vol)
        self.t = float(t)
        if self.t == 0: self.t = 0.000001 ## Case valuation in expiration date
        self.price = price
        self.right = right   ## 'C' or 'P'
        self.div = div
        self.buy_sell = buy_sell
        
    '''
    def calculate_t(self):
        if isinstance(self.eval_date, basestring):
            if '/' in self.eval_date:
                (day, month, year) = self.eval_date.split('/')
            else:
                (day, month, year) = self.eval_date[6:8], self.eval_date[4:6], self.eval_date[0:4]
            d0 = date(int(year), int(month), int(day))
        elif type(self.eval_date)==float or type(self.eval_date)==long or type(self.eval_date)==np.float64:
            (day, month, year) = (str(self.eval_date)[6:8], str(self.eval_date)[4:6], str(self.eval_date)[0:4])
            d0 = date(int(year), int(month), int(day))
        else:
            d0 = self.eval_date 
 
        if isinstance(self.exp_date, basestring):
            if '/' in self.exp_date:
                (day, month, year) = self.exp_date.split('/')
            else:
                (day, month, year) = self.exp_date[6:8], self.exp_date[4:6], self.exp_date[0:4]
            d1 = date(int(year), int(month), int(day))
        elif type(self.exp_date)==float or type(self.exp_date)==long or type(self.exp_date)==np.float64:
            (day, month, year) = (str(self.exp_date)[6:8], str(self.exp_date)[4:6], str(self.exp_date)[0:4])
            d1 = date(int(year), int(month), int(day))
        else:
            d1 = self.exp_date
 
        return (d1 - d0).days / 365.0
    '''
    
    def get_price_delta(self):
        d1 = ( math.log(self.s/self.k) + ( self.rf + self.div + math.pow( self.vol, 2)/2 ) * self.t ) / ( self.vol * math.sqrt(self.t) )
        d2 = d1 - self.vol * math.sqrt(self.t)
        if self.right == 'C':
            self.calc_price = ( norm.cdf(d1) * self.s * math.exp(-self.div*self.t) - norm.cdf(d2) * self.k * math.exp( -self.rf * self.t ) )
            self.delta = norm.cdf(d1)
            if self.buy_sell == 'SELL':
                self.calc_price = -self.calc_price
                self.delta = -self.delta
                
        elif self.right == 'P':
            self.calc_price =  ( -norm.cdf(-d1) * self.s * math.exp(-self.div*self.t) + norm.cdf(-d2) * self.k * math.exp( -self.rf * self.t ) )
            self.delta = -norm.cdf(-d1)
            if self.buy_sell == 'SELL':
                self.calc_price = -self.calc_price
                self.delta = -self.delta
                
 
    def get_call(self):
        d1 = ( math.log(self.s/self.k) + ( self.rf + math.pow( self.vol, 2)/2 ) * self.t ) / ( self.vol * math.sqrt(self.t) )
        d2 = d1 - self.vol * math.sqrt(self.t)
        self.call = ( norm.cdf(d1) * self.s - norm.cdf(d2) * self.k * math.exp( -self.rf * self.t ) )
        #put =  ( -norm.cdf(-d1) * self.s + norm.cdf(-d2) * self.k * math.exp( -self.rf * self.t ) ) 
        self.call_delta = norm.cdf(d1)
 
 
    def get_put(self):
        d1 = ( math.log(self.s/self.k) + ( self.rf + math.pow( self.vol, 2)/2 ) * self.t ) / ( self.vol * math.sqrt(self.t) )
        d2 = d1 - self.vol * math.sqrt(self.t)
        #call = ( norm.cdf(d1) * self.s - norm.cdf(d2) * self.k * math.exp( -self.rf * self.t ) )
        self.put =  ( -norm.cdf(-d1) * self.s + norm.cdf(-d2) * self.k * math.exp( -self.rf * self.t ) )
        self.put_delta = -norm.cdf(-d1) 
 
     
    #we could redo with black scholes greek
    def get_theta(self, dt = 0.0027777):
        self.t += dt
        self.get_price_delta()
        after_price = self.calc_price
        self.t -= dt
        self.get_price_delta()
        orig_price = self.calc_price
        self.theta = (after_price - orig_price) * (-1)
        if self.buy_sell == 'SELL':
            self.theta = -self.theta
 
 
    def get_gamma(self, ds = 0.01):
        self.s += ds
        self.get_price_delta()
        after_delta = self.delta
        self.s -= ds
        self.get_price_delta()
        orig_delta = self.delta
        self.gamma = (after_delta - orig_delta) / ds
        if self.buy_sell == 'SELL':
            self.gamma = -self.gamma
        
    def get_vega(self, dv = 0.0002):
        self.vol += dv
        self.get_price_delta()
        after_price = self.calc_price
        self.vol -= dv
        self.get_price_delta()
        orig_price = self.calc_price
        self.vega = ((after_price - orig_price) / dv) / 100
        if self.buy_sell == 'SELL':
            self.vega = -self.vega
 
    def get_all(self):
        self.get_price_delta()
        self.get_theta()
        self.get_gamma()
        self.get_vega()
        return self.calc_price, self.delta, self.theta, self.gamma, self.vega
    
    def get_k(self):
        return self.k
    
    def __str__(self):
        return self.right + " - " + str(self.k) + " - " + self.buy_sell