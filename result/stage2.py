
import json
import os
import random
import sys
from time import sleep

from web3 import Web3

root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'))
sys.path.append(root_path)

from modules.aave.result.main import deposit, borrow  # NOQA: E402
from modules.btcb.result.main import send_btcb_to_polygon  # NOQA: E402

config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../config.json')
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

AVAX_RPC_URL = config['AVAX_RPC_URL']
MIN_LOAN_USDC = config['MIN_LOAN_USDC']
MAX_LOAN_USDC = config['MAX_LOAN_USDC']
MIN_USDC_START = config['MIN_USDC_START']

usdc_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'abis/erc20_abi.json')
usdc_abi = json.load(open(usdc_abi_path))
btcb_avax_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'abis/btcb_abi.json')
btcb_avax_abi = json.load(open(btcb_avax_abi_path))


def stage2(private_key):
    avax_w3 = Web3(Web3.HTTPProvider(AVAX_RPC_URL))
    account = avax_w3.eth.account.from_key(private_key)

    # usdc_avax_address = avax_w3.to_checksum_address(
    #     '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E')
    usdc_avax_address = '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E'
    usdc_avax_contract = avax_w3.eth.contract(
        address=usdc_avax_address, abi=usdc_abi)

    BTCB_AVAX_ADDRESS = "0x152b9d0FdC40C096757F570A51E494bd4b943E50"
    btcb_avax_contract = avax_w3.eth.contract(
        address=BTCB_AVAX_ADDRESS, abi=btcb_avax_abi)

    amount_float = 0
    print(f'[STAGE 2] Waiting minimum {MIN_USDC_START} USDC for continue...')
    # Ждем прихода USDC через мост
    while (amount_float < MIN_USDC_START):
        try:
            amount = usdc_avax_contract.functions.balanceOf(
                account.address).call()
            amount_float = int(amount) / int("".join((["1"] + ["0"] * 6)))
        except:
            pass
        sleep(30)
    print(f'[STAGE 2] USDC {amount_float}$ got. Start Deposit & borrow btcb')
    min_usdc_deposit = MIN_LOAN_USDC * amount_float
    max_usdc_deposit = MAX_LOAN_USDC * amount_float
    usdc_for_deposit = random.uniform(min_usdc_deposit, max_usdc_deposit)
    while True:
        result = deposit(private_key, usdc_for_deposit)
        if (result > 0):
            break
        print(f'[STAGE 2] Try to repeat deposit...')
        sleep(30)
    while True:
        result = borrow(private_key)
        if (result > 0):
            break
        print(f'[STAGE 2] Try to repeat borrow...')
        sleep(30)

    btcb_amount_avax = btcb_avax_contract.functions.balanceOf(
        account.address).call()
    print(f'[STAGE 2] Start bridging to Polygon...')
    while True:
        result = send_btcb_to_polygon(private_key, btcb_amount_avax)
        if (result > 0):
            break
        print(f'[STAGE 2] Repeat after 30 sec...')
        sleep(30)


if __name__ == '__main__':
    print('[STAGE 2] Run global main script!')
