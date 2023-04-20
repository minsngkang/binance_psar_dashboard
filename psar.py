from binance.client import Client
import config_BIN
import pandas as pd
import time


# asset1 = input('What Asset To Check? ')
# asset1 = (asset1+'USDT').upper()

key = config_BIN.api_key
sec = config_BIN.api_secret
binance_client = Client(key, sec)

# PSAR settings
iaf = 0.02
maxaf = 0.2

q1 = 15
q2 = 15


def get_psar_htf(barsdata, iaf=iaf, maxaf=maxaf):
    length = len(barsdata)
    high = list(barsdata['High'])
    low = list(barsdata['Low'])
    close = list(barsdata['Close'])
    psar = close[0:len(close)]
    psarbull = [None] * length
    psarbear = [None] * length
    bull = True
    af = iaf
    ep = low[0]
    hp = high[0]
    lp = low[0]
    
    for i in range(2,length):
        if bull:
            psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
        else:
            psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
        
        reverse = False
        
        if bull:
            if low[i] < psar[i]:
                bull = False
                reverse = True
                psar[i] = hp
                lp = low[i]
                af = iaf
        else:
            if high[i] > psar[i]:
                bull = True
                reverse = True
                psar[i] = lp
                hp = high[i]
                af = iaf
    
        if not reverse:
            if bull:
                if high[i] > hp:
                    hp = high[i]
                    af = min(af + iaf, maxaf)
                if low[i - 1] < psar[i]:
                    psar[i] = low[i - 1]
                if low[i - 2] < psar[i]:
                    psar[i] = low[i - 2]
            else:
                if low[i] < lp:
                    lp = low[i]
                    af = min(af + iaf, maxaf)
                if high[i - 1] > psar[i]:
                    psar[i] = high[i - 1]
                if high[i - 2] > psar[i]:
                    psar[i] = high[i - 2]
                    
        if bull:
            psarbull[i] = psar[i]
            df.loc[i, 'PSAR'] = 1
        else:
            psarbear[i] = psar[i]
            df.loc[i, 'PSAR'] = -1

    return

def psar_binance_htf(asset1,htf,limit):

    bars_htf = binance_client.futures_klines(symbol=asset1,interval=htf, limit=limit)
    global df
    df = pd.DataFrame(bars_htf, columns=['Time','Open','High','Low','Close','Vol','1','2','3','4','5','6'])
    df['Time'] = pd.to_datetime(df['Time'] / 1000, unit='s')
    df = df.iloc[: , :-6]
    for i in df.columns:
            if i != 'Time':
                df[i] = df[i].astype(float)
    get_psar_htf(df)
    # print(df)

    N = q1
    
    last_n_rows = df.tail(N)

    psar_current = float(df['PSAR'].iloc[-1])
    psar_closed = float(df['PSAR'].iloc[-2])
    psar_prev = float(df['PSAR'].iloc[-3])

    print('----------------------------')
    print('Higher Time Frame:',htf,asset1)
    print('----------------------------')
    print(last_n_rows)
    print('----------------------------')
    print(asset1,'    Current PSAR', htf, psar_current)
    print(asset1,'Last Closed PSAR', htf, psar_closed)
    print(asset1,'   Previous PSAR', htf, psar_prev)

    return psar_current

# psar_binance_htf()

# EXAMPLE
# psar_binance_htf("BCHUSDT",'1h',1440)
# print( psar_binance_htf("BCHUSDT",'1h',1440)  )

# psar_binance_ltf()
#time.sleep(60)
