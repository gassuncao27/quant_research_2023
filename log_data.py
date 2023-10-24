import torch
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
