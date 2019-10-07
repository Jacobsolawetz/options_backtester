#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 21:52:32 2019

@author: jacobsolawetz
"""

#when we vary the roll day much different behavior occurs...
#to do: add in a market shift by day parameter. As if the market ran in an alternative time series.
#this disambiguates the fact that roll_day 5 is closer to expiration and delta pops up.
    
import warnings
#toggle pandas future warnings off
warnings.filterwarnings('ignore')
from backtester import Backtester
from visualizer import Visualizer
from visualizer_multi_roll import Visualizer_Multi_Roll

backtest_name = '15x_2.0_ml60_fan_out_rolls'
#in order to do constant_margin now we need to also write the bought call in there with arbitrary z-score
strategy = [['P', 2.0, 'SELL'], ['P', 2.0, 'BUY']]
#backtest_type = 'normal'
backtest_type = 'constant_margin'
#roll_day = 14
leverage = 15
max_loss = .6


#tester = Backtester(roll_day, strategy, leverage, backtest_type, max_loss)
#tester.load_data()
#tester.set_up_calendar()
#tester.get_roll_days()
#tester.backtest()


tester_results = []
for roll_day in [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
#for roll_day in [5,10]:
    tester = Backtester(roll_day, strategy, leverage, backtest_type, max_loss)
    tester.load_data()
    tester.set_up_calendar()
    tester.get_roll_days()
    tester.backtest()
    tester_results.append(tester.results)
    print('backtested roll day ' + str(roll_day))

viz = Visualizer_Multi_Roll(tester_results, backtest_name)
viz.save_figs()

#viz = Visualizer(tester.results,backtest_name)
#viz.save_figs()
#viz.print_results()
