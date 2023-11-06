
import pandas as pd
import numpy as np
import backtest
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import strategy_evaluation as st_eval

from log_data import StockData

import os

from dotenv import load_dotenv
from log_data import StockData
from datetime import datetime

import sys
import backtest

load_dotenv()

# VARIAVEIS GLOBAIS BACKTEST
retorno_treshold = float(input("\nTreshold Variação: "))
periodo_position = int(input('Qtd dias posicionado: ')) 


## upload data
df = pd.read_parquet('base_acoes.parquet'); df.fillna(0, inplace=True)
ambiente_local = os.getenv('AMBIENTE_MAC'); datapath_cdi = 'cdi_historico.xlsx'
cdi_data = backtest.cdidata_extract(ambiente_local+datapath_cdi)
print("\n // Upload CDI e Stocks Data // \n")
portfolio_liquidez, tickers_strategy = backtest.tratamento_portativos('portfolio_quant.csv')


# criando objetos para o backtest
stock_data = StockData(df, tickers_selecionados=tickers_strategy)
stock_data.dates = stock_data.dates[:-2]
stock_data.price_matrix = stock_data.price_matrix[:-2, :]
valores_nao_comuns = [valor for valor in tickers_strategy if valor not in stock_data.tickers]
weekdays = [StockData.date_to_weekday(date) for date in stock_data.dates]


# Inicio do piloto / demonstratti)
print('\nInicio Backtest: ', stock_data.dates[0])
print('Fim do Backtest: ', stock_data.dates[-1])
print('Return Benchmark _ Strategy Long Bova11: ', round( stock_data.price_matrix[-1,stock_data.tickers.index('BOVA11')]/ stock_data.price_matrix[0,stock_data.tickers.index('BOVA11')] - 1, 2), '\n')


# backtest ( transformar em uma função )
# backtest
contagem_dias = np.zeros(stock_data.price_matrix.shape[1])
capital_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
resultado_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
capital_alocacao[0, -1] = 1
cash = 1.0

for i, day in enumerate(stock_data.dates):

    ano = day.year; mes = day.month # identificar mes e ano
    cash = capital_alocacao[0, -1]

    stocks2trade = portfolio_liquidez[(portfolio_liquidez['Ano'] == str(ano)) & (portfolio_liquidez['Mes'] == str(mes))]    # pegar a linha do joao com o portfolio desejado
    if not stocks2trade.empty:
        stocks2trade = stocks2trade.iloc[0,1:-2].tolist()
    else:
        stocks2trade = []
        print('Falta mes e ano na portfolio de liquidez')
        sys.exit()        

    for i2, tickers in enumerate(stocks2trade):
        if tickers != 'XPBR31':

            capital_alocacao[i, stock_data.tickers.index(tickers)] = capital_alocacao[i-1, stock_data.tickers.index(tickers)]
            if stock_data.price_matrix[i, stock_data.tickers.index(tickers)] != 0:

                if capital_alocacao[i, stock_data.tickers.index(tickers)] != 0:
                    contagem_dias[stock_data.tickers.index(tickers)] += 1

                    if contagem_dias[stock_data.tickers.index(tickers)] >= int(periodo_position): 
                        capital_alocacao[i, stock_data.tickers.index(tickers)] = 0
                        contagem_dias[stock_data.tickers.index(tickers)] = 0 

                if weekdays[i] == 'sexta':
                    preco_ontem = stock_data.price_matrix[i-1, stock_data.tickers.index(tickers)]
                    preco_sextapassada = stock_data.price_matrix[i-4, stock_data.tickers.index(tickers)]
                    retorno_semanal = backtest.calculate_return(preco_sextapassada, preco_ontem)

                    if retorno_semanal > retorno_treshold and cash >= 0.10:
                        capital_alocacao[i, stock_data.tickers.index(tickers)], cash = backtest.simple_update_capital(cash, 'buy')                        
                        contagem_dias[stock_data.tickers.index(tickers)] = 0
                    
                    else:
                        continue

    if cash < -0.001 or cash > 1:
        print('SYSTEM ERROR - cash out of reality')
        print(cash)
        sys.exit()
    else:
        capital_alocacao[i, -1] = cash

