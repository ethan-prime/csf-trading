import numpy as np

def remove_outliers_iqr(prices):
    Q1 = np.percentile(prices, 25)
    Q3 = np.percentile(prices, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return [p for p in prices if lower_bound <= p <= upper_bound]