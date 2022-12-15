import requests
from pprint import pprint
from datetime import datetime
from math import ceil
import matplotlib.pyplot as plt
import asyncio
import pandas as pd
import decimal
import warnings
warnings.filterwarnings('ignore')

from copy import deepcopy as dc

from ema import calculate_ema

import plotly.graph_objs as go
import plotly.express as px
# from mplfinance import candlestick2_ohlc
import time

import os

plt.rcParams["figure.figsize"] = (20, 16)

def plot_candles_and_ichimoku(asset, ichi_df, show):
    fig, ax = plt.subplots()

    ax.plot(ichi_df['Date/Time'], ichi_df['Tenkan Sen'], c='g', alpha=0.8)
    ax.plot(ichi_df['Date/Time'], ichi_df['Kijun Sen'], c='r', alpha=0.8)
    ax.plot(ichi_df['Date/Time'], ichi_df['Senkou Span A'], c='g', alpha=0.2)
    ax.plot(ichi_df['Date/Time'], ichi_df['Senkou Span B'], c='r', alpha=0.2)
    # ax.plot(ichi_df['Date/Time'], ichi_df['Chikou Span'], c='b')
    
    ax.fill_between(ichi_df['Date/Time'], ichi_df['Senkou Span A'], ichi_df['Senkou Span B'], color='g' , alpha=0.2, where=ichi_df['Senkou Span A'] > ichi_df['Senkou Span B'])
    ax.fill_between(ichi_df['Date/Time'], ichi_df['Senkou Span A'], ichi_df['Senkou Span B'], color='r' , alpha=0.2, where=ichi_df['Senkou Span A'] <= ichi_df['Senkou Span B'])

    buy_df = ichi_df.loc[ichi_df['Buy'] == True]
    ax.scatter(buy_df['Date/Time'], buy_df['Close'], color='g', marker='^', s=250)

    sell_df = ichi_df.loc[ichi_df['Sell'] == True]
    ax.scatter(sell_df['Date/Time'], sell_df['Close'], color='r', marker='v', s=250)

    ax.plot(ichi_df['Date/Time'], ichi_df['Close'], c='k')

    for lag in (7, 9, 11, 13):
        ema = calculate_ema(ichi_df['Close'], lag)
        ax.plot(ichi_df['Date/Time'][lag-1:], ema, alpha=0.5)

    
    # os.system('clear')
    if show:
        plt.show()


def ichimoku(df, period):
    tenkan_window = 9
    kijun_window = 26
    senkou_span_b_window = 52
    cloud_displacement = 26
    chikou_shift = -cloud_displacement
    ohcl_df = dc(df)

    # Dates are floats in mdates like 736740.0
    # the period is the difference of last two dates
    last_date = ohcl_df["Timestamp"].iloc[-1]
    # period = last_date - ohcl_df["Timestamp"].iloc[-2]
    

    # Add rows for N periods shift (cloud_displacement)
    ext_beginning = last_date+period
    ext_end = last_date + ((period*cloud_displacement)+period)
    dates_ext = list(range(ext_beginning, ext_end, period))
    dates_ext_df = pd.DataFrame({"Date/Time": [datetime.fromtimestamp(time) for time in dates_ext], "Timestamp": dates_ext})
    # dates_ext_df.index = dates_ext # also update the df index
    ohcl_df = ohcl_df.append(dates_ext_df, ignore_index=True)

    # Tenkan 
    tenkan_sen_high = ohcl_df['High'].rolling( window=tenkan_window ).max()
    tenkan_sen_low = ohcl_df['Low'].rolling( window=tenkan_window ).min()
    ohcl_df['Tenkan Sen'] = (tenkan_sen_high + tenkan_sen_low) /2
    # Kijun 
    kijun_sen_high = ohcl_df['High'].rolling( window=kijun_window ).max()
    kijun_sen_low = ohcl_df['Low'].rolling( window=kijun_window ).min()
    ohcl_df['Kijun Sen'] = (kijun_sen_high + kijun_sen_low) / 2
    # Senkou Span A 
    ohcl_df['Senkou Span A'] = ((ohcl_df['Tenkan Sen'] + ohcl_df['Kijun Sen']) / 2).shift(cloud_displacement)
    # Senkou Span B 
    senkou_span_b_high = ohcl_df['High'].rolling( window=senkou_span_b_window ).max()
    senkou_span_b_low = ohcl_df['Low'].rolling( window=senkou_span_b_window ).min()
    ohcl_df['Senkou Span B'] = ((senkou_span_b_high + senkou_span_b_low) / 2).shift(cloud_displacement)
    # Chikou
    ohcl_df['Chikou Span'] = ohcl_df['Close'].shift(chikou_shift)
    display(ohcl_df)

    return ohcl_df

def strategy(ichi_df):
    ichi_df['Above'] = (ichi_df['Close'] > ichi_df['Senkou Span A']) & (ichi_df['Close'] > ichi_df['Senkou Span B'])
    ichi_df['Below'] = (ichi_df['Close'] < ichi_df['Senkou Span A']) & (ichi_df['Close'] < ichi_df['Senkou Span B'])
    ichi_df['Buy'] = ichi_df['Above'].diff() & ~ichi_df['Above']
    ichi_df['Sell'] = ichi_df['Below'].diff() & ~ichi_df['Below']
