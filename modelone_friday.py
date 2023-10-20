import torch
from datetime import datetime

class LogData:
    def __init__(self):
        self.data = []
        self.ativo = []
        self.abertura = torch.tensor([])
        self.minima = torch.tensor([])
        self.maxima = torch.tensor([])
        self.fechamento = torch.tensor([])

    @staticmethod
    def read_log_and_fill_class(file_path):
        log_data_obj = LogData()

        with open(file_path, 'r', encoding='UTF-16') as f:
            for line in f:
                ativo, data, abertura, minima, maxima, fechamento = line.strip().split(',')
                log_data_obj.ativo.append(ativo)
                log_data_obj.data.append(data)
                log_data_obj.abertura = torch.cat([log_data_obj.abertura, torch.tensor([float(abertura)])])
                log_data_obj.minima = torch.cat([log_data_obj.minima, torch.tensor([float(minima)])])
                log_data_obj.maxima = torch.cat([log_data_obj.maxima, torch.tensor([float(maxima)])])                
                log_data_obj.fechamento = torch.cat([log_data_obj.fechamento, torch.tensor([float(fechamento)])])
        log_data_obj.data = [datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S').date() for date_str in log_data_obj.data]                
        return log_data_obj




## Execução

file_path = "/Users/gabrielassuncao/CARTOR/quant/Cartor--quant/research_2023/ibov_data.txt"
log_data = LogData.read_log_and_fill_class(file_path)

print(log_data.data[2])
print(log_data.ativo[2])
print(log_data.abertura[2].item())
print(log_data.minima[2].item())
print(log_data.maxima[2].item())
print(log_data.fechamento[2].item())

