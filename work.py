import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import edhec_risk_kit as erk
import edhec_risk_kit_206 as erk1
import yfinance as yf
import statsmodels.api as sm
import seaborn as sns
from datetime import date
from pandas_datareader import data
import matplotlib.pyplot as plt
from matplotlib import colors
import investpy


def world_indices(end_date, weekly='No'):
    """
    Returns a dataframe with local currency and dollar returns for world equity indices over a day and YTD timeframe, sorted from highest one day dollar return to lowest (data cannot be sliced, plotted, etc; for that use world_indices_data())
    """

    
    indices_lcl = yf.download("^NSEI ^BSESN ^GSPC ^NDX ^BVSP ^MXX ^N225 000001.SS ^TWII ^AXJO ^KS11 ^HSI ^JKSE ^GDAXI ^IBEX ^TA125.TA ^FCHI ^STOXX50E IMOEX.ME ^SSMI", start='2020-01-01',end=end_date)['Close'].ffill()
    ccy = yf.download("INRUSD=X BRLUSD=X MXNUSD=X JPYUSD=X CNYUSD=X TWDUSD=X AUDUSD=X KRWUSD=X HKDUSD=X IDRUSD=X EURUSD=X ILSUSD=X RUBUSD=X CHFUSD=X", start='2020-01-01')['Close'].ffill()
    
    if weekly=='Yes':
        one_day_lcl = pd.concat([indices_lcl.iloc[-1,:],
                         indices_lcl.iloc[-1,:]-indices_lcl.iloc[-6,:],
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[-6,:]-1),
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[4,:]-1)], axis=1)
        one_day_lcl.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']
    
    else:
        one_day_lcl = pd.concat([indices_lcl.iloc[-1,:],
                         indices_lcl.iloc[-1,:]-indices_lcl.iloc[-2,:],
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[-2,:]-1),
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[4,:]-1)], axis=1)
        one_day_lcl.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']
    
    
    merged = indices_lcl.merge(ccy, on='Date')
    
    indices_usd = pd.concat([merged['000001.SS']*merged['CNYUSD=X'],
                            merged['IMOEX.ME']*merged['RUBUSD=X'],
                            merged['^AXJO']*merged['AUDUSD=X'],
                            merged['^BSESN']*merged['INRUSD=X'],
                            merged['^BVSP']*merged['BRLUSD=X'],
                            merged['^FCHI']*merged['EURUSD=X'],
                            merged['^GDAXI']*merged['EURUSD=X'],
                            merged['^GSPC'],
                            merged['^HSI']*merged['HKDUSD=X'],
                            merged['^IBEX']*merged['EURUSD=X'],
                            merged['^JKSE']*merged['IDRUSD=X'],
                            merged['^KS11']*merged['KRWUSD=X'],
                            merged['^MXX']*merged['MXNUSD=X'],
                            merged['^N225']*merged['JPYUSD=X'],
                            merged['^NDX'],
                            merged['^NSEI']*merged['INRUSD=X'],
                            merged['^SSMI']*merged['CHFUSD=X'],
                            merged['^STOXX50E']*merged['EURUSD=X'],
                            merged['^TA125.TA']*merged['ILSUSD=X'],
                            merged['^TWII']*merged['TWDUSD=X']],axis=1)
    
    indices_lcl.columns = ['China Shanghai Composite', 'MOEX Russia Index', 'Australia ASX200', 'S&P BSE SENSEX', 'Brazil Stock Market (BOVESPA)', 'France CAC 40 Stock Market Index', 'Germany DAX 30 Stock Market Index', 'S&P 500', 'Hong Kong Hang Seng Index', 'Spain Stock Market (IBEX 35)', 'Indonesia Stock Market (JCI)', 'South Korea Stock Market (KOSPI)', 'IPC Mexico Stock Market', 'Japan NIKKEI 225 Stock Market', 'NASDAQ100', 'Nifty50','Switzerland SMI','EURO STOXX 50 Stock Market Index', 'Israel Stock Market (TA-125)', 'Taiwan Stock Market (TWSE)']

    indices_usd.columns = indices_lcl.columns
    one_day_lcl.index = indices_lcl.columns
    
    if weekly=='Yes':
        one_day_usd = pd.concat([indices_usd.iloc[-1,:]-indices_usd.iloc[-6,:],
                        (indices_usd.iloc[-1,:]/indices_usd.iloc[-6,:]-1),
                        (indices_usd.iloc[-1,:]/indices_usd.iloc[4,:]-1)], axis=1)
        one_day_usd.columns = ['$ Chg', '$ Chg (%)', '$ Chg YTD (%)']
    
    else:
        one_day_usd = pd.concat([indices_usd.iloc[-1,:]-indices_usd.iloc[-2,:],
                            (indices_usd.iloc[-1,:]/indices_usd.iloc[-2,:]-1),
                            (indices_usd.iloc[-1,:]/indices_usd.iloc[4,:]-1)], axis=1)
        one_day_usd.columns = ['$ Chg', '$ Chg (%)', '$ Chg YTD (%)']

    final = pd.concat([one_day_lcl, one_day_usd], axis=1).sort_values('$ Chg (%)', ascending=False)
   
    if weekly=='Yes':
        final = final[['Price (EOD)', '$ Chg (%)', '$ Chg YTD (%)']]
        final = final.style.format({'$ Chg (%)': "{:.2%}", '$ Chg YTD (%)': "{:.2%}",'Price (EOD)': "{:.2f}"})\
                     .background_gradient(cmap='RdYlGn', subset=list(final.drop(['Price (EOD)'], axis=1).columns))
    else:    
        final = final.style.format({'Chg (%)': "{:.2%}", 'Chg YTD (%)': "{:.2%}", '$ Chg (%)': "{:.2%}", '$ Chg YTD (%)': "{:.2%}",'$ Chg': "{:+.2f}", 'Chg': "{:+.2f}", 'Price (EOD)': "{:.2f}"})\
                     .background_gradient(cmap='RdYlGn', subset=list(final.drop(['Price (EOD)', '$ Chg', 'Chg'], axis=1).columns))
    
    return final

