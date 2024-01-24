import pandas as pd
import numpy as np
import json

def upload_wallet(day_wallet):

    wallet_path = 'wallets/wallet_'+day_wallet+'.xlsx'
    fund_df = pd.read_excel(wallet_path, sheet_name='Sheet2_Fund')
    wallet_df = pd.read_excel(wallet_path, sheet_name='Sheet1_Wallet')

    return wallet_df, fund_df


def get_stocks_quantitites(wallet_df):
    
    quantities = []
    quantidade = np.array(wallet_df['quantidade'])
    operacao = np.array(wallet_df['operacao'])
    for i, quant in enumerate(quantidade):
        if operacao[i] == 'C':
            quantities.append(quant)
        else:
            quantities.append(quant*-1)
    return quantities


def get_data(date_end, historical_days, wallet_stocks):

    with open('stock_data/stocks_prices.json', 'r') as file:
        dict_stocks = json.load(file)
    with open('stock_data/dates.json', 'r') as file:
        dates = json.load(file)

    # dates
    date_data = []
    end = dates.index(date_end)
    start = end - historical_days
    for i in range(start, end+1):
        date_data.append(dates[i])

    price_data = np.zeros((historical_days+1, len(wallet_stocks)))
    column = 0
    for stock in wallet_stocks:
        price = []
        for data in date_data:
            price.append(dict_stocks[stock][data])
        price_data[:, column] = np.array(price)
        column += 1

    return price_data, np.array(date_data)


def get_returns(price_data):

    return_data = np.zeros((price_data.shape[0]-1, price_data.shape[1]))
    
    for column in range(return_data.shape[1]):
        for row in range(return_data.shape[0]):
            return_data[row, column] = (price_data[row+1, column] /
                                        price_data[row, column]  - 1)

    return return_data


def get_weights(prices, qte_positions, fund_df):

    index = fund_df[fund_df['Atributes'] == 'patliq'].index[0]
    pl_fund = float(fund_df.at[index, 'Value'])
    weights = ((prices * qte_positions) / pl_fund).round(4)
    
    return(weights)


def hist_wallet_returns(weights_data, return_data):

    pl_test = 1000
    financial_weights = weights_data * pl_test
    past_returns = []

    for row in range(return_data.shape[0]):
        financial_return = financial_weights * return_data[row, :]
        past_returns.append(np.sum(financial_return)/ pl_test)

    return np.array(past_returns)


def notional_wallet(wallet_qtes, wallet_prices):
    return np.sum(wallet_qtes * wallet_prices)


def calculate_var(portfolio_returns, confidence_level=0.95, time_period=1):

    var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)    
    return var


def wallet_volvar(day_wallet, fund_var=True):
    # wallet_df, fund_df = upload_wallet(day_wallet+"_v2")
    wallet_df, fund_df = upload_wallet(day_wallet)
    wallet_stocks = np.array(wallet_df['codigo'])
    wallet_prices = np.array(wallet_df['preco'])
    wallet_qtes = np.array(get_stocks_quantitites(wallet_df))
    
    print(day_wallet, "Notional: R$%.2f" % notional_wallet(wallet_qtes, wallet_prices))

    # stocks and qtes
    price_data, date_data = get_data(day_wallet, 21, wallet_stocks)
    return_data = get_returns(price_data)
    if fund_var == True:
        weights_data = get_weights(wallet_prices, wallet_qtes, fund_df)
    else:
        weights_data = get_weights_rv(wallet_prices, wallet_qtes, fund_df, wallet_df)
    wallet_returns = hist_wallet_returns(weights_data, return_data)

    vol = np.std(wallet_returns)
    vol_year = np.std(wallet_returns) * np.sqrt(252)
    var = calculate_var(wallet_returns, 0.99)

    return vol, vol_year, var


def get_weights_rv(prices, qte_positions, fund_df, wallet_df):

    wallet_stocks = np.array(wallet_df['codigo'])
    wallet_long = wallet_df[wallet_df['operacao'] == 'C']
    wallet_short = wallet_df[wallet_df['operacao'] != 'C']

    # RETIRAR DO CODIGO
    # criterio = wallet_short['codigo'] == 'BOVA11'
    # wallet_short.loc[criterio, 'quantidade'] = 474700
    # wallet_short.loc[criterio, 'financeiro'] = 58701402
    # RETIRAR DO CODIGO 

    long_stocks = np.array(wallet_long['codigo'])
    long_prices = np.array(wallet_long['preco'])
    long_qtes = np.array(get_stocks_quantitites(wallet_long))

    short_stocks = np.array(wallet_short['codigo'])
    short_prices = np.array(wallet_short['preco'])
    short_qtes = np.array(get_stocks_quantitites(wallet_short))

    weights_long = (long_prices * long_qtes) / np.sum(long_prices * long_qtes)
    weights_short = (short_prices * short_qtes) / np.sum(long_prices * long_qtes)

    dict_weights = {}
    for i, stock in enumerate(long_stocks):
        dict_weights[stock] = weights_long[i]
    for i, stock in enumerate(short_stocks):
        dict_weights[stock] = weights_short[i]        

    weights = np.zeros(len(wallet_stocks))
    for i, stock in enumerate(wallet_stocks):
        weights[i] = dict_weights[stock]

    return(weights)


def get_volatility_stock(stocks, day_start, past_days):
    
    stock_data, date = get_data(day_start, past_days, stocks)
    daily_return = get_returns(stock_data)
    return np.std(daily_return), daily_return


def calc_volatility_increase(day_wallet, assets_list, new_qte, type_position, wallet_df):

    # vol carteira normal
    vol_day, vol_year, var_wallet = wallet_volvar(day_wallet, False)

    stock_data, date = get_data(day_wallet, 21, assets_list)
    daily_return = get_returns(stock_data)
    price = stock_data[-1].item()

    print(wallet_df.columns)
    # vol carteira normal
    # fazer adicionando o ativo na ultima linha ou fazer consolidando os ativos
    wallet_df.loc[len(wallet_df)] = ['', assets_list[0], new_qte, new_qte*price, price,
                                     type_position, '', '', '']

    print(wallet_df.tail(5))
    

    pass


# import pandas as pd

# # Suponha que este seja o seu DataFrame original
# df = pd.DataFrame({
#     'coluna1': [1, 2, 3],
#     'coluna2': ['a', 'b', 'c']
# })

# # Nova linha a ser adicionada
# nova_linha = {'coluna1': 4, 'coluna2': 'd'}

# # Adicionando a nova linha
# df = df.append(nova_linha, ignore_index=True)

# print(df)