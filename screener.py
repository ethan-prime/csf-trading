import time
from strategy.ArbitrageStrategy import *

class Screener:
    def __init__(self, scan_list: str, strategy, **strategy_kwargs):
        self.scan_list = scan_list
        self.strategy = strategy
        self.strategy_kwargs = strategy_kwargs

    def read_list(self):
        with open(self.scan_list, 'r', encoding='utf-8') as f:
            self.scan_list = f.readlines()
            self.scan_list = list(map(lambda x: x.replace('\n',''), self.scan_list))

    def execute(self, n_iters: int = 1, delay: int = 0):
        self.read_list()
        
        for _ in range(n_iters):
            print("Starting ArbitrageStrategy...")
            self.strategy(self.scan_list, **self.strategy_kwargs)
            time.sleep(delay)