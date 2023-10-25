



def calculate_return(start_price, end_price):
    return end_price / start_price - 1

def simple_update_capital(cash, direction):
    if direction == "buy" and cash > 0.10:
        cash -= 0.10
        return 0.10, cash
    elif direction == "sell" and cash < 2.00:
        cash += 0.10
        return -0.10, cash
    return 0, cash