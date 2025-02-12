from screener import *
from screener_config import *
from strategy.ArbitrageStrategy import *
import sys

if __name__ == "__main__":
    input_file = ""
    output_file = ""
    if len(sys.argv) < 2:
        raise Exception("usage: py screen.py INPUT_FILE [OUTPUT_FILE]")
    if len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = f"output/{input_file.split("/")[-1]}"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    s = Screener(input_file, ArbitrageStrategy, min_price=MIN_PRICE, max_price=MAX_PRICE, threshold=EV_THRESHOLD, delta=DELTA, epsilon=EPSILON, delay=DELAY, min_similar_sales=MIN_SIMILAR_SALES, min_vol=MIN_VOL, heuristic=HEURISTIC, write_to_output=output_file, send_alert=SEND_ALERT, autobid_ev_threshold=AUTOBID_EV_THRESHOLD)
    s.execute()