from log_data import LogData

import statistics_functions as stat

import torch
import sys
import matplotlib.pyplot as plt

import statistics_functions

from scipy import stats

import numpy
from datetime import datetime
 

def equivalence_arrays(array1, array2):
    tensor1 = torch.tensor(array1)
    tensor2 = torch.tensor(array2)
    if tensor1.numel() > tensor2.numel():
        tensor1 = tensor1[:tensor2.numel()]
    elif tensor1.numel() < tensor2.numel(): 
        print('ERROR - verify array composition and size')
        sys.exit()
    return tensor1, tensor2


## Execução
file_path = "/Users/gabrielassuncao/CARTOR/quant/quant_research_2023/vale_data.txt"
log_data = LogData.read_log_and_fill_class(file_path)
LogData.reverse_attributes(log_data)

# estudo
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


print(len(retornos_analisar))
print(len(retornos_previsto))

# transformando listas em tensor
retornos_analisar, retornos_previstos = equivalence_arrays(retornos_analisar, retornos_previsto)
# retornos_previstos = torch.tensor(retornos_previsto)
# retornos_analisar = torch.tensor(retornos_previsto)

# plt.plot(log_data.fechamento, color='blue')
# plt.title('Scatter plot entre tensor1 e tensor2')
# plt.xlabel('tensor1')
# plt.ylabel('tensor2')
# plt.show()

# Calculando estatisticas:
correlacao_bruta = stat.correlation(retornos_analisar, retornos_previstos)
mean_analise, median_analise, std_analise, q1_analise, q3_analise = stat.statistics(retornos_analisar)
mean_previstos, median_previstos, std_previstos, q1_previstos, q3_previstos = stat.statistics(retornos_previstos)

print('### ESTATISTICAS ####', f'Tamanho população: {retornos_previstos.numel()}')
print(f'Correlação Amostras: {round(correlacao_bruta.item(), 4)}','\n')
print(f'Media Analise: {round(mean_analise.item(), 4)}')
print(f'Mediana Analise: {round(median_analise.item(), 4)}')
print(f'Desvio Padrao Analise: {round(std_analise.item(), 4)}')
print(f'Quartil 1 Analise: {round(q1_analise.item(), 4)}')
print(f'Quartil 4 Analise: {round(q3_analise.item(), 4)}', '\n')
print(f'Media Previsão: {round(mean_previstos.item(), 4)}')
print(f'Mediana Previsão: {round(median_previstos.item(), 4)}')
print(f'Desvio Padrao Previsão: {round(std_previstos.item(), 4)}')
print(f'Quartil 1 Previsão: {round(q1_previstos.item(), 4)}')
print(f'Quartil 4 Previsão: {round(q3_previstos.item(), 4)}')
print('### ----------- ###\n')

# Amostras
mask = retornos_analisar < 0
tensorA = retornos_analisar[mask]
tensorB = retornos_previstos[mask]

# Calculando estatisticas:
correlacao_bruta = stat.correlation(tensorA, tensorB)
mean_analise, median_analise, std_analise, q1_analise, q3_analise = stat.statistics(tensorA)
mean_previstos, median_previstos, std_previstos, q1_previstos, q3_previstos = stat.statistics(tensorB)

print('### ESTATISTICAS - AMOSTRA 1 ####', f'Tamanho amostra: {tensorA.numel()}')
print(f'Correlação Amostras: {round(correlacao_bruta.item(), 4)}','\n')
print(f'Media Analise: {round(mean_analise.item(), 4)}')
print(f'Mediana Analise: {round(median_analise.item(), 4)}')
print(f'Desvio Padrao Analise: {round(std_analise.item(), 4)}')
print(f'Quartil 1 Analise: {round(q1_analise.item(), 4)}')
print(f'Quartil 4 Analise: {round(q3_analise.item(), 4)}', '\n')
print(f'Media Previsão: {round(mean_previstos.item(), 4)}')
print(f'Mediana Previsão: {round(median_previstos.item(), 4)}')
print(f'Desvio Padrao Previsão: {round(std_previstos.item(), 4)}')
print(f'Quartil 1 Previsão: {round(q1_previstos.item(), 4)}')
print(f'Quartil 4 Previsão: {round(q3_previstos.item(), 4)}')
print('### ----------- ###\n')

 
print(f'Teste de hipótese da Correlação {stat.hypothesis_test_correlation(retornos_analisar, retornos_previstos)}')


pl = [100]
x=0
for i in range(retornos_previstos.numel()):
    if retornos_analisar[i].item() > 0:
        pl.append( pl[x] * ( 1 + retornos_previstos[i].item() * -1) )        
        x+=1
    else:
        pl.append( pl[x] * ( 1 + retornos_previstos[i].item() ) )
        x+=1

plt.plot(pl, color='blue')
plt.title('Scatter plot entre tensor1 e tensor2')
plt.xlabel('tensor1')
plt.ylabel('tensor2')
plt.show()
