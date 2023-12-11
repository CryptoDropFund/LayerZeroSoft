import json
import math
import os
import random
import sys
import concurrent.futures

from result.stage0 import stage0
from result.stage1 import stage1
from result.stage2 import stage2
from result.stage3 import stage3
from result.stage4 import stage4
from result.stage5 import stage5
from result.stage6 import stage6
sys.path.append(os.path.abspath('../modules/inch/result'))

with open("./config.json", "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()
START_FROM = config['START_FROM']


def read_lines(filename: str) -> list:
    with open(filename, "r") as f:
        lines = [row.strip() for row in f]
        if (len(lines) == 0):
            print(f'[GLOBAL] private.txt is empty')
            sys.exit(1)
    random.shuffle(lines)
    return lines


def process(key: str) -> None:
    stage0(key, START_FROM)  # Start swaps (step 2)
    stage1(key, START_FROM)  # Bridge USDC Polygon -> Avax (Step 3)
    stage2(key)  # Borrow BTCB -> bridge BTCB to polygon
    # Waiting BTCB in Polygon, MATIC Swaps, bridge BTCB to Avalanche
    stage3(key)
    # Waiting BTCB in Polygon, Repay BTCB in AAVE, Withdraw USDC from AAVE, bridge all usdc to ftm
    stage4(key)
    # Waiting USDC in Fantom ,swaps, bridge to polygon / avax
    stage5(key, START_FROM)
    stage6(key, START_FROM)


if __name__ == '__main__':
    num_processes = os.cpu_count()
    keys_list = read_lines('private.txt')
    num_keys = len(keys_list)

    chunk_size = math.ceil(num_keys / num_processes)
    chunks = [keys_list[i:i + chunk_size]
              for i in range(0, num_keys, chunk_size)]

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = []
        for chunk in chunks:
            for line in chunk:
                futures.append(executor.submit(process, line))
        for future in concurrent.futures.as_completed(futures):
            future.result()
