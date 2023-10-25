
import os
import chardet

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
data_path = 'acoes_precos2.txt'

print(ambiente_local)
print(data_path )

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
                    # if weekdays[i-1] == 'sexta':
                    retornos_previsto.append(stock_data.price_matrix[i,j] / stock_data.price_matrix[i-1,j] - 1)
                    chave_loop = False
        retornos_analisar, retornos_previsto = equivalence_arrays(retornos_analisar, retornos_previsto)


        # print(f'Ticker: {stock_data.tickers[j]}')
        # print(stat.correlation(retornos_analisar, retornos_previsto))
        mask = (retornos_analisar > 0.01) | (retornos_analisar < -0.01)
        arrayA = retornos_analisar[mask]
        arrayB = retornos_previsto[mask]
        # print(stat.correlation(arrayA, arrayB))
        # stat.print_statistics(arrayA, arrayB)


# backtest
capital_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
resultado_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
capital_alocacao[:, -1] = 1
equity =[100]

# print(type(stock_data.price_matrix))
# print(stock_data.price_matrix.shape)
# print(stock_data.price_matrix[0,:])
# print('----- ### -----')
# print(type(capital_alocacao))
# print(capital_alocacao.shape)
# # print(capital_alocacao[0,:])


# retornos = np.diff(stock_data.price_matrix, axis=0) / stock_data.price_matrix[:-1]
# print(type(retornos))
# print(retornos.shape)
# print(retornos[0,:])


# for i in range(10, len(weekdays)):

#     cash = 1

#     for i2, ticker in enumerate(stock_data.tickers):

#         if stock_data.price_matrix[i-6, i2] != 0:

#             if weekdays[i] == 'sexta':

#                 weekly_return = backtest.calculate_return(stock_data.price_matrix[i-5, i2], stock_data.price_matrix[i-1, i2])
#                 if weekly_return < -0.01:
#                     capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "buy")
#                 elif weekly_return > 0.01:
#                     capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "sell")                

#             elif weekdays[i] == 'segunda':

#                 weekly_return = backtest.calculate_return(stock_data.price_matrix[i-6, i2], stock_data.price_matrix[i-1, i2])
#                 if weekly_return < -0.01:
#                     capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "sell")
#                 elif weekly_return > 0.01:
#                     capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "buy")    

#             else:
#                 continue
            
#             if cash < 0 or cash >= 2.1:
#                 print('SYSTEM ERROR - cash out of reality')
#                 print(cash)
#                 sys.exit()
#             else:
#                 capital_alocacao[i, -1] = cash

# print(capital_alocacao[:40])


for i in range(10, len(weekdays)): # len(weekdays)): # loop passando dia a dia 

    cash = 1

    for i2 in range(len(stock_data.tickers)):

        if stock_data.price_matrix[i-6, i2] != 0:

            if weekdays[i] == 'sexta': # calcular o retorno da semana de sexta a quinta

                weekly_return = backtest.calculate_weekly_return(stock_data.price_matrix[i-5, i2], stock_data.price_matrix[i-1, i2])
                if weekly_return < -0.01: 
                    capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "buy")
                elif  weekly_return > 0.01: 
                    capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "sell")    
            
            elif weekdays[i] == 'segunda':  # calcular o retorno da semana de sexta a sexta

                weekly_return = backtest.calculate_weekly_return(stock_data.price_matrix[i-6, i2], stock_data.price_matrix[i-1, i2])
                if weekly_return < -0.01: 
                    capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "sell")   
                elif  weekly_return > 0.01: 
                    capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "buy")
            
            if cash < 0 or cash >= 2.1:
                print('SYSTEM ERROR - cash out of reality')
                print(cash)
                sys.exit()
            else:
                capital_alocacao[i, -1] = cash


for i, day in enumerate(stock_data.dates[1:], start=1):

    for i2, ticker in enumerate(stock_data.tickers):
        
        if stock_data.price_matrix[i-1, i2] != 0: 

            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return

    equity.append((np.sum(resultado_alocacao[i, :])+1) * equity[i-1])

# print(capital_alocacao[123,:])
# print(resultado_alocacao[123,:])
# print(np.sum(resultado_alocacao[123,:]))
# print(100*(1+np.sum(resultado_alocacao[123,:])))
# print(capital_alocacao[:40])  

print(len(stock_data.dates))
print(len(equity))

plt.plot(stock_data.dates, equity, color='blue')
plt.title('Scatter plot entre tensor1 e tensor2')
plt.xlabel('tensor1')
plt.ylabel('tensor2')
plt.xticks(rotation=45)

every_nth_date = 50  # Mostrar a cada 50 dias
visible_dates = stock_data.dates[::every_nth_date]
plt.xticks(visible_dates)

plt.tight_layout()  # Ajusta o layout para evitar sobreposição de rótulos
plt.show()
