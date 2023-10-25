
import os
import chardet

from dotenv import load_dotenv
from log_data import LogData, StockData

import chardet
import sys
import numpy as np
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
data_path = 'acoes_precos2.txt'
file_path = ambiente_local + data_path
stock_data = StockData(file_path)
weekdays = [StockData.date_to_weekday(date) for date in stock_data.dates]

# strategy develop // study
for j in range(len(stock_data.tickers)):
    if stock_data.tickers[j] not in ['B3SA3', 'SUZB3', 'BPAC11']:
        retornos_analisar = []
        retornos_previsto = []
        chave_loop = False
        for i in range (len(weekdays)):
            if chave_loop==False:
                if weekdays[i] == 'sexta':
                    if i >= 5:                
                        retornos_analisar.append(stock_data.price_matrix[i,j] / stock_data.price_matrix[i-5,j] - 1)
                        chave_loop = True
            if chave_loop:
                if weekdays[i] == 'segunda':
                    if weekdays[i-1] == 'sexta':
                        retornos_previsto.append(stock_data.price_matrix[i,j] / stock_data.price_matrix[i-i,j] - 1)
                        chave_loop = False
        retornos_analisar, retornos_previsto = equivalence_arrays(retornos_analisar, retornos_previsto)
        
        print(f'Ticker: {stock_data.tickers[j]}')
        mask = retornos_analisar > 0.01
        arrayA = retornos_analisar[mask]
        arrayB = retornos_previsto[mask]
        print(stat.correlation(arrayA, arrayB))

# backtest



# stock_data.display()
# # print(stock_data.price_matrix.shape)
# print(stock_data.tickers)
# # print(stock_data.dates[2000])
# print(stock_data.dates[0])
# print(stock_data.dates[-1])
# print(stock_data.price_matrix[0,:])



# print(type(stock_data.tickers))
# print(type(stock_data.dates))
# print(type(stock_data.price_matrix))

# print(stock_data.tickers[12])
# plt.plot(stock_data.price_matrix[:,12], color='blue')
# plt.title('Scatter plot entre tensor1 e tensor2')
# plt.xlabel('tensor1')
# plt.ylabel('tensor2')
# plt.show()
