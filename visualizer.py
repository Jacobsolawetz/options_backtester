#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 15:35:11 2019

@author: jacobsolawetz
"""
from matplotlib.backends.backend_pdf import PdfPages
import os


class Visualizer:
    def __init__(self,results, backtest_name):
        self.results = results
        self.backtest_name = backtest_name
        
    def save_figs(self):
        pp = PdfPages("output/" + self.backtest_name + '.pdf')
        
        viz_df = self.results
        ax = viz_df[['daily_returns_cumulative']].plot()
        ax.set_title('daily_returns_cumulative')
        ax.set_ylabel('x-return')
        fig = ax.get_figure()
        pp.savefig(fig)
        fig.clear()
        
        ax = viz_df.groupby('roll_period')['roll_cumulative_return_raw'].last().hist(bins=40)
        ax.set_title('histogram of roll returns')
        fig = ax.get_figure()
        pp.savefig(fig)
        fig.clear()
        
        
        ax = viz_df['margin_pct'].round(2).plot()
        ax.set_title('margin_vizualization')
        ax.set_ylabel('percent_margin_call')
        fig = ax.get_figure()
        pp.savefig(fig)
        fig.clear()
        
        

        
        
        pp.close()
        return None
        
    def print_results(self):
        print_df = self.results
        text_file = open("output/" + self.backtest_name + ".txt", "w")
        max_roll_drawdown = print_df.groupby('roll_period')['roll_cumulative_return_raw'].last().min()
        max_intra_roll_drawdown = print_df['roll_cumulative_return_raw'].min()
        max_daily_drawdown = print_df['portfolio_returns_raw'].min()
        text_file.write("max roll drawdown :" + str(max_roll_drawdown) + "\n\n")
        text_file.write("max intra roll drawdown :" + str(max_intra_roll_drawdown) + "\n\n")
        text_file.write("max daily drawdown :" + str(max_daily_drawdown) + "\n\n")

        
        text_file.close()
        
        print_df.to_csv("output/" + self.backtest_name + ".csv")
        return None
        
        
        
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