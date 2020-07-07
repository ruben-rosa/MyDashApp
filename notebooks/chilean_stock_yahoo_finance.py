#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#%%timeit
# Using Yahoo Finance
import pandas as pd
import datetime as dt
import yfinance as yf

tickers = ['LTM.SN', 'AESGENER.SN', 'AGUAS-A.SN', 'ANDINA-B.SN', 'BCI.SN', 'CAP.SN', 'CCU.SN',
           'CENCOSUD.SN', 'ENTEL.SN', 'FALABELLA.SN', 'CHILE.SN', 'COPEC.SN', 'RIPLEY.SN'
          ]

start = dt.datetime(2018,1,1)
end = dt.datetime.now()
df = pd.DataFrame()
for accion in tickers:
    df_ticker = yf.Ticker(accion)
    # get company name
    try:
        longname = df_ticker.info['longName']
        industry = df_ticker.info['industry']
        payoutRatio = df_ticker.info['payoutRatio']
    except:
        longname = accion
        industry = 'N/A'
        payoutRatio = 0 
    # get historical market data
    hist = df_ticker.history(start=start, end=end, interval='1d')
    hist['Ticker'] = accion
    hist['Name'] = longname
    hist['Industry'] = industry
    hist['PayoutRatio'] = payoutRatio
    df = df.append(hist, ignore_index=False)
file_name = '../DATA/chilean_stocks.csv'
df.to_csv(file_name)


# In[1]:


#%%timeit
# Using Pandas Datareader
import pandas as pd
import datetime as dt
from pandas_datareader import data as pdr

tickers = ['LTM.SN', 'AESGENER.SN', 'AGUAS-A.SN', 'ANDINA-B.SN', 'BCI.SN', 'CAP.SN', 'CCU.SN',
           'CENCOSUD.SN', 'ENTEL.SN', 'FALABELLA.SN', 'CHILE.SN', 'COPEC.SN', 'RIPLEY.SN'
          ]

start = dt.datetime(2018,1,1)
end = dt.datetime.now()
df = pd.DataFrame()
for accion in tickers:
    # get historical market data
    hist = pdr.get_data_yahoo(accion, start=start, end=end)
    hist['ticker'] = accion
    df = df.append(hist, ignore_index=False)
file_name = '../DATA/chilean_stocks_pdr.csv'
df.to_csv(file_name)


# In[ ]:




