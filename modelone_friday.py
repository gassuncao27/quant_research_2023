import torch
import warnings
import matplotlib.pyplot as plt

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


## Execução
# warnings.filterwarnings("ignore")
file_path = "/Users/gabrielassuncao/CARTOR/quant/quant_research_2023/ibov_data.txt"
log_data = LogData.read_log_and_fill_class(file_path)
LogData.reverse_attributes(log_data)

# print(log_data.data[2])
# print(log_data.ativo[2])
# print(log_data.abertura[2].item())
# print(log_data.minima[2].item())
# print(log_data.maxima[2].item())
# print(log_data.fechamento[:10])
# print(log_data.weekday[:10])

# definir valores de retorno a serem analisados e previstos
retornos_analisar = []
retornos_previsto = []
chave_loop = False
for i in range (len(log_data.weekday)):
    if chave_loop==False:
        if log_data.weekday[i] == 'quinta-feira':
            if i >= 4:                
                retornos_analisar.append(log_data.fechamento[i].item() / log_data.fechamento[i-4].item() - 1)
                chave_loop = True
    if chave_loop:
        if log_data.weekday[i] == 'sexta-feira':
            if log_data.weekday[i-1] == 'quinta-feira':
                retornos_previsto.append(log_data.fechamento[i].item() / log_data.fechamento[i-1].item() - 1)
                chave_loop = False

# transformando listas em tensor
retornos_previstos = torch.tensor(retornos_previsto)
retornos_analisar = torch.tensor(retornos_analisar)
retornos_analisar = retornos_analisar[:-1]


print(retornos_previstos.numel())
print(retornos_analisar.numel())

# # print(retornos_analisar)
# # # Crie o gráfico
# plt.figure(figsize=(12, 6))  # Defina o tamanho do gráfico
# plt.plot(retornos_previsto)
# plt.title('Preço de Abertura ao Longo do Tempo')
# plt.xlabel('Data')
# plt.ylabel('Preço de Abertura')
# # plt.legend()
# plt.grid(True)
# # plt.tight_layout()

# # Salve o gráfico como um arquivo .png
# # plt.savefig('/Users/gabrielassuncao/Desktop/preco_abertura.png')

# # Mostre o gráfico
# plt.show()



