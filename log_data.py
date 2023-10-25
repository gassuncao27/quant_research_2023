import torch
import chardet

import numpy as np

from datetime import datetime

class LogData:
    def __init__(self):
        self.data = []        
        self.weekday = []
        self.ativo = []
        self.abertura = torch.tensor([])
        self.minima = torch.tensor([])
        self.maxima = torch.tensor([])
        self.fechamento = torch.tensor([])

    def guess_file_properties(file_path, num_lines=10):
        with open(file_path, 'rb') as file:
            rawdata = file.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
        
        delimiters = [',', ';', '\t', ' ']
        counts = {delimiter: 0 for delimiter in delimiters}

        with open(file_path, 'r', encoding=encoding, errors="ignore") as file:
            for _ in range(num_lines):
                line = file.readline()
                for delimiter in delimiters:
                    counts[delimiter] += line.count(delimiter)
        delimiter = max(counts, key=counts.get)
        return delimiter, encoding

    # @staticmethod
    def read_log_and_fill_class(file_path, encoding_str, delimiter_str):
        log_data_obj = LogData()

        with open(file_path, 'r', encoding=encoding_str) as f:            
            for line in f:
                ativo, data, abertura, minima, maxima, fechamento = line.strip().split(delimiter_str)
                log_data_obj.ativo.append(ativo)
                log_data_obj.data.append(data)
                log_data_obj.abertura = torch.cat([log_data_obj.abertura, torch.tensor([float(abertura)])])
                log_data_obj.minima = torch.cat([log_data_obj.minima, torch.tensor([float(minima)])])
                log_data_obj.maxima = torch.cat([log_data_obj.maxima, torch.tensor([float(maxima)])])                
                log_data_obj.fechamento = torch.cat([log_data_obj.fechamento, torch.tensor([float(fechamento)])])
        log_data_obj.data = [datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S').date() for date_str in log_data_obj.data]       
        dias_da_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
        log_data_obj.weekday = [dias_da_semana[date_obj.weekday()] for date_obj in log_data_obj.data]

        return log_data_obj

    
    def reverse_attributes(self):
        self.data.reverse()
        self.weekday.reverse()
        self.ativo.reverse()
        self.abertura = torch.flip(self.abertura, [0])
        self.minima = torch.flip(self.minima, [0])
        self.maxima = torch.flip(self.maxima, [0])
        self.fechamento = torch.flip(self.fechamento, [0])        





class StockData:
    def __init__(self, file_path):
        # Ler os dados
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Processar os dados
        data = [line.strip().split(', ') for line in lines]

        # Obter listas únicas de datas e ativos mantendo a ordem
        self.tickers = []
        self.dates = []
        for item in data:
            ticker, date, _ = item
            if ticker not in self.tickers:
                self.tickers.append(ticker)
            if date not in self.dates:
                self.dates.append(date)

        # Criar matriz de preços
        self.price_matrix = np.zeros((len(self.dates), len(self.tickers)))
        
        # Preencher a matriz de preços
        for item in data:
            ticker, date, price = item
            row_idx = self.dates.index(date)
            col_idx = self.tickers.index(ticker)
            self.price_matrix[row_idx][col_idx] = float(price)
    
    def display(self):
        print("Tickers:", self.tickers)
        print("Dates:", self.dates)
        print("Price Matrix:")
        print(self.price_matrix)

    def date_to_weekday(date_str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        days = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        return days[date_obj.weekday()]