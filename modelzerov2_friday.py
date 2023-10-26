
import os

from dotenv import load_dotenv
from log_data import LogData, StockData

import sys
import numpy as np
import backtest
import statistics_functions as stat
import matplotlib.pyplot as plt
import strategy_evaluation as st_eval

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
data_path = 'acoes_precos_last.txt'
data_path = 'acoes_precos_poscovid.txt'

file_path = ambiente_local + data_path
stock_data = StockData(file_path)
weekdays = [StockData.date_to_weekday(date) for date in stock_data.dates]

print('Inicio Backtest: ', stock_data.dates[0])
print('Fim do Backtest: ', stock_data.dates[-1])
print('Return Benchmark _ Strategy Long Bova11: ', stock_data.price_matrix[-1,6]/ stock_data.price_matrix[0,6] - 1,'\n')

# backtest
contagem = np.zeros(stock_data.price_matrix.shape[1])
capital_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
resultado_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
capital_alocacao[:, -1] = 1
equity =[100]

# estratégia = comprar na segunda ou na sexta feira e permanecer por x dias se a ação cair x % nos x dias anteriores
retorno_treshold = 0.01
periodo_position = input("Digite um número inteiro: ")

for i, day in enumerate(stock_data.dates):
    cash = 1
    for i2, ticker in enumerate(stock_data.tickers):

        if stock_data.price_matrix[i-5, i2] != 0:
            # tratamento posição já existente
            capital_alocacao[i, i2] = capital_alocacao[i-1, i2]   
            if capital_alocacao[i-1, i2] != 0: # se posicionado, conta-se dias posicionados
                contagem[i2] += 1
            if contagem[i2] > int(periodo_position): # se tempo de posição se excede vende
                capital_alocacao[i, i2] = 0
                contagem[i2] = 0

            # verificação para abertura de nova posição
            if weekdays[i] == 'sexta': # pode ser segunda tbm
                weekly_return = backtest.calculate_return(stock_data.price_matrix[i-5, i2], stock_data.price_matrix[i-1, i2])
                if weekly_return < retorno_treshold*-1:
                    capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "buy")
                    contagem[i2] = 0
            else:
                continue

            if cash < 0:
                print('SYSTEM ERROR - cash out of reality')
                print(cash)
                sys.exit()
            else:
                capital_alocacao[i, -1] = cash

# Building Equity Curve
for i, day in enumerate(stock_data.dates[1:], start=1):
    for i2, ticker in enumerate(stock_data.tickers):
        if stock_data.price_matrix[i-1, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return

    equity.append((np.sum(resultado_alocacao[i, :])) * equity[i-1] + equity[i-1])

# Building Equity Curve with cash
equity_cash =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    for i2 in range(capital_alocacao.shape[1]):

        if i2 == (capital_alocacao.shape[1]-1):
            position_ticker = capital_alocacao[i, i2]
            day_return = 1.05**(1/252)-1
            resultado_alocacao[i, i2] = position_ticker*day_return
        elif stock_data.price_matrix[i-1, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return
            
    equity_cash.append((np.sum(resultado_alocacao[i, :])) * equity_cash[i-1] + equity_cash[i-1])


print('\n STRATEGY EVALUATION \n')
print(f'Total Return Benchmark {st_eval.total_return(stock_data.price_matrix[:,6])}')
print(f'Profit Factor Benchmark {st_eval.profit_factor(stock_data.price_matrix[:,6])}')
print(f'Trade Accuracy Benchmark {st_eval.percentage_positive_trades(stock_data.price_matrix[:,6])}')
print(f'Maximum Drawndown Benchmark {st_eval.max_drawdown(stock_data.price_matrix[:,6])}')
print('\n#### // ####\n')
print(f'Total Return {st_eval.total_return(equity)}')
print(f'Profit Factor {st_eval.profit_factor(equity)}')
print(f'Trade Accuracy {st_eval.percentage_positive_trades(equity)}')
print(f'Maximum Drawndown {st_eval.max_drawdown(equity)}\n')
print('\n#### // ####\n')
print(f'Total Return with cash {st_eval.total_return(equity_cash)}')
print(f'Profit Factor with cash {st_eval.profit_factor(equity_cash)}')
print(f'Trade Accuracy with cash {st_eval.percentage_positive_trades(equity_cash)}')
print(f'Maximum Drawndown with cash {st_eval.max_drawdown(equity_cash)}\n')

equity = np.array(equity)
equity_cash = np.array(equity_cash)
result_column_stack = np.column_stack((equity, equity_cash))

colors = ['blue', 'green']  

plt.figure(figsize=(10,6))

for i, color in enumerate(colors):
    plt.plot(result_column_stack[:,i], color=color, label=f'Coluna {i+1}')

plt.title('Gráfico das colunas')
plt.xlabel('Índice')
plt.ylabel('Valor')
plt.legend() 
plt.show()