def world_indices_data(end_date, weekly='No'):
    """
    Returns a dataframe with local currency and dollar returns for world equity indices over a day and YTD timeframe, sorted from highest one day dollar return to lowest
    """

    
    indices_lcl = yf.download('^NSEI ^BSESN ^GSPC ^NDX ^BVSP ^MXX ^N225 000001.SS ^TWII ^AXJO ^KS11 ^HSI ^JKSE ^GDAXI ^IBEX ^TA125.TA ^FCHI ^STOXX50E IMOEX.ME ^SSMI', start='2020-01-01', end=end_date)['Close'].ffill()
    ccy = yf.download('INRUSD=X BRLUSD=X MXNUSD=X JPYUSD=X CNYUSD=X TWDUSD=X AUDUSD=X KRWUSD=X HKDUSD=X IDRUSD=X EURUSD=X ILSUSD=X RUBUSD=X CHFUSD=X'
                   , start='2020-01-01')['Close'].ffill()
    
    
    if weekly=='Yes':
        one_day_lcl = pd.concat([indices_lcl.iloc[-1,:],
                         indices_lcl.iloc[-1,:]-indices_lcl.iloc[-6,:],
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[-6,:]-1)*100,
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[4,:]-1)*100], axis=1)
        one_day_lcl.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']
    
    else:
        one_day_lcl = pd.concat([indices_lcl.iloc[-1,:],
                         indices_lcl.iloc[-1,:]-indices_lcl.iloc[-2,:],
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[-2,:]-1)*100,
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[4,:]-1)*100], axis=1)
        one_day_lcl.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']

    merged = indices_lcl.merge(ccy, on='Date')
    
    indices_usd = pd.concat([merged['000001.SS']*merged['CNYUSD=X'],
                            merged['IMOEX.ME']*merged['RUBUSD=X'],
                            merged['^AXJO']*merged['AUDUSD=X'],
                            merged['^BSESN']*merged['INRUSD=X'],
                            merged['^BVSP']*merged['BRLUSD=X'],
                            merged['^FCHI']*merged['EURUSD=X'],
                            merged['^GDAXI']*merged['EURUSD=X'],
                            merged['^GSPC'],
                            merged['^HSI']*merged['HKDUSD=X'],
                            merged['^IBEX']*merged['EURUSD=X'],
                            merged['^JKSE']*merged['IDRUSD=X'],
                            merged['^KS11']*merged['KRWUSD=X'],
                            merged['^MXX']*merged['MXNUSD=X'],
                            merged['^N225']*merged['JPYUSD=X'],
                            merged['^NDX'],
                            merged['^NSEI']*merged['INRUSD=X'],
                            merged['^SSMI']*merged['CHFUSD=X'],
                            merged['^STOXX50E']*merged['EURUSD=X'],
                            merged['^TA125.TA']*merged['ILSUSD=X'],
                            merged['^TWII']*merged['TWDUSD=X']],axis=1)
    
    indices_lcl.columns = ['China Shanghai Composite', 'MOEX Russia Index', 'Australia ASX200', 'S&P BSE SENSEX', 'Brazil Stock Market (BOVESPA)', 'France CAC 40 Stock Market Index', 'Germany DAX 30 Stock Market Index', 'S&P 500', 'Hong Kong Hang Seng Index', 'Spain Stock Market (IBEX 35)', 'Indonesia Stock Market (JCI)', 'South Korea Stock Market (KOSPI)', 'IPC Mexico Stock Market', 'Japan NIKKEI 225 Stock Market', 'NASDAQ100', 'Nifty50','Switzerland SMI','EURO STOXX 50 Stock Market Index', 'Israel Stock Market (TA-125)', 'Taiwan Stock Market (TWSE)']

    indices_usd.columns = indices_lcl.columns
    one_day_lcl.index = indices_lcl.columns
    
    if weekly=='Yes':
        one_day_usd = pd.concat([indices_usd.iloc[-1,:]-indices_usd.iloc[-6,:],
                            (indices_usd.iloc[-1,:]/indices_usd.iloc[-6,:]-1)*100,
                            (indices_usd.iloc[-1,:]/indices_usd.iloc[4,:]-1)*100], axis=1)
        one_day_usd.columns = ['$ Chg', '$ Chg (%)', '$ Chg YTD (%)']
    
    else:
        one_day_usd = pd.concat([indices_usd.iloc[-1,:]-indices_usd.iloc[-2,:],
                            (indices_usd.iloc[-1,:]/indices_usd.iloc[-2,:]-1)*100,
                            (indices_usd.iloc[-1,:]/indices_usd.iloc[4,:]-1)*100], axis=1)
        one_day_usd.columns = ['$ Chg', '$ Chg (%)', '$ Chg YTD (%)']
    
    final = pd.concat([one_day_lcl, one_day_usd], axis=1).sort_values('$ Chg (%)', ascending=False)
    
    return final


