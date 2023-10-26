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

## indicators
mediamovel_20 = backtest.moving_average(stock_data.price_matrix[:,4], 20)
mediamovel_100 = backtest.moving_average(stock_data.price_matrix[:,4], 100)
mediamovel_20 = mediamovel_20[80:]
precos_vale = stock_data.price_matrix[99:,4]


print('vamos verificar: ')
print(type(mediamovel_20))
print(mediamovel_20.shape)
print(mediamovel_100.shape)
print(precos_vale.shape)
print('vamos verificar: ')

result_column_stack = np.column_stack((precos_vale, mediamovel_20, mediamovel_100))
print('tamanho juncao: ', len(result_column_stack))
print(type(result_column_stack))
print(result_column_stack.shape)

# plt.plot(result_column_stack[1500:2500,:], color='blue')
# plt.title('Scatter plot entre tensor1 e tensor2')
# plt.xlabel('tensor1')
# plt.ylabel('tensor2')
# plt.show()

colors = ['blue', 'red', 'green']  

plt.figure(figsize=(10,6))

for i, color in enumerate(colors):
    plt.plot(result_column_stack[1500:2500,i], color=color, label=f'Coluna {i+1}')

plt.title('Gráfico das colunas')
plt.xlabel('Índice')
plt.ylabel('Valor')
plt.legend() 
plt.show()