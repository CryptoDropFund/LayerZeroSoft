
from modules.stargate.result.stargate_polygon_avax import swap_usdc_polygon_to_avax
import json
import os
import sys
from time import sleep
from web3 import Web3

root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'))
sys.path.append(root_path)

from result.swaps import swaps  # NOQA: E402

config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../config.json')
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

POLYGON_RPC_URL = config['POLYGON_RPC_URL']
AVAX_RPC_URL = config['AVAX_RPC_URL']
MIN_USDC_START = config['MIN_USDC_START']

usdc_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'abis/erc20_abi.json')
usdc_abi = json.load(open(usdc_abi_path))


def polygon_actions(private_key):
    polygon_w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
    account = polygon_w3.eth.account.from_key(private_key)

    usdc_polygon_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
    usdc_polygon_contract = polygon_w3.eth.contract(
        address=usdc_polygon_address, abi=usdc_abi)

    amount_float = 0
    print(f'[STAGE 6] Waiting {MIN_USDC_START} USDC for continue...')
    # Ждем прихода USDC через мост
    while (amount_float < MIN_USDC_START):
        amount = usdc_polygon_contract.functions.balanceOf(
            account.address).call()
        amount_float = int(amount) / int("".join((["1"] + ["0"] * 6)))
        sleep(60)
    print(f'[STAGE 6] USDC {amount_float}$ got.')
    print(f'[STAGE 6] Start swaps in polygon')
    swaps(private_key, 'MATIC_USDC')
    print(f'[STAGE 6] Complete swaps in polygon')
    print(f'[STAGE 6] Bridge USDC to Avalanche')
    amount = usdc_polygon_contract.functions.balanceOf(account.address).call()
    while True:
        result = swap_usdc_polygon_to_avax(amount, private_key)
        if (result > 0):
            break
        print(f'[STAGE 6] Try to repeat bridge...')
        sleep(30)
    print(f'[STAGE 6] Bridge complete. Finish')


def waiting_usdc_avax(private_key):
    avax_w3 = Web3(Web3.HTTPProvider(AVAX_RPC_URL))
    account = avax_w3.eth.account.from_key(private_key)

    usdc_avax_address = '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E'
    usdc_avax_contract = avax_w3.eth.contract(
        address=usdc_avax_address, abi=usdc_abi)

    amount_float = 0
    print(f'[STAGE 6] Waiting {MIN_USDC_START} USDC for continue...')
    # Ждем прихода USDC через мост
    while (amount_float < MIN_USDC_START):
        try:
            amount = usdc_avax_contract.functions.balanceOf(
                account.address).call()
            amount_float = int(amount) / int("".join((["1"] + ["0"] * 6)))
        except:
            pass
        sleep(30)
    print(f'[STAGE 6] USDC {amount_float}$ got. Finish.')


def stage6(private_key, START_FROM):
    match START_FROM:
        case 'AVAX':
            polygon_actions(private_key)
            return
        case 'MATIC':
            waiting_usdc_avax(private_key)
            return
        case _:
            print(f'[STAGE 6] Not found start mode')
            return


if __name__ == '__main__':
    print('[STAGE 6] Run global main script!')
