import sys
import os
import json
import random
import time
from web3 import Web3
root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'))
sys.path.append(root_path)

# Импортируем функцию test из inch.py
from modules.inch.result.swap_inch import inch_swap  # NOQA: E402

config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../config.json")
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

RAND_MIN_SWAPS = config["RAND_MIN_SWAPS"]
RAND_MAX_SWAPS = config["RAND_MAX_SWAPS"]
SWAP_VALUE = config['SWAP_VALUE']
SLEEPING_BETWEEN_TRANSACTIONS = config['SLEEPING_BETWEEN_TRANSACTIONS']

AVAX_RPC_URL = config['AVAX_RPC_URL']
POLYGON_RPC_URL = config['POLYGON_RPC_URL']
FANTOM_RPC_URL = config['FANTOM_RPC_URL']

POLYGON_SWAP_TOKENS = ['USDC', 'FRAX', 'DAI', 'BUSD', 'MATIC']
AVAX_SWAP_TOKENS = ['USDC', 'FRAX', 'DAI', 'TUSD', 'BUSD']
FTM_SWAP_TOKENS = ['USDC', 'FRAX', 'DAI']


def swap_ftm_usdc(private_key):
    fantom_w3 = Web3(Web3.HTTPProvider(FANTOM_RPC_URL))

    swap_min_value = SWAP_VALUE * 0.8
    swap_max_value = SWAP_VALUE * 0.99
    random_amount = random.uniform(swap_min_value, swap_max_value)
    amount = random_amount

    swaps_count = random.randint(RAND_MIN_SWAPS, RAND_MAX_SWAPS)

    in_token = ''
    out_token = ''
    for i in range(1, swaps_count + 1):
        if (i == 1):
            in_token = 'USDC'
        while (out_token == in_token or out_token == ''):
            out_token = random.choice(FTM_SWAP_TOKENS)
        if (i == swaps_count):
            if (in_token == 'USDC'):
                break
            out_token = 'USDC'
        print(f'[SWAPS] swap: {in_token}<->{out_token}')
        MODE = 'TOKEN' if i == 1 else 'UINT'
        while True:
            result = inch_swap(fantom_w3, private_key, 'FANTOM',
                               in_token, out_token, amount, MODE)
            if (result > 0):
                amount = result
                break
            time.sleep(10)
        in_token = out_token

        time.sleep(random.uniform(SLEEPING_BETWEEN_TRANSACTIONS *
                                  0.4, SLEEPING_BETWEEN_TRANSACTIONS * 1.4))
    print(f'[SWAPS] Fantom swaps complete')


def swap_avax_usdc(private_key):
    avax_w3 = Web3(Web3.HTTPProvider(AVAX_RPC_URL))

    swap_min_value = SWAP_VALUE * 0.8
    swap_max_value = SWAP_VALUE * 0.99
    random_amount = random.uniform(swap_min_value, swap_max_value)
    amount = random_amount

    swaps_count = random.randint(RAND_MIN_SWAPS, RAND_MAX_SWAPS)
    in_token = ''
    out_token = ''
    for i in range(1, swaps_count + 1):
        if (i == 1):
            in_token = 'USDC'
        while (out_token == in_token or out_token == ''):
            out_token = random.choice(AVAX_SWAP_TOKENS)
        if (i == swaps_count):
            if (in_token == 'USDC'):
                break
            out_token = 'USDC'
        print(f'[SWAPS] swap: {in_token}<->{out_token}')
        MODE = 'TOKEN' if i == 1 else 'UINT'
        while True:
            result = inch_swap(avax_w3, private_key, 'AVALANCHE',
                               in_token, out_token, amount, MODE)
            if (result > 0):
                amount = result
                break
            time.sleep(10)
        in_token = out_token

        time.sleep(random.uniform(SLEEPING_BETWEEN_TRANSACTIONS *
                                  0.4, SLEEPING_BETWEEN_TRANSACTIONS * 1.4))
    print(f'[SWAPS] Avalanche swaps complete')


def swap_matic_usdc(private_key):
    polygon_w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

    swap_min_value = SWAP_VALUE * 0.8
    swap_max_value = SWAP_VALUE * 0.99
    random_amount = random.uniform(swap_min_value, swap_max_value)
    amount = random_amount

    swaps_count = random.randint(RAND_MIN_SWAPS, RAND_MAX_SWAPS)

    in_token = ''
    out_token = ''
    for i in range(1, swaps_count + 1):
        if (i == 1):
            in_token = 'USDC'
        while (out_token == in_token or out_token == ''):
            out_token = random.choice(POLYGON_SWAP_TOKENS)
        if (i == swaps_count):
            if (in_token == 'USDC'):
                break
            out_token = 'USDC'
        print(f'[SWAPS] swap: {in_token}<->{out_token}')
        MODE = 'TOKEN' if i == 1 else 'UINT'
        while True:
            result = inch_swap(polygon_w3, private_key, 'POLYGON',
                               in_token, out_token, amount, MODE)
            if (result > 0):
                amount = result
                break
            time.sleep(10)
        in_token = out_token

        time.sleep(random.uniform(SLEEPING_BETWEEN_TRANSACTIONS *
                                  0.4, SLEEPING_BETWEEN_TRANSACTIONS * 1.4))

    print(f'[SWAPS] Polygon swaps complete')


def swap_matic(private_key):
    polygon_w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

    swap_min_value = SWAP_VALUE * 0.8
    swap_max_value = SWAP_VALUE * 0.99
    random_amount = random.uniform(swap_min_value, swap_max_value)
    amount = random_amount

    in_token = 'MATIC'
    out_token = ''
    while (out_token == in_token or out_token == ''):
        out_token = random.choice(POLYGON_SWAP_TOKENS)

    print(f'[SWAPS] swap: {in_token}<->{out_token}')
    while True:
        result = inch_swap(polygon_w3, private_key, 'POLYGON',
                           in_token, out_token, amount, 'TOKEN')
        if (result > 0):
            amount = result
            break
        time.sleep(10)
    time.sleep(random.uniform(SLEEPING_BETWEEN_TRANSACTIONS *
                              0.4, SLEEPING_BETWEEN_TRANSACTIONS * 1.4))
    in_token = out_token
    out_token = 'MATIC'
    while True:
        result = inch_swap(polygon_w3, private_key, 'POLYGON',
                           in_token, out_token, amount, 'UINT')
        if (result > 0):
            amount = result
            break
        time.sleep(10)
    print(f'[SWAPS] Polygon swaps complete')


def swaps(private_key: str, MODE: str):
    match MODE:
        case 'AVAX_USDC':
            swap_avax_usdc(private_key)
        case 'MATIC_USDC':
            swap_matic_usdc(private_key)
        case 'FTM_USDC':
            swap_ftm_usdc(private_key)
        case 'MATIC':
            swap_matic(private_key)
        case _:
            print(f'[SWAPS] Not found mode')


if __name__ == '__main__':
    print('[SWAPS] Run global main script!')
