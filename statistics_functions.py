import torch
import numpy

from scipy import stats

def correlation(tensor1, tensor2):
    mean1 = torch.mean(tensor1)
    mean2 = torch.mean(tensor2)
    std1 = torch.std(tensor1)
    std2 = torch.std(tensor2)
    covariance = torch.mean((tensor1 - mean1) * (tensor2 - mean2))
    return covariance / (std1 * std2)

def statistics(tensor):
    mean = torch.mean(tensor)
    median = torch.median(tensor)
    std = torch.std(tensor)
    q1 = torch.quantile(tensor, 0.25) if hasattr(torch, 'quantile') else None
    q3 = torch.quantile(tensor, 0.75) if hasattr(torch, 'quantile') else None
    
    return mean, median, std, q1, q3

def hypothesis_test_mean(sample_tensor, population_tensor):
    sample_data = sample_tensor.numpy()
    population_data = population_tensor.numpy()
    t_stat, p_value_mean = stats.ttest_ind(sample_data, population_data)
    return t_stat, p_value_mean

def hypothesis_test_correlation(tensor1, tensor2):
    data1 = tensor1.numpy()
    data2 = tensor2.numpy()
    corr_coeff, p_value = stats.pearsonr(data1, data2)
    return corr_coeff, p_value   

def print_statistics(tensor1_analise, tensor2_prev):

    correlation_calc = correlation(tensor1_analise, tensor2_prev)
    mean_calc, median_calc, std_calc, q1_calc, q3_calc = statistics(tensor1_analise)
    mean_calc2, median_calc2, std_calc2, q1_calc2, q3_calc2 = statistics(tensor2_prev)    
    print('### ESTATISTICAS ####', f'Tamanho tensor: {tensor.numel()}')
    print(f'Correlação Amostras: {round(correlation_calc.item(), 4)}','\n')
    print(f'Media Analise: {round(mean_calc.item(), 4)}')
    print(f'Mediana Analise: {round(median_calc.item(), 4)}')
    print(f'Desvio Padrao Analise: {round(std_calc.item(), 4)}')
    print(f'Quartil 1 Analise: {round(q1_calc.item(), 4)}')
    print(f'Quartil 4 Analise: {round(q3_calc.item(), 4)}', '\n')
    print(f'Media Previsão: {round(mean_calc2.item(), 4)}')
    print(f'Mediana Previsão: {round(median_calc2.item(), 4)}')
    print(f'Desvio Padrao Previsão: {round(std_calc2.item(), 4)}')
    print(f'Quartil 1 Previsão: {round(q1_calc2.item(), 4)}')
    print(f'Quartil 4 Previsão: {round(q3_calc2.item(), 4)}')
    print('### ----------- ###\n')    