import requests
import json
import time
import sys
import os

from dotenv import load_dotenv

ticker_list = ['VALE3','PETR4','ITUB4','BBDC4','BBAS3','ELET3', 'BOVA11', 
               'ABEV3','WEGE3','ITSA4','RENT3','JBSS3','RADL3', 'CSNA3' , 'EQTL3']

load_dotenv()
endpoint = os.getenv('ENDPOINT')
token = os.getenv('TOKEN')

# baixar dados api
print(len(ticker_list))
data = {}
for ticker in ticker_list:
    print(ticker)
    parameters = {
            "period_init": "2020-04-20",
            "period_end": "2023-10-20"
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
with open('acoes_precos_poscovid.txt', 'w') as file:
    for ticker, values in data.items():
        if values:  # verifica se os valores não são None
            for date, close_price in values.items():
                line = f"{ticker}, {date}, {close_price}\n"
                file.write(line)