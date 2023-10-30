import requests
import json
import time
import sys
import os

import pandas as pd
from dotenv import load_dotenv

def valores_unicos_df(dataframe):
    valores_unicos = []
    for coluna in dataframe.columns[1:]:
        valores_unicos_coluna = list(dataframe[coluna].unique())
        valores_unicos.extend(valores_unicos_coluna)
    valores_unicos = list(set(valores_unicos))
    return valores_unicos

stocks = pd.read_csv('portfolio_quant.csv', delimiter=',', header=None)
ticker_list = valores_unicos_df(stocks)
print(len(ticker_list))

# ticker_list = ['VALE3','PETR4','ITUB4','BBDC4','BBAS3','ELET3', 'BOVA11', 
#                'ABEV3','WEGE3','ITSA4','RENT3','JBSS3','RADL3', 'CSNA3' , 'EQTL3']

load_dotenv()
endpoint = os.getenv('ENDPOINT')
token = os.getenv('TOKEN')

# baixar dados api
print(len(ticker_list))
data = {}
for ticker in ticker_list:
    print(ticker)
    parameters = {
            "period_init": "2010-01-01",
            "period_end": "2023-10-25"
        }
        
    headers = { 'Authorization': f'Bearer {token}' }
    route = f"/tickers/{ticker}/quotes"

    # print(endpoint+route)
    response= requests.get(str(endpoint) + route, headers=headers, params=parameters)
    time.sleep(1)
    try:
        json_response = json.loads(response.text)
        if len(json_response) > 0:
            data[ticker] = {}
            for info in json_response:
                # data[ticker][info["date"]] = info["close"]
                data[ticker][info["date"]] = info["adj_close"]                
                # print(f'\t{type(info["date"])} {type(info["close"])}')
    except Exception as e:
        data[ticker] = None
        print(e.args)

# arquivo txt
with open('prices_portfolioquant.txt', 'w') as file:
    for ticker, values in data.items():
        if values:  # verifica se os valores não são None
            for date, close_price in values.items():
                line = f"{ticker},{date},{close_price}\n"
                file.write(line)