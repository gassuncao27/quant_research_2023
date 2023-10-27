# Indicators - strategy evaluation

def total_return(equity):
    return round((equity[-1] / equity[0]) - 1, 2)

def annualized_return(prices, periods_per_year):
    total_periods = len(prices) - 1
    overall_return = total_return(prices)
    return (1 + overall_return) ** (periods_per_year / total_periods) - 1

def annualized_volatility(prices, periods_per_year):
    returns = [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]
    return (sum([(x - sum(returns) / len(returns)) ** 2 for x in returns]) / len(returns)) ** 0.5 * (periods_per_year ** 0.5)

def sharpe_ratio(prices, periods_per_year, risk_free_rate=0.0):
    ret_ann = annualized_return(prices, periods_per_year)
    vol_ann = annualized_volatility(prices, periods_per_year)
    return (ret_ann - risk_free_rate) / vol_ann

def sortino_ratio(prices, periods_per_year, risk_free_rate=0.0):
    ret_ann = annualized_return(prices, periods_per_year)
    returns = [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]
    downside_volatility = (sum([(min(0, x - sum(returns) / len(returns))) ** 2 for x in returns]) / len(returns)) ** 0.5 * (periods_per_year ** 0.5)
    return (ret_ann - risk_free_rate) / downside_volatility

def profit_factor(equity):
    trades = []
    for i in range(1, len(equity)):
        trades.append(equity[i]/ equity[i-1]-1)
    gross_profit = sum([trade for trade in trades if trade > 0])
    gross_loss = abs(sum([trade for trade in trades if trade < 0]))
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0
    return round(gross_profit / gross_loss, 2)

def percentage_positive_trades(equity):
    trades = []
    for i in range(1, len(equity)):
        trades.append(equity[i]/ equity[i-1]-1)
    positive_trades = sum(1 for trade in trades if trade > 0)
    return round(positive_trades / len(trades) * 100, 2)

def max_drawdown(equity):
    peak = equity[0]
    max_dd = 0.0
    for price in equity:
        if price > peak:
            peak = price
        dd = (peak - price) / peak
        if dd > max_dd:
            max_dd = dd
    return round(max_dd, 2)
