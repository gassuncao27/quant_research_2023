
import os
import chardet

from dotenv import load_dotenv
from log_data import LogData, StockData

import chardet
import matplotlib.pyplot as plt

## upload data
load_dotenv()
ambiente_local = os.getenv('AMBIENTE_WIN')
data_path = 'acoes_precos.txt'

file_path = ambiente_local + data_path
# print(file_path)
stock_data = StockData(file_path)
# stock_data.display()
# print(stock_data.price_matrix.shape)
# print(stock_data.tickers)
# print(stock_data.dates)
# print(stock_data.price_matrix[-1,:])

print(stock_data.tickers[6])
plt.plot(stock_data.price_matrix[:,6], color='blue')
plt.title('Scatter plot entre tensor1 e tensor2')
plt.xlabel('tensor1')
plt.ylabel('tensor2')
plt.show()
