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
# from ema import calculate_ema
import plotly.graph_objs as go
import plotly.express as px
# from mplfinance import candlestick2_ohlc
import time
import os



def strategy(df_ind, ema_lags, ichi=True):

    ema_lags = sorted(ema_lags)
    # print(df_ind)
    # emas = df_ind[["EMA {}".format(lag) for lag in ema_lags]]
    if ichi:
        df_ind['Above'] = (df_ind['Close'] > df_ind['Senkou Span A']) & (df_ind['Close'] > df_ind['Senkou Span B'])
        df_ind['Below'] = (df_ind['Close'] < df_ind['Senkou Span A']) & (df_ind['Close'] < df_ind['Senkou Span B'])

    df_ind['Buy'] = (df_ind['Close'] == df_ind['Close']) if not ichi else df_ind['Above'].diff() & ~df_ind['Above']
    df_ind['Sell'] = (df_ind['Close'] == df_ind['Close']) if not ichi else df_ind['Below'].diff() & ~df_ind['Below']

    for lower, higher in zip(ema_lags[:-1], ema_lags[1:]):
        df_ind['Buy'] &= (df_ind['EMA {}'.format(lower)] > df_ind['EMA {}'.format(higher)])
        df_ind['Sell'] &= (df_ind['EMA {}'.format(lower)] < df_ind['EMA {}'.format(higher)])

