import json
import os
import random
import sys

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


if __name__ == '__main__':
    with open("private.txt", "r") as f:
        keys_list = [row.strip() for row in f]
    if len(keys_list) == 0:
        print(f'[GLOBAL] private.txt is empty')
        sys.exit(1)
    random.shuffle(keys_list)
    for private_key in keys_list:
        stage0(private_key, START_FROM)  # Start swaps (step 2)
        stage1(private_key, START_FROM)  # Bridge USDC Polygon -> Avax (Step 3)
        stage2(private_key)  # Borrow BTCB -> bridge BTCB to polygon
        # Waiting BTCB in Polygon, MATIC Swaps, bridge BTCB to Avalanche
        stage3(private_key)
        # Waiting BTCB in Polygon, Repay BTCB in AAVE, Withdraw USDC from AAVE, bridge all usdc to ftm
        stage4(private_key)
        # Waiting USDC in Fantom ,swaps, bridge to polygon / avax
        stage5(private_key, START_FROM)
        stage6(private_key, START_FROM)
