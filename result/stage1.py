import json
import os
import sys
from time import sleep

from web3 import Web3

root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'))
sys.path.append(root_path)

from modules.stargate.result.stargate_polygon_avax import swap_usdc_polygon_to_avax  # NOQA: E402


config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../config.json')
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

SLIPPAGE_STARGATE = config['SLIPPAGE_STARGATE']
POLYGON_RPC_URL = config['POLYGON_RPC_URL']

usdc_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'abis/erc20_abi.json')
usdc_abi = json.load(open(usdc_abi_path))


def bridge_to_avax(private_key):
    polygon_w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
    account = polygon_w3.eth.account.from_key(private_key)

    # Bridge to avax
    usdc_polygon_address = polygon_w3.to_checksum_address(
        '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')
    usdc_polygon_contract = polygon_w3.eth.contract(
        address=usdc_polygon_address, abi=usdc_abi)

    amount = usdc_polygon_contract.functions.balanceOf(account.address).call()
    print(f'[STAGE 1] Start transfer all USDC from Polygon to Avalanche')
    while True:
        result = swap_usdc_polygon_to_avax(amount, private_key)
        if (result > 0):
            break
        print(f'[STAGE 1] Try to repeat bridge...')
        sleep(30)


def stage1(private_key, START_FROM: str):
    match START_FROM:
        case 'AVAX':
            pass
        case 'MATIC':
            bridge_to_avax(private_key)
        case _:
            print(f'[STAGE 1] Not found start mode')
