#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 21:52:32 2019

@author: jacobsolawetz
"""
import warnings
#toggle pandas future warnings off
warnings.filterwarnings('ignore')
from backtester import Backtester
from visualizer import Visualizer

backtest_name = 'classic'
strategy = [['P', 1.0, 'SELL']]
#backtest_type = 'normal'
backtest_type = 'normal'
roll_day = 10
leverage = 3


tester = Backtester(roll_day, strategy, leverage, backtest_type)
tester.load_data()
tester.set_up_calendar()
tester.get_roll_days()
tester.backtest()

viz = Visualizer(tester.results,backtest_name)
viz.save_figs()
viz.print_results()
