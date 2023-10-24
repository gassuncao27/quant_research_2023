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