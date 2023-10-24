import os
import numpy
import torch
import sys
import matplotlib.pyplot as plt
import statistics_functions as stat
import strategy_evaluation as st_eval

from scipy import stats
from dotenv import load_dotenv
from log_data import LogData 

def equivalence_arrays(array1, array2):
    tensor1 = torch.tensor(array1)
    tensor2 = torch.tensor(array2)
    if tensor1.numel() > tensor2.numel():
        tensor1 = tensor1[:tensor2.numel()]
    elif tensor1.numel() < tensor2.numel(): 
        print('ERROR - verify array composition and size')
        sys.exit()
    return tensor1, tensor2


## upload data
load_dotenv()
ambiente_local = os.getenv('AMBIENTE_WIN')
data_path = 'vale_data.txt'
file_path = ambiente_local + data_path
delimiter, encoding = LogData.guess_file_properties(file_path)
log_data = LogData.read_log_and_fill_class(file_path, encoding, delimiter)
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
retornos_analisar, retornos_previstos = equivalence_arrays(retornos_analisar, retornos_previsto)
# stat.print_statistics(retornos_analisar, retornos_previstos)
# Amostras
print('TESTE COM... \nAnalise com amostra onde retornos semanais < 0\n')
mask = retornos_analisar < 0
tensorA = retornos_analisar[mask]
tensorB = retornos_previstos[mask]
stat.print_statistics(tensorA, tensorB)

correl, p_value = stat.hypothesis_test_correlation(retornos_analisar, retornos_previstos)
print(f'Visualized correlation {round(correl, 4)} and p-value is {round(p_value, 6)}\n')


pl = [100]
x=0
for i in range(retornos_previstos.numel()):
    if retornos_analisar[i].item() > 0:
        pl.append( pl[x] * ( 1 + retornos_previstos[i].item() * -1) )        
        x+=1
    else:
        pl.append( pl[x] * ( 1 + retornos_previstos[i].item() ) )
        x+=1


print('\n STRATEGY EVALUATION \n')
print(f'Total Return {st_eval.total_return(pl)}')
print(f'Profit Factor {st_eval.profit_factor(pl)}')
print(f'Trade Accuracy {st_eval.percentage_positive_trades(pl)}')
print(f'Maximum Drawndown {st_eval.max_drawdown(pl)}')


plt.plot(pl, color='blue')
plt.title('Scatter plot entre tensor1 e tensor2')
plt.xlabel('tensor1')
plt.ylabel('tensor2')
plt.show()
