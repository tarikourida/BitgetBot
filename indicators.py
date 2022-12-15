import requests
from pprint import pprint
from datetime import datetime
from math import ceil
import matplotlib.pyplot as plt
import asyncio
import pandas as pd
import numpy as np
import decimal
import warnings
warnings.filterwarnings('ignore')

from copy import deepcopy as dc

import plotly.graph_objs as go
import plotly.express as px
# from mplfinance import candlestick2_ohlc
import time

import os

import plotly.graph_objs as go
import plotly.express as px
# from mplfinance import candlestick2_ohlc
import pylab as pl
from IPython import display as display_graph



plt.rcParams["figure.figsize"] = (20, 16)

def calculate_ema(prices, num, smoothing=2):
    ema = [sum(prices[:num]) / num]
    for price in prices[num:]:
        ema.append((price * (smoothing / (1 + num))) + ema[-1] * (1 - (smoothing / (1 + num))))
    return ema

def plot_close_indicators(asset, df_ind, refresh_plot, ema_lags, ichi=True):
    try:
        fig, ax = plt.subplots()

        if ichi:
            ax.plot(df_ind['Date/Time'], df_ind['Tenkan Sen'], c='g', alpha=0.8)
            ax.plot(df_ind['Date/Time'], df_ind['Kijun Sen'], c='r', alpha=0.8)
            ax.plot(df_ind['Date/Time'], df_ind['Senkou Span A'], c='g', alpha=0.2)
            ax.plot(df_ind['Date/Time'], df_ind['Senkou Span B'], c='r', alpha=0.2)
            
            ax.fill_between(df_ind['Date/Time'], df_ind['Senkou Span A'], df_ind['Senkou Span B'], color='g' , alpha=0.2, where=df_ind['Senkou Span A'] > df_ind['Senkou Span B'])
            ax.fill_between(df_ind['Date/Time'], df_ind['Senkou Span A'], df_ind['Senkou Span B'], color='r' , alpha=0.2, where=df_ind['Senkou Span A'] <= df_ind['Senkou Span B'])

        buy_df = df_ind.loc[df_ind['Buy'] == True]
        ax.scatter(buy_df['Date/Time'], buy_df['Close'], color='g', marker='^', s=250)

        sell_df = df_ind.loc[df_ind['Sell'] == True]
        ax.scatter(sell_df['Date/Time'], sell_df['Close'], color='r', marker='v', s=250)

        ax.plot(df_ind['Date/Time'], df_ind['Close'], c='k')

        for lag in sorted(ema_lags):
            ax.plot(df_ind['Date/Time'], df_ind['EMA {}'.format(lag)], alpha=0.5)

        if refresh_plot:
            display_graph.clear_output(wait=True)
            display_graph.display(plt.gcf())
        else:
            plt.show()
    except KeyboardInterrupt:
        pass    

def ichimoku_and_ema(df, period, ema_lags, tenkan_window=9, kijun_window=26, senkou_span_b_window=52, ichi=True):
    ema_lags = sorted(ema_lags)

    cloud_displacement = kijun_window
    chikou_shift = -cloud_displacement
    df_ind = dc(df)

    for lag in sorted(ema_lags):
        if len(df_ind) >= lag:
            df_ind['EMA {}'.format(lag)] = [np.nan]*(lag-1) + calculate_ema(df_ind['Close'], lag)

    if ichi & (len(df_ind) >= senkou_span_b_window):
        last_date = df_ind["Timestamp"].iloc[-1]
        ext_beginning = last_date+period
        ext_end = last_date + ((period*cloud_displacement)+period)
        dates_ext = list(range(ext_beginning, ext_end, period))
        dates_ext_df = pd.DataFrame({"Date/Time": [datetime.fromtimestamp(time) for time in dates_ext], "Timestamp": dates_ext})
        df_ind = df_ind.append(dates_ext_df, ignore_index=True)
        
        # Tenkan 
        tenkan_sen_high = df_ind['High'].rolling( window=tenkan_window ).max()
        tenkan_sen_low = df_ind['Low'].rolling( window=tenkan_window ).min()
        df_ind['Tenkan Sen'] = (tenkan_sen_high + tenkan_sen_low) /2        

        # Kijun 
        kijun_sen_high = df_ind['High'].rolling( window=kijun_window ).max()
        kijun_sen_low = df_ind['Low'].rolling( window=kijun_window ).min()
        df_ind['Kijun Sen'] = (kijun_sen_high + kijun_sen_low) / 2

        # Senkou Span A 
        df_ind['Senkou Span A'] = ((df_ind['Tenkan Sen'] + df_ind['Kijun Sen']) / 2).shift(cloud_displacement)

        # Senkou Span B 
        senkou_span_b_high = df_ind['High'].rolling( window=senkou_span_b_window ).max()
        senkou_span_b_low = df_ind['Low'].rolling( window=senkou_span_b_window ).min()
        df_ind['Senkou Span B'] = ((senkou_span_b_high + senkou_span_b_low) / 2).shift(cloud_displacement)

        # Chikou
        df_ind['Chikou Span'] = df_ind['Close'].shift(chikou_shift)        

    return df_ind
