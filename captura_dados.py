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

ticker_list = [
    'VALE3', 'PETR4', 'ELET3', 'ABEV3', 'RENT3', 'ITSA4', 'B3SA3', 'WEGE3', 'BPAC11','EQTL3',
    'PRIO3', 'SUZB3', 'RADL3', 'RAIL3', 'GGBR4', 'UGPA3', 'RDOR3', 'JBSS3', 'VBBR3', 'BRFS3',
    'VIVT3', 'CSAN3', 'ENEV3', 'HAPV3', 'CMIG4', 'SBSP3', 'TOTS3', 'KLBN11','CPLE6','ENGI11',
    'EMBR3', 'HYPE3', 'LREN3', 'TIMS3', 'ASAI3', 'CCRO3', 'EGIE3', 'CSNA3', 'CMIN3', 'GOAU4', 
    'TAEE11','RRRP3', 'MULT3', 'CPFE3', 'MGLU3', 'FLRY3', 'YDUQ3', 'AZUL4', 'CRFB3', 'CYRE3', 
    'COGN3', 'BRAP4', 'BRKM5','IGTI11', 'CIEL3', "TTEN3", "ABCB4", "AERI3", "AALR3", "ALPA4",
    "ALUP11","AMBP3", "ANIM3", "ARZZ3", "ARML3", "BMOB3", "CEAB3", "CLSA3", "CSMG3", "CURY3", 
    "CVCB3", "DASA3", "DXCO3", "PNVL3", "DIRR3", "ECOR3", "ENAT3", "ESPA3", "EVEN3", "EZTC3", 
    "FESA4", "FRAS3", "GFSA3", "GOLL4", "GGPS3", "GRND3", "SBFG3", "GUAR3", "HBSA3", "INTB3",
    "MYPK3", "RANI3", "JHSF3", "KEPL3", "LAVV3", "LWSA3", "LOGG3", "LOGN3", "POMO4", "MRFG3", 
    "MATD3", "LEVE3", "BEEF3", "MOVI3", "MRVE3", "MLAS3", "ODPV3", "ONCO3", "ORVR3", "PCAR3", 
    "PGMN3", "RECV3", "PETZ3", "PLPL3", "PTBL3", "POSI3", "QUAL3", "LJQQ3", "RAPT4", "ROMI3",
    "SAPR11","STBP3", "SEQL3", "SEER3", "SIMH3", "SLCE3", "SMFT3", "TASA4", "TGMA3", "TEND3", 
    "TRIS3", "TUPY3", "UNIP6", "USIM5", "VLID3", "VULC3", "WIZC3", "ZAMP3", "BOVA11","SMAL11" ]

load_dotenv()
endpoint = os.getenv('ENDPOINT')
token = os.getenv('TOKEN')

# baixar dados api
print(len(ticker_list))
data = {}
for ticker in ticker_list:
    print(ticker)
    parameters = {
            "period_init": "2020-01-01",
            "period_end": "2023-12-01"
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
with open('stockprices_dashboard.txt', 'w') as file:
    for ticker, values in data.items():
        if values:  # verifica se os valores não são None
            for date, close_price in values.items():
                line = f"{ticker},{date},{close_price}\n"
                file.write(line)