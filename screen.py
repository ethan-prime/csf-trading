from screener import *
from screener_config import *
from strategy.ArbitrageStrategy import *
from tools import parse_args
import sys

if __name__ == "__main__":
    input_file = ""
    output_file = ""
    start_at = 0
    if len(sys.argv) < 2:
        raise Exception("usage: py screen.py input=<INPUT_FILE> [output=<OUTPUT_FILE>] [start=<INDEX_START>]")
    args_concat = " ".join(sys.argv[1:])
    args = parse_args(args_concat)
    if "input" not in args:
        raise Exception("usage: py screen.py input=<INPUT_FILE> [output=<OUTPUT_FILE>] [start=<INDEX_START>]")
    input_file = args["input"]
    if "output" in args:
        output_file = args["output"]
    else:
        output_file = f"output/{input_file.split('/')[-1]}"
    if "start" in args:
        start_at = int(args["start"])
        
    s = Screener(input_file, ArbitrageStrategy, min_price=MIN_PRICE, max_price=MAX_PRICE, threshold=EV_THRESHOLD,  
                 delta=DELTA, epsilon=EPSILON, delay=DELAY, min_similar_sales=MIN_SIMILAR_SALES, min_vol=MIN_VOL, heuristic=HEURISTIC, 
                 write_to_output=output_file, send_alert=SEND_ALERT, autobid_ev_threshold=AUTOBID_EV_THRESHOLD, sticker_price_threshold=STICKER_PRICE_THRESHOLD)
    s.execute(start_at=start_at)