#### WEEKLY ####

def world_indices_data_wtd(start_date, end_date):
    """
    Returns a dataframe with local currency and dollar returns for world equity indices over a day and YTD timeframe, sorted from highest one day dollar return to lowest
    """

    
    indices_lcl = yf.download('^NSEI ^BSESN ^GSPC ^NDX ^BVSP ^MXX ^N225 000001.SS ^TWII ^AXJO ^KS11 ^HSI ^JKSE ^GDAXI ^IBEX ^TA125.TA ^FCHI ^STOXX50E IMOEX.ME ^SSMI', start=start_date, end=end_date)['Close']
    ccy = yf.download('INRUSD=X BRLUSD=X MXNUSD=X JPYUSD=X CNYUSD=X TWDUSD=X AUDUSD=X KRWUSD=X HKDUSD=X IDRUSD=X EURUSD=X ILSUSD=X RUBUSD=X CHFUSD=X'
                   , start= start_date, end=end_date)['Close']
    
    one_day_lcl = pd.concat([indices_lcl.iloc[-1,:],
                         indices_lcl.iloc[-1,:]-indices_lcl.iloc[-2,:],
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[-2,:]-1)*100,
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[4,:]-1)*100], axis=1)
    one_day_lcl.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg WTD (%)']
    
    
    merged = indices_lcl.merge(ccy, on='Date')
    
    indices_usd = pd.concat([merged['000001.SS']*merged['CNYUSD=X'],
                            merged['IMOEX.ME']*merged['RUBUSD=X'],
                            merged['^AXJO']*merged['AUDUSD=X'],
                            merged['^BSESN']*merged['INRUSD=X'],
                            merged['^BVSP']*merged['BRLUSD=X'],
                            merged['^FCHI']*merged['EURUSD=X'],
                            merged['^GDAXI']*merged['EURUSD=X'],
                            merged['^GSPC'],
                            merged['^HSI']*merged['HKDUSD=X'],
                            merged['^IBEX']*merged['EURUSD=X'],
                            merged['^JKSE']*merged['IDRUSD=X'],
                            merged['^KS11']*merged['KRWUSD=X'],
                            merged['^MXX']*merged['MXNUSD=X'],
                            merged['^N225']*merged['JPYUSD=X'],
                            merged['^NDX'],
                            merged['^NSEI']*merged['INRUSD=X'],
                            merged['^SSMI']*merged['CHFUSD=X'],
                            merged['^STOXX50E']*merged['EURUSD=X'],
                            merged['^TA125.TA']*merged['ILSUSD=X'],
                            merged['^TWII']*merged['TWDUSD=X']],axis=1)
    
    indices_lcl.columns = ['China Shanghai Composite', 'MOEX Russia Index', 'Australia ASX200', 'S&P BSE SENSEX', 'Brazil Stock Market (BOVESPA)', 'France CAC 40 Stock Market Index', 'Germany DAX 30 Stock Market Index', 'S&P 500', 'Hong Kong Hang Seng Index', 'Spain Stock Market (IBEX 35)', 'Indonesia Stock Market (JCI)', 'South Korea Stock Market (KOSPI)', 'IPC Mexico Stock Market', 'Japan NIKKEI 225 Stock Market', 'NASDAQ100', 'Nifty50','Switzerland SMI','EURO STOXX 50 Stock Market Index', 'Israel Stock Market (TA-125)', 'Taiwan Stock Market (TWSE)']

    indices_usd.columns = indices_lcl.columns
    one_day_lcl.index = indices_lcl.columns
    one_day_usd = pd.concat([indices_usd.iloc[-1,:]-indices_usd.iloc[-2,:],
                        (indices_usd.iloc[-1,:]/indices_usd.iloc[-2,:]-1)*100,
                        (indices_usd.iloc[-1,:]/indices_usd.iloc[4,:]-1)*100], axis=1)
    one_day_usd.columns = ['$ Chg', '$ Chg (%)', '$ Chg WTD (%)']
    
    final = pd.concat([one_day_lcl, one_day_usd], axis=1).sort_values('$ Chg WTD (%)', ascending=False)
    
    return final














