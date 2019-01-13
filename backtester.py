#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 15:30:51 2019

@author: jacobsolawetz
"""

#load in spy, vix, skew data
import pandas_market_calendars as mcal
import warnings
#toggle pandas future warnings off
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import sqlite3
from option import Option
from utils import *



class Backtester:
    
    def __init__(self,roll_day, strategy, leverage):
        self.roll_day = roll_day
        self.strategy = strategy
        self.leverage = leverage
        
        
    def load_data(self):
        #loads in historical dail spy, skew, and vix data from the cboe
        market_prices = pd.read_csv('Spy_Vix_Skew_Data.csv')
        market_prices['DATE'] = pd.to_datetime(market_prices['DATE'])
        market_prices['SPY'] = pd.to_numeric(market_prices['SPY'])
        market_prices['VIX'] = pd.to_numeric(market_prices['VIX'])
        market_prices['SKEW'] = pd.to_numeric(market_prices['SKEW'])
        self.market_prices = market_prices
        print('historical data loaded')
        return None
    
    def set_up_calendar(self):
        #roll parameter expressed in trading days before contract is due
        cme = mcal.get_calendar('CME')
        start_day = '1990-1-1'
        end_day = '2019-1-1'
        schedule = cme.schedule(start_date = start_day, end_date = end_day)
        schedule = schedule.reset_index()
        schedule = schedule.rename(index=str, columns={"index": "date"})
        #join in market data onto the trading days skeleton
        bt_df = schedule.set_index('date').join(self.market_prices.set_index('DATE'), how = 'left')
        #for n/a dates fill from the previous close
        bt_df = bt_df.fillna(method='ffill')
        bt_df = bt_df[~bt_df['SPY'].isnull()]
        bt_df = bt_df.reset_index()
        bt_df = bt_df.rename(index=str, columns={"index": "date"})
        bt_df['VIX'] = pd.to_numeric(bt_df['VIX'])
        bt_df = bt_df.drop(['market_open', 'market_close'], axis = 1)
        self.bt_df = bt_df
        print('calendar set ' + start_day + ' to ' + end_day)
        return None

    def get_roll_days(self):
        bt_df = self.bt_df
        third_friday = bt_df[bt_df['date'].apply(is_third_friday)]
        third_friday['next_expiration'] = third_friday['date'].shift(-1)
        #find roll dates from schedule
        third_friday['roll_date'] = list(bt_df[bt_df.index.isin([ str(int(x) - self.roll_day) for  x in list(third_friday.index)])]['date'])
        third_friday['next_roll_date'] = third_friday['roll_date'].shift(-1)
        #find what the market was like on that roll_day
        third_friday['SPY'] = list(bt_df[bt_df.index.isin([ str(int(x) - self.roll_day) for  x in list(third_friday.index)])]['SPY'])
        third_friday['VIX'] = list(bt_df[bt_df.index.isin([ str(int(x) - self.roll_day) for  x in list(third_friday.index)])]['VIX'])
        third_friday['SKEW'] = list(bt_df[bt_df.index.isin([ str(int(x) - self.roll_day) for  x in list(third_friday.index)])]['SKEW'])
        third_friday['days_to_expir'] =  (third_friday['next_expiration'] - third_friday['roll_date']).dt.days
        third_friday = third_friday[~third_friday['days_to_expir'].isnull()]

        conn = sqlite3.connect(':memory:')
        #massage datetypes
        bt_df.to_sql('bt',conn, index = False)
        third_friday.to_sql('tf', conn, index = False)
        qry = """select 
                    bt.*, tf.next_expiration, tf.days_to_expir as roll_days_to_expir, tf.roll_date, tf.next_roll_date,
                    tf.SPY as roll_SPY, tf.VIX as roll_VIX, tf.SKEW as roll_SKEW
                from bt
                left join
                tf on bt.date >= tf.roll_date and bt.date < tf.next_roll_date"""
        df = pd.read_sql_query(qry,conn)
        df['next_expiration'] = pd.to_datetime(df['next_expiration'])
        df['roll_date'] = pd.to_datetime(df['roll_date'])
        df['next_roll_date'] = pd.to_datetime(df['next_roll_date'])
        df['date'] = pd.to_datetime(df['date'])
        df['days_to_expir'] =  (df['next_expiration'] - df['date']).dt.days
        df = df[~df['next_expiration'].isnull()]
        #now the backtest framework is set up
        self.df = df
        return None


    def backtest(self):
        
        #now we want to loop through and create options objects that we bought and sold at the roll
        rolled_options = []
        rolled_strikes = []
        rolled_prices = []
        df = self.df
        for index, row in df.iterrows():
            #hardcoding 2 as risk free rate for now
            options_rolled = []
            option_strikes = []
            option_prices = []
            for option in self.strategy:
                option_type = option[0]
                zscore = option[1]
                buy_sell = option[2]
                #30 delta put
                #problem is we don't know implied vol until we define strike
                #don't know strike until we get implied vol
                #strike = strike_from_delta(row['roll_SPY'],row['roll_days_to_expir']/365,.01,row['roll_VIX']/100,.30,option_type)
                strike = calculate_strike(option_type, row['roll_SPY'], row['roll_VIX'], zscore)
                implied_vol = get_implied_vol(option_type, strike, row['roll_SPY'], row['roll_VIX'], row['roll_SKEW'])    
                o = Option(buy_sell, option_type, row['roll_SPY'], strike, row['roll_days_to_expir']/365, None, .01, implied_vol/100, 0.03)
                o.get_price_delta()
                options_rolled.append([o])
                option_strikes.append(strike)
                option_prices.append(o.calc_price)
            rolled_options.append(options_rolled)
            rolled_strikes.append(option_strikes)
            rolled_prices.append(option_prices)
        df['rolled_options'] = rolled_options
        df['rolled_strikes'] = rolled_strikes
        df['rolled_prices'] = rolled_prices
        df['previous_rolled_strikes'] = df['rolled_strikes'].shift(1)
        df['previous_rolled_strikes'] = df['previous_rolled_strikes'].fillna(method = 'bfill')
        df['previous_days_to_expir'] = (df['next_expiration'].shift(1).fillna(method = 'bfill') - df['date']).dt.days
        #now we create a time series of the same options measured as time decays and the market moves
        options_list = []
        prices_list = []
        delta_list = []
        vega_list = []
        theta_list = []
        gamma_list = []
        portfolio_prices = []
        portfolio_deltas = []
        portfolio_vegas = []
        portfolio_thetas = []
        portfolio_gammas = []
        previous_option_price = []
        
        for index, row in df.iterrows():
            #hardcoding 2 as risk free rate for now
            options = []
            prices = []
            deltas = []
            vegas = []
            thetas = []
            gammas = []
            previous_rolled_option_price = []
            for i, option in enumerate(self.strategy):
                
                option_type = option[0]
                zscore = option[1]
                buy_sell = option[2]
                strike = row['rolled_strikes'][i]
                implied_vol = get_implied_vol(option_type, strike, row['SPY'], row['VIX'], row['SKEW'])    
                o = Option(buy_sell, option_type, row['SPY'], strike, row['days_to_expir']/365, None, .02, implied_vol/100, 0.03)
                o.get_price_delta()
                options.append([o])
                prices.append(o.calc_price)
                deltas.append(o.delta)
                o.get_vega()
                vegas.append(o.vega)
                o.get_theta()
                thetas.append(o.theta)
                o.get_gamma()
                gammas.append(o.gamma)
                
                ##caculate price on previously rolled option
                ##if backtester is too slow we could add in a codition that it must be roll to caculate, otherwise previous option = current option
                previous_strike = row['previous_rolled_strikes'][i]
                previous_implied_vol = get_implied_vol(option_type, previous_strike, row['SPY'], row['VIX'], row['SKEW']) 
                o_previous = Option(buy_sell, option_type, row['SPY'], previous_strike, row['previous_days_to_expir']/365, None, .02, previous_implied_vol/100, 0.03)
                o_previous.get_price_delta()
                previous_rolled_option_price.append(o_previous.calc_price)
                
                
            previous_option_price.append(previous_rolled_option_price)
            options_list.append(options)
            prices_list.append(prices)
            delta_list.append(deltas)
            vega_list.append(vegas)
            theta_list.append(thetas)
            gamma_list.append(gammas)
            #averages for portfolio attributes
            portfolio_price = sum(prices)/float(len(prices))
            portfolio_delta = sum(deltas)/float(len(deltas))
            portfolio_vega = sum(vegas)/float(len(vegas))
            portfolio_theta = sum(thetas)/float(len(thetas))
            portfolio_gamma = sum(gammas)/float(len(gammas))
            portfolio_prices.append(portfolio_price)
            portfolio_deltas.append(portfolio_delta)
            portfolio_vegas.append(portfolio_vega)
            portfolio_thetas.append(portfolio_theta)
            portfolio_gammas.append(portfolio_gamma)
        
        df['previous_option_current_price'] = previous_option_price
        df['options'] = options_list
        df['prices'] = prices_list
        df['deltas'] = delta_list
        df['vegas'] = vega_list
        df['thetas'] = theta_list
        df['gammas'] = gamma_list
        df['portfolio_price'] = portfolio_prices
        df['portfolio_delta'] = portfolio_deltas
        df['portfolio_vega'] = portfolio_vegas
        df['portfolio_theta'] = portfolio_thetas
        df['portfolio_gamma'] = portfolio_gammas

        df['previous_prices'] = df['prices'].shift(1)
        df['previous_prices'] = df['previous_prices'].fillna(method = 'bfill')


        returns_list = []
        portfolio_returns = []
        for index, row in df.iterrows():
            returns = []
            for i, option in enumerate(self.strategy):
                if i == 0:
                    #log the put's stike to calculate other returns and leverage from
                    #key assumption - all leverage revolves around the sold put
                    previous_rolled_strike = row['previous_rolled_strikes'][i]
                current_price = row['previous_option_current_price'][i]
                previous_price = row['previous_prices'][i]
                ret = (current_price - previous_price)/previous_rolled_strike
                returns.append(ret)
            returns_list.append(returns)
            portfolio_return = sum(returns)
            portfolio_returns.append(portfolio_return)
        
        df['returns_list'] = returns_list
        df['portfolio_returns_raw'] = portfolio_returns
        #Lever
        df['portfolio_returns_raw'] = df['portfolio_returns_raw'] * 3
        #lever other portfolio metrics as well like greeks
        
        #cum_sum of returns within roll period
        df['roll_period'] = df['roll_date'].shift(1)
        df['roll_period'] = df['roll_period'].fillna(method = 'bfill')
        df['next_roll_period'] = df['next_roll_date'].shift(1)
        df['next_roll_period'] = df['next_roll_period'].fillna(method = 'bfill')
    
        df['roll_cumulative_return_raw'] = df.groupby('roll_period')['portfolio_returns_raw'].cumsum()

        #here we start each roll out with the cumulative returns of rolls before it

        cum_rolls = (df.groupby('next_roll_period')['roll_cumulative_return_raw'].last() + 1).cumprod()
        cum_rolls = cum_rolls.drop(cum_rolls.index[len(cum_rolls)-1]).rename('previous_roll_return')
        df = df.set_index('roll_period').join(cum_rolls, how = 'left').set_index('date')
        df['previous_roll_return'] = df['previous_roll_return'].fillna(1)
        df['daily_returns_cumulative'] = (df['roll_cumulative_return_raw'] + 1) * df['previous_roll_return']
        #df[(df['date'] > '2005-2-25') & (df['date'] < '2011-9-16')]['daily_returns_cumulative'].plot()
        df['roll_period'] = df['roll_date'].shift(1)
        self.results = df
        print('backtest complete')
        return None

