import requests
import json
import time

import sys

ticker_list = ['VALE3','PETR4','ITUB4','BBDC4','BBAS3','ELET3', 'BOVA11', 
               'B3SA3','ABEV3','WEGE3','ITSA4','RENT3','PRIO3','SUZB3','BPAC11','RADL3']


# baixar dados api
print(len(ticker_list))
data = {}
for ticker in ticker_list:
    print(ticker)
    parameters = {
            "period_init": "2018-10-20",
            "period_end": "2023-10-20"
        }

    endpoint = 'https://api.dadosdemercado.com.br/v1'
    token = '8eba33dfe1829adc8bcf8cad4538bc41'
    headers = { 'Authorization': f'Bearer {token}' }
    route = f"/tickers/{ticker}/quotes"

    # print(endpoint+route)
    response= requests.get(endpoint + route, headers=headers, params=parameters)
    time.sleep(1)
    try:
        json_response = json.loads(response.text)
        if len(json_response) > 0:
            data[ticker] = {}
            for info in json_response:
                data[ticker][info["date"]] = info["close"]
                # print(f'\t{type(info["date"])} {type(info["close"])}')
    except Exception as e:
        data[ticker] = None
        print(e.args)

# arquivo txt
with open('acoes_precos.txt', 'w') as file:
    for ticker, values in data.items():
        if values:  # verifica se os valores não são None
            for date, close_price in values.items():
                line = f"{ticker}, {date}, {close_price}\n"
                file.write(line)