###### WORLD INDICES EXPERIMENT //////

def world_indices_new(end_date, start_date='2020-01-06'):
    """
    Returns a dataframe with local currency and dollar returns for world equity indices over a day and YTD timeframe, sorted from highest one day dollar return to lowest (data cannot be sliced, plotted, etc; for that use world_indices_data())
    """

    
    indices_lcl = data.DataReader(["^NSEI", "^BSESN", "^GSPC", "^NDX", "^BVSP","^MXX","^N225","000001.SS","^TWII","^AXJO","^KS11","^HSI","^JKSE","^GDAXI","^IBEX","^TA125.TA","^FCHI","^STOXX50E","IMOEX.ME","^FTSE","^SSMI"], 'yahoo', start_date, end_date)['Close']
    ccy = data.DataReader(["INRUSD=X","BRLUSD=X","MXNUSD=X","JPYUSD=X","CNYUSD=X","TWDUSD=X","AUDUSD=X","KRWUSD=X","HKDUSD=X","IDRUSD=X","EURUSD=X","ILSUSD=X","RUBUSD=X","GBPUSD=X","CHFUSD=X"],'yahoo', start_date, end_date)['Close']
    
    one_day_lcl = pd.concat([indices_lcl.iloc[-1,:],
                         indices_lcl.iloc[-1,:]-indices_lcl.iloc[-3,:],
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[-3,:]-1),
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[0,:]-1)], axis=1)
    one_day_lcl.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']
    
    
    merged = indices_lcl.merge(ccy, on='Date')
    
    indices_usd = pd.concat([merged['000001.SS']*merged['CNYUSD=X'],
                            merged['IMOEX.ME']*merged['RUBUSD=X'],
                            merged['^AXJO']*merged['AUDUSD=X'],
                            merged['^BSESN']*merged['INRUSD=X'],
                            merged['^BVSP']*merged['BRLUSD=X'],
                            merged['^FCHI']*merged['EURUSD=X'],
                            merged['^FTSE']*merged['GBPUSD=X'],
                            merged['^GDAXI']*merged['EURUSD=X'],
                            merged['^GSPC'],
                            merged['^HSI']*merged['HKDUSD=X'],
                            merged['^IBEX']*merged['EURUSD=X'],
                            merged['^JKSE']*merged['IDRUSD=X'],
                            merged['^KS11']*merged['KRWUSD=X'],
                            merged['^MXX']*merged['MXNUSD=X'],
                            merged['^N225']*merged['JPYUSD=X'],
                            merged['^NDX'],
                            merged['^NSEI']*merged['INRUSD=X'],
                            merged['^SSMI']*merged['CHFUSD=X'],
                            merged['^STOXX50E']*merged['EURUSD=X'],
                            merged['^TA125.TA']*merged['ILSUSD=X'],
                            merged['^TWII']*merged['TWDUSD=X']],axis=1)
    
    indices_lcl.columns = ['China Shanghai Composite', 'MOEX Russia Index', 'Australia ASX200', 'S&P BSE SENSEX', 'Brazil Stock Market (BOVESPA)', 'France CAC 40 Stock Market Index', 'UK FTSE 100','Germany DAX 30 Stock Market Index', 'S&P 500', 'Hong Kong Hang Seng Index', 'Spain Stock Market (IBEX 35)', 'Indonesia Stock Market (JCI)', 'South Korea Stock Market (KOSPI)', 'IPC Mexico Stock Market', 'Japan NIKKEI 225 Stock Market', 'NASDAQ100', 'Nifty50', 'Switzerland SMI','EURO STOXX 50 Stock Market Index', 'Israel Stock Market (TA-125)', 'Taiwan Stock Market (TWSE)']

    indices_usd.columns = indices_lcl.columns
    one_day_lcl.index = indices_lcl.columns
    one_day_usd = pd.concat([indices_usd.iloc[-1,:]-indices_usd.iloc[-2,:],
                        (indices_usd.iloc[-1,:]/indices_usd.iloc[-2,:]-1),
                        (indices_usd.iloc[-1,:]/indices_usd.iloc[0,:]-1)], axis=1)
    one_day_usd.columns = ['$ Chg', '$ Chg (%)', '$ Chg YTD (%)']
    
    final = pd.concat([one_day_lcl, one_day_usd], axis=1).sort_values('$ Chg (%)', ascending=False)
   
    final = final.style.format({'Chg (%)': "{:.2%}", 'Chg YTD (%)': "{:.2%}", '$ Chg (%)': "{:.2%}", '$ Chg YTD (%)': "{:.2%}",'$ Chg': "{:+.2f}", 'Chg': "{:+.2f}", 'Price (EOD)': "{:.2f}"})
    
    return final