# 4 curvas de capital
# Building Equity Curve
equity =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    for i2, ticker in enumerate(stock_data.tickers):
        if stock_data.price_matrix[i-1, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return
    equity.append((np.sum(resultado_alocacao[i, :])) * equity[i-1] + equity[i-1])

# Building Equity with cash
equity_cash =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    ano = day.year; mes = day.month
    for i2 in range(capital_alocacao.shape[1]):
        if i2 == (capital_alocacao.shape[1]-1): # if it is cash
            linhas_correspondentes = cdi_data[(cdi_data[:, 2] == mes) & (cdi_data[:, 3] == ano)]
            position_ticker = capital_alocacao[i, i2]
            day_return = (linhas_correspondentes[0][1]+1)**(1/252)-1
            resultado_alocacao[i, i2] = position_ticker*day_return
        elif stock_data.price_matrix[i-1, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return
    equity_cash.append((np.sum(resultado_alocacao[i, :])) * equity_cash[i-1] + equity_cash[i-1])

# Building Equity only BOVA11
equity_benchmark =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    day_return = backtest.calculate_return(stock_data.price_matrix[i-1, stock_data.tickers.index('BOVA11')], stock_data.price_matrix[i, stock_data.tickers.index('BOVA11')])
    equity_benchmark.append(day_return * equity_benchmark[i-1] + equity_benchmark[i-1])

# Building Equity only BOVA11 0.5 CASH
equity_benchmark_cash =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    linhas_correspondentes = cdi_data[(cdi_data[:, 2] == mes) & (cdi_data[:, 3] == ano)]
    position_ticker = 0.5
    day_return_cash = (linhas_correspondentes[0][1]+1)**(1/252)-1
    day_return = backtest.calculate_return(stock_data.price_matrix[i-1, stock_data.tickers.index('BOVA11')], stock_data.price_matrix[i, stock_data.tickers.index('BOVA11')])
    equity_benchmark_cash.append( (day_return * equity_benchmark_cash[i-1]*0.5) + (day_return_cash * equity_benchmark_cash[i-1]*0.5) + equity_benchmark_cash[i-1])


# Print de avaliacao da estratégia
print('\n AVALIAÇÃO BACKTESTS \n')

column_titles = ['Strategy', 'Strategy with Cash', 'BOVA', 'BOVA & CASH 50/50']
curva_analisada = [equity, equity_cash, equity_benchmark, equity_benchmark_cash]

for i, capital in enumerate (curva_analisada):
    print(f'Analise: {column_titles[i]}')
    print(f'Retorno Total {st_eval.total_return(capital)}')
    print(f'Retorno Anual {round(st_eval.calcular_retorno_anualizado(capital), 2)}')
    print(f'Volatilidade Anual {round(st_eval.calcular_vol_negativos(capital), 2)}')
    print(f'Dias Positivos {st_eval.percentage_positive_trades(capital)}%')
    print(f'Drawndown Máximo {st_eval.max_drawdown(capital)*-1}')
    print(f'Sharpe Ratio {round(st_eval.calcular_retorno_anualizado(capital) / st_eval.calcular_vol_negativos(capital), 2)}\n')
    print('\n#### // ####\n')



# plot curvas
equity = np.array(equity)
equity_cash = np.array(equity_cash)
equity_benchmark = np.array(equity_benchmark) 
equity_benchmark_cash = np.array(equity_benchmark_cash)
result_column_stack = np.column_stack((equity, equity_cash, equity_benchmark, equity_benchmark_cash))
column_titles = ['Strategy Equity', 'Strategy with Cash', 'Benchmark', 'Benchmark with 0.5 cash']

colors = ['blue', 'green', 'red', 'black']  
plt.figure(figsize=(10,6))

# datestring = np.array(stock_data.dates)
dates = stock_data.dates
for i, color in enumerate(colors):
    plt.plot(dates, result_column_stack[:,i], color=color, label=column_titles[i])
plt.title('Gráfico das colunas')
plt.xlabel('Data')
plt.ylabel('Valor')
plt.legend()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=150))  
plt.gcf().autofmt_xdate()
plt.show()

# sys.exit()

# 2 curvas de capital
# insignia e mach5
# Dados msql
# baixa dados do insignia e mach5 
import mysql.connector
import warnings
warnings.filterwarnings('ignore')

db = mysql.connector.connect(
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    host=os.getenv('MYSQL_HOST'),
    port=os.getenv('MYSQL_PORT'),
    database=os.getenv('MYSQL_DATABASE'),
    )

msql = pd.read_sql_query("SELECT * from cota_fundos", db)
msql = msql.reset_index(drop=True) 


# Curva de Capital Insignia
# Backtest Insignia
insignia_pl =[100]
dates = np.array(msql['Date']); dates = dates[5:-2]
ativo = ['insignia']
cotacao_insignia = np.array(msql['quota_insignia']);  cotacao_insignia = cotacao_insignia[5:-2]
array_posicao = np.ones(cotacao_insignia.shape)

for i, day in enumerate(dates[1:], start=1):

    position_acao = array_posicao[i]
    retorno_dia = backtest.calculate_return(cotacao_insignia[i-1], cotacao_insignia[i])
    insignia_pl.append( retorno_dia * insignia_pl[i-1] + insignia_pl[i-1])\

# Curva de Capital Mach5
# Backtest MACH5
mach5_pl =[100]
dates = np.array(msql['Date']); dates = dates[5:-2]
ativo = ['mach5']
cotacao_mach5 = np.array(msql['quota_mach5']); cotacao_mach5 = cotacao_mach5[5:-2]  
array_posicao = np.ones(cotacao_mach5.shape)

