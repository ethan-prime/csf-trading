import math

EV_WEIGHT = 0.5
VOLUME_WEIGHT = 0.2
SIMILAR_SALES_WEIGHT = 0.3

def harvey(ev: float, similar_sales: int, volume: int) -> float:
    log_volume = math.log10(1 + volume)
    sim_sales_per_sale = similar_sales / 20
    return ((EV_WEIGHT * ev) + (VOLUME_WEIGHT * log_volume) + (SIMILAR_SALES_WEIGHT * sim_sales_per_sale))