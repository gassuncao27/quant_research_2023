
import numpy as np
import pandas as pd


def calculate_return(start_price, end_price):
    return end_price / start_price - 1

def simple_update_capital(cash, direction):
    if direction == "buy" and cash > 0.10:
        cash -= 0.10
        return 0.10, cash
    elif direction == "sell" and cash < 2.00:
        cash += 0.10
        return -0.10, cash
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
    
    df = pd.read_excel('cdi_historico.xlsx', engine='openpyxl')
    array = df.iloc[:, :2].values
    months = [item.month for item in array[:, 0]]
    years = [item.year for item in array[:, 0]]
    array = np.column_stack((array, months, years))

    return array