def world_indices_new_data(end_date, start_date='2020-01-06'):
    """
    Returns a dataframe with local currency and dollar returns for world equity indices over a day and YTD timeframe, sorted from highest one day dollar return to lowest (data cannot be sliced, plotted, etc; for that use world_indices_data())
    """

    
    indices_lcl = data.DataReader("^NSEI ^BSESN ^GSPC ^NDX ^BVSP ^MXX ^N225 000001.SS ^TWII ^AXJO ^KS11 ^HSI ^JKSE ^GDAXI ^IBEX ^TA125.TA ^FCHI ^STOXX50E IMOEX.ME ^FTSE ^SSMI", start_date, end_date)['Adj Close']
    ccy = data.DataReader("INRUSD=X BRLUSD=X MXNUSD=X JPYUSD=X CNYUSD=X TWDUSD=X AUDUSD=X KRWUSD=X HKDUSD=X IDRUSD=X EURUSD=X ILSUSD=X RUBUSD=X, GBPUSD=X, CHFUSD=X", start_date, end_date)['Adj Close']
    
    one_day_lcl = pd.concat([indices_lcl.iloc[-1,:],
                         indices_lcl.iloc[-1,:]-indices_lcl.iloc[-2,:],
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[-2,:]-1),
                        (indices_lcl.iloc[-1,:]/indices_lcl.iloc[0,:]-1)], axis=1)
    one_day_lcl.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']
    
    
    merged = indices_lcl.merge(ccy, on='Date')
    
    indices_usd = pd.concat([merged['000001.SS']*merged['CNYUSD=X'],
                            merged['IMOEX.ME']*merged['RUBUSD=X'],
                            merged['^AXJO']*merged['AUDUSD=X'],
                            merged['^BSESN']*merged['INRUSD=X'],
                            merged['^BVSP']*merged['BRLUSD=X'],
                            merged['^FCHI']*merged['EURUSD=X'],
                            merged['^FTSE']*merged['GBPUSD=X'],
                            merged['^GDAXI']*merged['EURUSD=X'],
                            merged['^GSPC'],
                            merged['^HSI']*merged['HKDUSD=X'],
                            merged['^IBEX']*merged['EURUSD=X'],
                            merged['^JKSE']*merged['IDRUSD=X'],
                            merged['^KS11']*merged['KRWUSD=X'],
                            merged['^MXX']*merged['MXNUSD=X'],
                            merged['^N225']*merged['JPYUSD=X'],
                            merged['^NDX'],
                            merged['^NSEI']*merged['INRUSD=X'],
                            merged['^SSMI']*merged['CHFUSD=X'],
                            merged['^STOXX50E']*merged['EURUSD=X'],
                            merged['^TA125.TA']*merged['ILSUSD=X'],
                            merged['^TWII']*merged['TWDUSD=X']],axis=1)
    
    indices_lcl.columns = ['China Shanghai Composite', 'MOEX Russia Index', 'Australia ASX200', 'S&P BSE SENSEX', 'Brazil Stock Market (BOVESPA)', 'France CAC 40 Stock Market Index', 'UK FTSE 100','Germany DAX 30 Stock Market Index', 'S&P 500', 'Hong Kong Hang Seng Index', 'Spain Stock Market (IBEX 35)', 'Indonesia Stock Market (JCI)', 'South Korea Stock Market (KOSPI)', 'IPC Mexico Stock Market', 'Japan NIKKEI 225 Stock Market', 'NASDAQ100', 'Nifty50', 'Switzerland SMI','EURO STOXX 50 Stock Market Index', 'Israel Stock Market (TA-125)', 'Taiwan Stock Market (TWSE)']

    indices_usd.columns = indices_lcl.columns
    one_day_lcl.index = indices_lcl.columns
    one_day_usd = pd.concat([indices_usd.iloc[-1,:]-indices_usd.iloc[-2,:],
                        (indices_usd.iloc[-1,:]/indices_usd.iloc[-2,:]-1),
                        (indices_usd.iloc[-1,:]/indices_usd.iloc[0,:]-1)], axis=1)
    one_day_usd.columns = ['$ Chg', '$ Chg (%)', '$ Chg YTD (%)']
    
    final = pd.concat([one_day_lcl, one_day_usd], axis=1).sort_values('$ Chg (%)', ascending=False)
   
    #final = final.style.format({'Chg (%)': "{:.2%}", 'Chg YTD (%)': "{:.2%}", '$ Chg (%)': "{:.2%}", '$ Chg YTD (%)': "{:.2%}",'$ Chg': "{:+.2f}", 'Chg': "{:+.2f}", 'Price (EOD)': "{:.2f}"})
    
    return final

