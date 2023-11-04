
import numpy as np
import pandas as pd
from datetime import datetime


def calculate_return(start_price, end_price):
    return end_price / start_price - 1


def simple_update_capital(cash, direction):
    if direction == "buy" and cash >= 0.10:
        cash -= 0.10
        return 0.10, round(cash, 5)
    elif direction == "sell" and cash < 2.00:
        cash += 0.10
        return -0.10, round(cash, 5)
    return 0, cash


def moving_average(prices: np.array, window: int) -> np.array:
    return np.convolve(prices, np.ones(window)/window, mode='valid')


def bollinger_bands(prices: np.array, window: int, num_std: float=2) -> (np.array, np.array, np.array):
    ma = moving_average(prices, window)
    rolling_std = np.array([np.std(prices[i - window:i]) for i in range(window, len(prices) + 1)])
    upper_band = ma + (rolling_std * num_std)
    lower_band = ma - (rolling_std * num_std)
    
    return ma, upper_band, lower_band


def cdidata_extract(cdidata_path):
    
    df = pd.read_excel(cdidata_path, engine='openpyxl')
    cdi_array = df.iloc[:, :2].values
    months = [item.month for item in cdi_array[:, 0]]
    years = [item.year for item in cdi_array[:, 0]]
    cdi_array = np.column_stack((cdi_array, months, years))

    return cdi_array


def datestring_tostruct(date_list):

    data_datetimes = np.array([datetime.strptime(data, "%Y-%m-%d") for data in date_list])
    meses = np.array([data.month for data in data_datetimes])
    anos = np.array([data.year for data in data_datetimes])
    data_datetimes = np.column_stack((data_datetimes, meses, anos))

    return data_datetimes


# funcoes para lidar com o portfolio de liquidez

def valores_unicos_df(dataframe):
    valores_unicos = []
    for coluna in dataframe.columns[1:]:
        valores_unicos_coluna = list(dataframe[coluna].unique())
        valores_unicos.extend(valores_unicos_coluna)
    valores_unicos = list(set(valores_unicos))

    return valores_unicos


def extrair_ano(data):
    return data[:4]


def extrair_apos_hifen(data):
    partes = data.split('-')
    if len(partes) > 1:
        return partes[1]
    else:
        return None  


def tratamento_portativos(arquivo_portfolio):

    portfolio_liquidez = pd.read_csv(arquivo_portfolio, delimiter=',', header=None)
    portfolio_liquidez['Ano'] = portfolio_liquidez[0].apply(extrair_ano)
    portfolio_liquidez['Mes'] = portfolio_liquidez[0].apply(extrair_apos_hifen)
    tickers_strategy = valores_unicos_df(portfolio_liquidez)
    return portfolio_liquidez, tickers_strategy 


# curvas de capital



def curva_capital(capital_inicial, dias_historico, precos_historico, array_posicao, acoes_historico, resultado_alocacao):

    equity =[capital_inicial]
    # print(precos_historico.shape[0])
    # print(precos_historico.shape[1])
    # resultado_alocacao = np.zeros(precos_historico.shape[0], precos_historico.shape[1]+1)

    for i, day in enumerate(dias_historico[1:], start=1):
        for i2, ticker in enumerate(acoes_historico):
            if precos_historico[i-1, i2] != 0:

                position_acao = array_posicao[i, i2]
                retorno_dia = calculate_return(precos_historico[i-1, i2], precos_historico[i, i2])
                resultado_alocacao[i, i2] = position_acao*retorno_dia
        
        equity.append((np.sum(resultado_alocacao[i, :])) * equity[i-1] + equity[i-1])

    return equity