#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 15:35:11 2019

@author: jacobsolawetz
"""
from matplotlib.backends.backend_pdf import PdfPages
import os
import matplotlib.pyplot as plt
import pandas as pd

class Visualizer_Multi_Roll:
    def __init__(self,tester_results,backtest_name):
        #use first results as a skeleton
        self.results = tester_results[0]
        self.backtest_name = backtest_name
        for result in tester_results[1:]:
            #average portfolio metrics
            self.results['portfolio_returns_raw'] = self.results['portfolio_returns_raw'] + result['portfolio_returns_raw']
            self.results['portfolio_delta'] = self.results['portfolio_delta'] + result['portfolio_delta']
            self.results['margin_pct'] = self.results['margin_pct'] + result['margin_pct']
        #averaging, assumes each of the puts have the same capital allocated
        self.results['portfolio_returns_raw'] = self.results['portfolio_returns_raw'] / len(tester_results)
        self.results['portfolio_delta'] = self.results['portfolio_delta'] / len(tester_results)
        self.results['margin_pct'] = self.results['margin_pct'] / len(tester_results)
        
        self.results['daily_returns_cumulative'] = (self.results['portfolio_returns_raw'] + 1).cumprod()
        self.results['spy_returns_cumulative'] = (self.results['spy_return'] + 1).cumprod()



        
        
        
    def save_figs(self):
        pp = PdfPages("output/" + self.backtest_name + '.pdf')
        
        viz_df = self.results
        ax = viz_df[['daily_returns_cumulative']].plot()
        ax.set_title('daily_returns_cumulative')
        ax.set_ylabel('x-return')
        fig = ax.get_figure()
        pp.savefig(fig)
        fig.clear()
        print(list(viz_df))
        
        viz_df = viz_df.reset_index()
        monthly_returns = (viz_df.groupby(viz_df['date'].dt.to_period("M") )['daily_returns_cumulative'].last() / viz_df.groupby(viz_df['date'].dt.to_period("M"))['daily_returns_cumulative'].last().shift(1).fillna(1)) - 1
        ax = monthly_returns.hist(bins = 40)
        ax.set_title('histogram of monthly returns')
        fig = ax.get_figure()
        pp.savefig(fig)
        fig.clear()
        
        
        yearly_returns = (viz_df.groupby(viz_df['date'].dt.year)['daily_returns_cumulative'].last() / viz_df.groupby(viz_df['date'].dt.year)['daily_returns_cumulative'].last().shift(1).fillna(1)) - 1
        yearly_spy_returns = (viz_df.groupby(viz_df['date'].dt.year)['spy_returns_cumulative'].last() / viz_df.groupby(viz_df['date'].dt.year)['spy_returns_cumulative'].last().shift(1).fillna(1)) - 1
        yearly_df = pd.concat([yearly_returns, yearly_spy_returns], axis = 1)
        yearly_df.columns = ['strategy','SPY']
        ax = yearly_df.plot.bar()
        ax.set_title('yearly returns')
        ax.set_ylabel('pct return')
        plt.grid()
        fig = ax.get_figure()
        pp.savefig(fig)
        fig.clear()
        
        viz_df = viz_df.set_index('date')
        ax = viz_df['margin_pct'].round(2).plot()
        ax.set_title('margin_visualization')
        ax.set_ylabel('percent_margin_call')
        fig = ax.get_figure()
        pp.savefig(fig)
        fig.clear()
        
        #ax = viz_df.groupby('roll_period')['portfolio_delta'].first().plot()
        #ax.set_title('roll_deltas')
        #ax.set_ylabel('delta')
        #fig = ax.get_figure()
        #pp.savefig(fig)
        #fig.clear()
        
        ax = viz_df['portfolio_delta'].hist(bins=40)
        ax.set_title('portfolio_delta histogram')
        ax.set_ylabel('delta')
        fig = ax.get_figure()
        pp.savefig(fig)
        fig.clear()
        

        
        pp.close()
        return None
        
# =============================================================================
#     def print_results(self):
#         print_df = self.results
#         text_file = open("output/" + self.backtest_name + ".txt", "w")
#         max_roll_drawdown = print_df.groupby('roll_period')['roll_cumulative_return_raw'].last().min()
#         max_intra_roll_drawdown = print_df['roll_cumulative_return_raw'].min()
#         max_daily_drawdown = print_df['portfolio_returns_raw'].min()
#         text_file.write("max roll drawdown :" + str(max_roll_drawdown) + "\n\n")
#         text_file.write("max intra roll drawdown :" + str(max_intra_roll_drawdown) + "\n\n")
#         text_file.write("max daily drawdown :" + str(max_daily_drawdown) + "\n\n")
# 
#         
#         text_file.close()
#         
#         print_df.to_csv("output/" + self.backtest_name + ".csv")
#         return None
# =============================================================================
        
        
        
'''
df['roll_period'] = df['roll_date'].shift(1)
#returns for each roll
#we can use a similar method to get roll deltas, ect. 
df.groupby('roll_period')['roll_cumulative_return_raw'].last().hist(bins=40)

#max roll drawdown
df.groupby('roll_period')['roll_cumulative_return_raw'].last().min()

#mean roll return
df.groupby('roll_period')['roll_cumulative_return_raw'].last().mean()

#max intra roll drawdown
df['roll_cumulative_return_raw'].min()

#max daily drawdown
df['portfolio_returns_raw'].min()

#mean daily return
df['portfolio_returns_raw'].mean()

df = df.reset_index()
yearly_returns = (df.groupby(df['date'].dt.year)['daily_returns_cumulative'].last() / df.groupby(df['date'].dt.year)['daily_returns_cumulative'].last().shift(1).fillna(1)) - 1
yearly_returns.plot.bar()

#yearly return
yearly_return = math.pow(df['daily_returns_cumulative'].iloc[-1], 1/((df['date'].iloc[-1] - df['date'].iloc[0]).days / 365)) - 1
#yearly std
yearly_std = df.groupby('roll_period')['roll_cumulative_return_raw'].last().std()*math.sqrt(12)
#sharpe ratio
(yearly_return - .031) / yearly_std 
df['portfolio_returns_raw'].hist(bins = 300)


df['portfolio_delta'].hist(bins=40)

df.set_index('date')['portfolio_delta'].plot()

df['portfolio_theta'].hist()
#roll deltas
df.groupby('roll_period')['portfolio_delta'].first().hist(bins=40)


#we could imagine where we set a strike based on delta not Z-score
df.groupby('roll_period')['portfolio_delta'].first().plot()


df.groupby('roll_period')['portfolio_theta'].first().hist(bins=40)
'''