def commodities():
    start_date = '2020-01-01'
    commodities = data.DataReader("PA=F PL=F GC=F HO=F NG=F CL=F SI=F HG=F", start_date, date.today())['Adj Close']
    commodities.columns = ['Crude Oil', 'Gold', 'Copper', 'Heating Oil', 'Natural Gas', 'Palladium', 'Platinum', 'Silver']
    commodities_d = pd.concat([commodities.iloc[-1,:],
                         commodities.iloc[-1,:]-commodities.iloc[-2,:],
                        (commodities.iloc[-1,:]/commodities.iloc[-2,:]-1),
                        (commodities.iloc[-1,:]/commodities.iloc[0,:]-1)], axis=1)
    commodities_d.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']
    return commodities_d.style.format({'Chg (%)': "{:.2%}", 'Chg YTD (%)': "{:.2%}", 'Chg': "{:+.2f}", 'Price (EOD)': "{:.2f}"})

def commodities_display():
    start_date = '2020-01-01'
    commodities = data.DataReader("PA=F PL=F GC=F HO=F NG=F CL=F SI=F HG=F", start_date, date.today())['Adj Close']
    commodities.columns = ['Crude Oil', 'Gold', 'Copper', 'Heating Oil', 'Natural Gas', 'Palladium', 'Platinum', 'Silver']
    commodities_d = pd.concat([commodities.iloc[-1,:],
                         commodities.iloc[-1,:]-commodities.iloc[-2,:],
                        (commodities.iloc[-1,:]/commodities.iloc[-2,:]-1)*100,
                        (commodities.iloc[-1,:]/commodities.iloc[0,:]-1)*100], axis=1)
    commodities_d.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']
    return commodities_d
           
    
