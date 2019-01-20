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

'''DATA STRUCTURES'''
valid_strings = {
    'option_type': ['P', 'C'],
    'right': ['SELL', 'BUY'],
    'your decision': ['Y', 'N'],
    'your backtest type': ['normal', 'constant_margin']
}

inputs = []


'''FUNCTIONS'''
def get_str_input(parameter, name):
    while parameter == None:
        parameter = input('What is the ' + name + '?\n')
        if parameter not in valid_strings[name]:
            print('That is invalid. Your options are ', valid_strings[name])
            parameter = None
    
    inputs.append(parameter)
    return parameter

def get_int_input(parameter, name):
    while parameter == None:
        parameter = input('What is the ' + name + '?\n')
        try:
            parameter = float(parameter)
        except:
            print('That was not a number. Please enter a number.')
            parameter = None
    inputs.append(parameter)
    return parameter

def print_portfolio(p):
    print('\nBacktesting a portfolio of {} option(s)'.format(len(p)))
    option_num = 1
    for o in p:
        print('Option', option_num)
        print('\tOption: {}\n\tZ-Scores Out: {}\n\tLong or Short: {}'.format(*o))
        option_num += 1
    print()

#backtest_name = '2_scores_constantmargin_8x' DELETE THIS LATER
done = False

'''PORTFOLIO VARIABLES'''
strategy    = []
option_type = None
zscore      = None
right       = None
decision    = None
leverage    = None
backtest_type = None

print('Input the first option for your portfolio.\n')
while not done:
    option_type = get_str_input(option_type, 'option_type')
    zscore     = get_int_input(zscore, 'zscore')
    right       = get_str_input(right, 'right')
    strategy.append([option_type, zscore, right])
    print('\nYou can still add more options.\n')
    if get_str_input(decision, 'your decision') == 'Y':
        option_type = None
        zscore     = None
        right       = None
    else:
        done = True

backtest_type = get_str_input(backtest_type, 'your backtest type')
inputs.append(backtest_type)
leverage = get_int_input(leverage, 'leverage')
inputs.append(leverage)

print_portfolio(strategy)

#strategy = [['P', 2.0, 'SELL']]
#backtest_type = 'normal'
#backtest_type = 'constant_margin'
roll_day = 10
#leverage = 8


backtest_name = '{}_scores_{}_{}'.format(zscore, backtest_type, leverage)
tester = Backtester(roll_day, strategy, leverage, backtest_type)
tester.load_data()
tester.set_up_calendar()
tester.get_roll_days()
tester.backtest()

viz = Visualizer(tester.results,backtest_name)
viz.save_figs()
viz.print_results()

f = open('repeat', 'w')

for _input in inputs:
    f.write(str(_input))
    f.write('\n')

f.close()
print('`python input_run_bt.py < repeat` will repeat this backtest')



