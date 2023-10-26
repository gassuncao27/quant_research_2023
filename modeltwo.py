import os

from dotenv import load_dotenv
from log_data import LogData, StockData

import chardet
import sys
import numpy as np
import backtest
import statistics_functions as stat
import matplotlib.pyplot as plt


def equivalence_arrays(array1, array2):
    np1 = np.array(array1)
    np2 = np.array(array2)
    if len(np1) > len(np2):
        np1 = np1[:len(np2)]
    elif len(np1) < len(np2): 
        print('ERROR - verify array composition and size')
        sys.exit()
    return np1, np2


## upload data
load_dotenv()
ambiente_local = os.getenv('AMBIENTE_MAC')
data_path = 'acoes_precos5.txt'
file_path = ambiente_local + data_path
stock_data = StockData(file_path)
weekdays = [StockData.date_to_weekday(date) for date in stock_data.dates]


# backtest
capital_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
resultado_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
capital_alocacao[:, -1] = 1
equity =[100]


for i in range(10, len(weekdays)): 
    cash = 1

    for i2 in range(len(stock_data.tickers)):
        if stock_data.price_matrix[i-6, i2] != 0:
            # if weekdays[i] == 'segunda': 
            #     weekly_return = backtest.calculate_return(stock_data.price_matrix[i-6, i2], stock_data.price_matrix[i-1, i2])
            #     if weekly_return < -0.01: 
            #         capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "buy")   
            
            if weekdays[i] == 'sexta': 
                weekly_return = backtest.calculate_return(stock_data.price_matrix[i-5, i2], stock_data.price_matrix[i-1, i2])
                if weekly_return < -0.01: 
                    capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "buy")   
            
            if cash < 0:
                print('SYSTEM ERROR - cash out of reality')
                print(cash)
                sys.exit()
            else:
                capital_alocacao[i, -1] = cash

return_upfront = 3
for i in range(1, len(stock_data.dates)-return_upfront): 
    for i2, ticker in enumerate(stock_data.tickers):
        if stock_data.price_matrix[i, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i, i2], stock_data.price_matrix[i+return_upfront, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return

    equity.append((np.sum(resultado_alocacao[i, :])) * equity[i-1] + equity[i-1])

plt.plot(equity, color='blue')
plt.title('Scatter plot entre tensor1 e tensor2')
plt.xlabel('tensor1')
plt.ylabel('tensor2')
plt.show()