def updated_world_indices(category='Major', timeframe='Daily'):
    """
    
    """
    tdy = str(date.today().day)+'/'+str(date.today().month)+'/'+str(date.today().year)
    idxs = pd.read_excel('World_Indices_List.xlsx', index_col=0, header=0, sheet_name=category)
    index_names = list(idxs['Indices'])
    country_names = list(idxs['Country'])
    
    def idx_data(index, country):
        df = investpy.get_index_historical_data(index=index, country=country, from_date='01/01/2020', to_date=tdy)['Close']
        df = pd.DataFrame(df)
        df.columns = [index]
        return df
    
    df = pd.DataFrame(index=pd.bdate_range(start='2020-01-01', end=date.today()))
    df.index.name='Date'
    
    #Stitch Local Currency Indices Data
    for i in range(len(idxs)):
        df = df.join(idx_data(index_names[i], country_names[i]), on='Date')
        
    df1 = df.ffill().dropna()
    df1.index.name = 'Date'
    
    
    if timeframe=='Daily':
        pos = -2
    elif timeframe =='Weekly':
        pos = -6
    #Local Currency Returns Table
    oned_lcl = pd.concat([df1.iloc[-1,:],
                         df1.iloc[-1,:]-df1.iloc[pos,:],
                        (df1.iloc[-1,:]/df1.iloc[pos,:]-1),
                        (df1.iloc[-1,:]/df1.iloc[0,:]-1)], axis=1)
    oned_lcl.columns = ['Price (EOD)','Chg', 'Chg (%)', 'Chg YTD (%)']
    
    #Add Country and Currency Names
    cntry = pd.DataFrame(idxs['Country'])
    cntry.index = idxs['Indices']

    currency = pd.DataFrame(idxs['Currency'])
    currency.index = idxs['Indices']
    
    oned_lcl = oned_lcl.sort_values('Chg (%)', ascending=False)
    oned_lcl.index.name = 'Indices'
    oned_lcl = oned_lcl.merge(cntry['Country'], on='Indices')
    oned_lcl = oned_lcl.merge(currency['Currency'], on='Indices')
    oned_lcl=oned_lcl[['Country', 'Price (EOD)', 'Chg', 'Chg (%)', 'Chg YTD (%)', 'Currency']]
    
    #Import Currency Data

    ccyidx = yf.download("CADUSD=X BRLUSD=X MXNUSD=X EURUSD=X GBPUSD=X EURUSD=X EURUSD=X EURUSD=X EURUSD=X EURUSD=X CHFUSD=X EURUSD=X EURUSD=X EURUSD=X SEKUSD=X DKKUSD=X RUBUSD=X PLNUSD=X HUFUSD=X TRYUSD=X SARUSD=X JPYUSD=X AUDUSD=X NZDUSD=X CNYUSD=X CNYUSD=X CNYUSD=X CNYUSD=X HKDUSD=X TWDUSD=X THBUSD=X KRWUSD=X IDRUSD=X INRUSD=X INRUSD=X PHPUSD=X PKRUSD=X VNDUSD=X BHDUSD=X BGNUSD=X CLPUSD=X COPUSD=X EURUSD=X CZKUSD=X EGPUSD=X EURUSD=X EURUSD=X EURUSD=X MYRUSD=X OMRUSD=X PENUSD=X QARUSD=X SGDUSD=X ZARUSD=X KRWUSD=X TNDUSD=X", start='2020-01-01', progress=False)['Close'].ffill()
    dfmix = df1.merge(ccyidx, on='Date')
    ccys = dfmix.iloc[:,len(idxs):]
    
    #Calculate Currency Returns
    oned_ccy = pd.concat([ccys.iloc[-1,:],
                             ccys.iloc[-1,:]-ccys.iloc[pos,:],
                            (ccys.iloc[-1,:]/ccys.iloc[pos,:]-1),
                            (ccys.iloc[-1,:]/ccys.iloc[0,:]-1)], axis=1)
    oned_ccy.columns = ['Price (EOD)','Chg', 'CChg (%)', 'CChg YTD (%)']
    
    abc = oned_ccy.copy()
    abc = abc.append({'Price (EOD)':0, 'Chg':0, 'CChg (%)':0, 'CChg YTD (%)':0}, ignore_index=True)
    abc.index = list(oned_ccy.index) + ['USD']
    abc.index.name='Currency'
    
    #Convert Local Currency to USD Returns
    oned_lcl_copy = oned_lcl.copy()
    oned_lcl_copy['Indices'] = oned_lcl_copy.index
    testa = oned_lcl_copy.merge(abc[['CChg (%)', 'CChg YTD (%)']], on='Currency')
    testa.index = testa['Indices']

    testa['$ Chg (%)'] = (1+testa['Chg (%)'])*(1+testa['CChg (%)'])-1
    testa['$ Chg YTD (%)'] = (1+testa['Chg YTD (%)'])*(1+testa['CChg YTD (%)'])-1
    testa = testa[['Country', 'Price (EOD)', 'Chg', 'Chg (%)', 'Chg YTD (%)', '$ Chg (%)', '$ Chg YTD (%)']]
    
    testa = testa.sort_values('$ Chg (%)', ascending=False)
    
    formatted = testa.style.format({'Price (EOD)': "{:.2f}",'Chg': "{:.2f}", 'Chg (%)': "{:.2%}", 'Chg YTD (%)': "{:.2%}", '$ Chg (%)': "{:.2%}", '$ Chg YTD (%)': "{:.2%}"})\
                         .background_gradient(cmap='RdYlGn', subset=list(testa.drop(['Price (EOD)', 'Chg', 'Country'], axis=1).columns))
    return formatted, testa