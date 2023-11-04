
import os

from dotenv import load_dotenv
from log_data import StockData
from datetime import datetime

import sys
import backtest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import strategy_evaluation as st_eval

## upload data
load_dotenv()
ambiente_local = os.getenv('AMBIENTE_MAC')
datapath_portfolio = 'portfolio_quant.csv'
datapath_cdi = 'cdi_historico.xlsx'
datapath_prices = 'prices_portfolioquant.txt'

cdi_data = backtest.cdidata_extract(ambiente_local+datapath_cdi)
file_path = ambiente_local + datapath_prices
stock_data = StockData(file_path)
weekdays = [StockData.date_to_weekday(date) for date in stock_data.dates]
stocks_2trade = pd.read_csv(ambiente_local+datapath_portfolio, delimiter=',', header=None)

print(stocks_2trade.head(5))
print('Inicio Backtest: ', stock_data.dates[0])
print('Fim do Backtest: ', stock_data.dates[-1])
print('Return Benchmark _ Strategy Long Bova11: ', round( stock_data.price_matrix[-1,6]/ stock_data.price_matrix[0,6] - 1, 2),'\n')

# backtest
contagem = np.zeros(stock_data.price_matrix.shape[1])
capital_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
resultado_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
capital_alocacao[:, -1] = 1


# Alocação portfolio
retorno_treshold = 0.01
periodo_position = input("Nr de dias posicionado: ")
cash = 1
for i, day in enumerate(stock_data.dates):
    for i2, ticker in enumerate(stock_data.tickers):

        if stock_data.price_matrix[i-5, i2] != 0:
            # tratamento posição já existente
            capital_alocacao[i, i2] = capital_alocacao[i-1, i2]   
            if capital_alocacao[i-1, i2] != 0: # se posicionado, conta-se dias posicionados
                contagem[i2] += 1
            if contagem[i2] > int(periodo_position): # se tempo de posição se excede vende
                capital_alocacao[i, i2] = 0
                contagem[i2] = 0
                cash += capital_alocacao[i-1][i2]
            # verificação para abertura de nova posição
            if weekdays[i] == 'sexta': # pode ser segunda tbm
                weekly_return = backtest.calculate_return(stock_data.price_matrix[i-5, i2], stock_data.price_matrix[i-1, i2])
                if weekly_return < retorno_treshold*-1:
                    if contagem[i2] != 0:
                        cash += capital_alocacao[i-1][i2]
                    capital_alocacao[i, i2], cash = backtest.simple_update_capital(cash, "buy")
                    contagem[i2] = 0
            else:
                continue
    if cash < 0:
        print('SYSTEM ERROR - cash out of reality')
        print(cash)
        sys.exit()
    else:
        # cash = 1 - np.sum(capital_alocacao[i, :-1])
        capital_alocacao[i, -1] = cash
print('\n',capital_alocacao[30:60, 0:6])                

# Building Equity Curve
equity =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    for i2, ticker in enumerate(stock_data.tickers):
        if stock_data.price_matrix[i-1, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return
    equity.append((np.sum(resultado_alocacao[i, :])) * equity[i-1] + equity[i-1])

# Building Equity Curve with cash
equity_cash =[100]
date_structure = backtest.datestring_tostruct(stock_data.dates)
for i, day in enumerate(stock_data.dates[1:], start=1):

    for i2 in range(capital_alocacao.shape[1]):

        if i2 == (capital_alocacao.shape[1]-1): # if it is cash
            linhas_correspondentes = cdi_data[(cdi_data[:, 2] == date_structure[i,1]) & (cdi_data[:, 3] == date_structure[i,2])]
            position_ticker = capital_alocacao[i, i2]
            day_return = (linhas_correspondentes[0][1]+1)**(1/252)-1
            resultado_alocacao[i, i2] = position_ticker*day_return

        elif stock_data.price_matrix[i-1, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return

    equity_cash.append((np.sum(resultado_alocacao[i, :])) * equity_cash[i-1] + equity_cash[i-1])

# Building Equity Curve - Benchmark
equity_benchmark =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    day_return = backtest.calculate_return(stock_data.price_matrix[i-1, 6], stock_data.price_matrix[i, 6])
    equity_benchmark.append(day_return * equity_benchmark[i-1] + equity_benchmark[i-1])

# Print de avaliacao da estratégia
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
result_column_stack = np.column_stack((equity, equity_cash, equity_benchmark))
column_titles = ['Strategy Equity', 'Strategy with Cash', 'Benchmark']

colors = ['blue', 'green', 'red']  
plt.figure(figsize=(10,6))

# for i, color in enumerate(colors):
#     plt.plot(result_column_stack[:,i], color=color, label=column_titles[i])
# plt.title('Gráfico das colunas')
# plt.xlabel('Índice')
# plt.ylabel('Valor')
# plt.legend() 
# plt.show()


# colocar data no grafico de simulacao

# datestring = np.array(stock_data.dates)
print(type(stock_data.dates))
dates = [datetime.strptime(date, '%Y-%m-%d') for date in stock_data.dates]
for i, color in enumerate(colors):
    plt.plot(dates, result_column_stack[:,i], color=color, label=column_titles[i])

plt.title('Gráfico das colunas')
plt.xlabel('Data')
plt.ylabel('Valor')
plt.legend()

# Configura o formato da data no eixo x
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=150))  # Ajuste o intervalo conforme necessário

# Rotação das datas no eixo x para melhor visualização
plt.gcf().autofmt_xdate()

plt.show()