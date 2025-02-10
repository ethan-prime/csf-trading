import math

EV_WEIGHT = 0.6
VOLUME_WEIGHT = 0.15
SIMILAR_SALES_WEIGHT = 0.25

def harvey(ev: float, similar_sales: int, volume: int) -> float:
    log_volume = math.log10(1 + volume)
    sim_sales_per_sale = similar_sales / 2
    exp_ev = 20**ev - 1
    return ((EV_WEIGHT * exp_ev) + (VOLUME_WEIGHT * log_volume) + (SIMILAR_SALES_WEIGHT * sim_sales_per_sale))

def hamilton(ev: float, similar_sales: int, volume: int) -> float:
    ev_val = min(10*ev, 1)
    return ((0.75 * ev_val) + (0.05 * volume/20) + (0.2 * similar_sales/20))