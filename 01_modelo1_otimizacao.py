
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

# Print de avaliacao da estratégia
print('\n AVALIAÇÃO BACKTESTS - OTIMIZAÇÃO \n')

a = 0.00
z = 1 
for x in range(0, 10):
    # print(f'treshold: {a}')
    a -= 0.01 

    for w in range(5, 30, 5):
        # print(f'dias posicionados {i}')

        z = 1
        while z <= 12:
        
            # print('finalizado\n')

            ## upload data
            retorno_treshold = x
            periodo_position = w
            tipo_arquivoportfolio = str(z)

            df = pd.read_parquet('base_acoes.parquet'); df.fillna(0, inplace=True)
            ambiente_local = os.getenv('AMBIENTE_MAC'); datapath_cdi = 'cdi_historico.xlsx'
            cdi_data = backtest.cdidata_extract(ambiente_local+datapath_cdi)
            portfolio_liquidez, tickers_strategy = backtest.tratamento_portativos('portfolio_quant_RANK_'+tipo_arquivoportfolio+'.csv')

            # criando objetos para o backtest
            stock_data = StockData(df, tickers_selecionados=tickers_strategy)
            stock_data.dates = stock_data.dates[252:-2]
            stock_data.price_matrix = stock_data.price_matrix[252:-2, :]
            valores_nao_comuns = [valor for valor in tickers_strategy if valor not in stock_data.tickers]
            weekdays = [StockData.date_to_weekday(date) for date in stock_data.dates]

            # backtest ( transformar em uma função )
            # backtest
            contagem_dias = np.zeros(stock_data.price_matrix.shape[1])
            capital_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
            resultado_alocacao = np.zeros((stock_data.price_matrix.shape[0], stock_data.price_matrix.shape[1] + 1))
            capital_alocacao[0, -1] = 1
            cash = 1.0

            for i, day in enumerate(stock_data.dates):

                ano = str(day.year); mes = str(day.month) # identificar mes e ano
                cash = capital_alocacao[0, -1]

                if len(mes) == 1:
                    mes = '0' + mes    

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

                                if retorno_semanal < retorno_treshold and cash >= 0.10:
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

            column_titles = ['Strategy'+'_'+str(a)+'_'+str(w)+'_'+str(z)]
            curva_analisada = [equity]

            for i, capital in enumerate (curva_analisada):
                print(f'\nAnalise: {column_titles[i]}')
                print(f'Retorno Total {st_eval.total_return(capital)}')
                print(f'Retorno Anual {round(st_eval.calcular_retorno_anualizado(capital), 2)}')
                print(f'Volatilidade Anual {round(st_eval.calcular_vol_negativos(capital), 2)}')
                print(f'Dias Positivos {st_eval.percentage_positive_trades(capital)}%')
                print(f'Drawndown Máximo {st_eval.max_drawdown(capital)*-1}')
                print(f'Sharpe Ratio {round(st_eval.calcular_retorno_anualizado(capital) / st_eval.calcular_vol_negativos(capital), 2)}')
                print('#### // ####\n')

            if z == 1:
                z+=2
            else:
                z*=2