print(f'Inicio: {dates[0]}')
print(f'Fim: {dates[-1]}')
# print(cotacao_mach5.shape)
# print(array_posicao.shape)

for i, day in enumerate(dates[1:], start=1):

    position_acao = array_posicao[i]
    retorno_dia = backtest.calculate_return(cotacao_mach5[i-1], cotacao_mach5[i])
    mach5_pl.append( retorno_dia * mach5_pl[i-1] + mach5_pl[i-1])


stock_data.dates = stock_data.dates[-308:]
capital_alocacao = capital_alocacao[-308:]
stock_data.price_matrix = stock_data.price_matrix[-308:,:]

# Building Equity Curve
equity =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    for i2, ticker in enumerate(stock_data.tickers):
        if stock_data.price_matrix[i-1, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return
    equity.append((np.sum(resultado_alocacao[i, :])) * equity[i-1] + equity[i-1])

# Building Equity with cash
equity_cash =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    ano = day.year; mes = day.month
    for i2 in range(capital_alocacao.shape[1]):
        if i2 == (capital_alocacao.shape[1]-1): # if it is cash
            linhas_correspondentes = cdi_data[(cdi_data[:, 2] == mes) & (cdi_data[:, 3] == ano)]
            position_ticker = capital_alocacao[i, i2]
            day_return = (linhas_correspondentes[0][1]+1)**(1/252)-1
            resultado_alocacao[i, i2] = position_ticker*day_return
        elif stock_data.price_matrix[i-1, i2] != 0: 
            position_ticker = capital_alocacao[i, i2]
            day_return = backtest.calculate_return(stock_data.price_matrix[i-1, i2], stock_data.price_matrix[i, i2])
            resultado_alocacao[i, i2] = position_ticker*day_return
    equity_cash.append((np.sum(resultado_alocacao[i, :])) * equity_cash[i-1] + equity_cash[i-1])

# Building Equity only BOVA11 0.5 CASH
equity_benchmark_cash =[100]
for i, day in enumerate(stock_data.dates[1:], start=1):
    linhas_correspondentes = cdi_data[(cdi_data[:, 2] == mes) & (cdi_data[:, 3] == ano)]
    position_ticker = 0.5
    day_return_cash = (linhas_correspondentes[0][1]+1)**(1/252)-1
    day_return = backtest.calculate_return(stock_data.price_matrix[i-1, stock_data.tickers.index('BOVA11')], stock_data.price_matrix[i, stock_data.tickers.index('BOVA11')])
    equity_benchmark_cash.append( (day_return * equity_benchmark_cash[i-1]*0.5) + (day_return_cash * equity_benchmark_cash[i-1]*0.5) + equity_benchmark_cash[i-1])

# Print de avaliacao da estratégia
print('\n AVALIAÇÃO BACKTESTS \n')

column_titles = ['BOVA & CASH 50/50', 'Strategy with Cash', 'Mach5', 'Insignia']
curva_analisada = [equity_benchmark_cash, equity_cash, mach5_pl, insignia_pl]

for i, capital in enumerate (curva_analisada):
    print(f'Analise: {column_titles[i]}')
    print(f'Retorno Total {st_eval.total_return(capital)}')
    print(f'Retorno Anual {round(st_eval.calcular_retorno_anualizado(capital), 2)}')
    print(f'Volatilidade Anual {round(st_eval.calcular_vol_negativos(capital), 2)}')
    print(f'Dias Positivos {st_eval.percentage_positive_trades(capital)}%')
    print(f'Drawndown Máximo {st_eval.max_drawdown(capital)*-1}\n')
    print(f'Sharpe Ratio {round(st_eval.calcular_retorno_anualizado(capital) / st_eval.calcular_vol_negativos(capital), 2)}\n')
    print('\n#### // ####\n')


# plot curvas
equity = np.array(equity_benchmark_cash)
equity_cash = np.array(equity_cash)
equity_benchmark = np.array(insignia_pl) 
equity_benchmark_cash = np.array(mach5_pl)

# result_column_stack = np.column_stack((equity, equity_cash, equity_benchmark, equity_benchmark_cash))
# column_titles = ['BOVA & CASH 50/50', 'Strategy with Cash', 'Insignia', 'Mach5']

result_column_stack = np.column_stack((equity_cash, equity_benchmark_cash))
column_titles = ['Strategy with Cash', 'Mach5']

# colors = ['blue', 'green', 'red', 'black']  

colors = ['blue', 'green']  
plt.figure(figsize=(10,6))

# datestring = np.array(stock_data.dates)
dates = stock_data.dates
for i, color in enumerate(colors):
    plt.plot(dates, result_column_stack[:,i], color=color, label=column_titles[i])
plt.title('Gráfico das colunas')
plt.xlabel('Data')
plt.ylabel('Valor')
plt.legend()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=30))  
plt.gcf().autofmt_xdate()
plt.show()