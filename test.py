
import json
import os
import random
import sys

from web3 import Web3
sys.path.append(os.path.abspath('../modules/sushi/result'))


root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'))
sys.path.append(root_path)

config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "config.json")
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

# Импортируем функцию test из inch.py
from modules.inch.result.swap_inch import inch_swap  # NOQA: E402


SWAP_VALUE = config['SWAP_VALUE']
AVAX_RPC_URL = config['AVAX_RPC_URL']
POLYGON_RPC_URL = config['POLYGON_RPC_URL']
FANTOM_RPC_URL = config['FANTOM_RPC_URL']

if __name__ == '__main__':
    with open("private.txt", "r") as f:
        keys_list = [row.strip() for row in f]
    if len(keys_list) == 0:
        print(f'[GLOBAL] private.txt is empty')
        sys.exit(1)
    random.shuffle(keys_list)
    for private_key in keys_list:
        avax_w3 = Web3(Web3.HTTPProvider(AVAX_RPC_URL))
        swap_min_value = SWAP_VALUE * 0.8
        swap_max_value = SWAP_VALUE * 0.99
        random_amount = random.uniform(swap_min_value, swap_max_value)
        # amount = random_amount
        amount = 82421503663470010

        in_token = 'DAI'
        out_token = 'USDC'

        result = inch_swap(avax_w3, private_key, 'AVALANCHE',
                           in_token, out_token, amount, 'UINT')
        print(f'result: {result}')
