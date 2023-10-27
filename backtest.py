
import numpy as np
import pandas as pd
from datetime import datetime


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