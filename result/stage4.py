
import json
import os
import random
import sys
from time import sleep

from web3 import Web3

root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'))
sys.path.append(root_path)

from modules.aave.result.main import repay, withdraw  # NOQA: E402
from modules.stargate.result.stargate_ftm_avax import swap_usdc_avax_to_fantom  # NOQA: E402

config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../config.json')
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

AVAX_RPC_URL = config['AVAX_RPC_URL']

USDC_ADDRESS = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
usdc_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'abis/erc20_abi.json')
usdc_abi = json.load(open(usdc_abi_path))

BTCB_AVAX_ADDRESS = "0x152b9d0FdC40C096757F570A51E494bd4b943E50"
btcb_avax_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'abis/btcb_abi.json')
btcb_avax_abi = json.load(open(btcb_avax_abi_path))


def stage4(private_key):
    avax_w3 = Web3(Web3.HTTPProvider(AVAX_RPC_URL))
    account = avax_w3.eth.account.from_key(private_key)
    btcb_avax_contract = avax_w3.eth.contract(
        address=BTCB_AVAX_ADDRESS, abi=btcb_avax_abi)
    btcb_amount_avax = 0
    print(f'[STAGE 4] Waiting BTCB in Avalanche...')
    while (btcb_amount_avax < 100):
        try:
            btcb_amount_avax = btcb_avax_contract.functions.balanceOf(
                account.address).call()
        except:
            pass
        sleep(60)
    print(f'[STAGE 4] Start repay BTCB to AAVE')
    while True:
        result = repay(private_key)
        if (result > 0):
            break
        print(f'[STAGE 4] Try to repeat repay...')
        sleep(30)
    print(f'[STAGE 4] Start withdraw USDC from AAVE')
    retry = 0
    while True:
        result = withdraw(private_key, retry)
        if (result > 0):
            break
        retry += 1
        print(f'[STAGE 4] Withdraw retry')
        sleep(30)
        if (retry > 3):
            print(f'[STAGE 4] WITHDRAW FAILED. EXIT')
            exit(-1)

    usdc_avax_contract = avax_w3.eth.contract(
        address=USDC_ADDRESS, abi=usdc_abi)
    amount = usdc_avax_contract.functions.balanceOf(account.address).call()
    print(f'[STAGE 4] Bridge USDC to Fantom')
    while True:
        result = swap_usdc_avax_to_fantom(amount, private_key)
        if (result > 0):
            break
        print(f'[STAGE 4] Try to repeat bridge...')
        sleep(30)
    print(f'[STAGE 4] Bridge complete')


if __name__ == '__main__':
    print('[STAGE 4] Run global main script!')
