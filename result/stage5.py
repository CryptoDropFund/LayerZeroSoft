
import json
import os
import random
import sys
from time import sleep

from web3 import Web3

root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'))
sys.path.append(root_path)

from result.swaps import swaps  # NOQA: E402
from modules.stargate.result.stargate_ftm_avax import swap_usdc_fantom_to_avax  # NOQA: E402
from modules.stargate.result.stargate_ftm_polygon import swap_usdc_fantom_to_polygon  # NOQA: E402

config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../config.json')
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

FANTOM_RPC_URL = config['FANTOM_RPC_URL']
MIN_USDC_START = config['MIN_USDC_START']
FTM_WAIT_MIN = config['FTM_WAIT_MIN']
FTM_WAIT_MAX = config['FTM_WAIT_MAX']

usdc_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'abis/erc20_abi.json')
usdc_abi = json.load(open(usdc_abi_path))


def stage5(private_key, START_FROM):
    fantom_w3 = Web3(Web3.HTTPProvider(FANTOM_RPC_URL))
    account = fantom_w3.eth.account.from_key(private_key)

    usdc_fantom_address = '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75'
    usdc_fantom_contract = fantom_w3.eth.contract(
        address=usdc_fantom_address, abi=usdc_abi)
    amount_float = 0
    print(f'[STAGE 5] Waiting minimum {MIN_USDC_START} USDC for continue...')
    # Ждем прихода USDC через мост
    while (amount_float < MIN_USDC_START):
        try:
            amount = usdc_fantom_contract.functions.balanceOf(
                account.address).call()
            amount_float = int(amount) / int("".join((["1"] + ["0"] * 6)))
        except:
            pass
        sleep(30)
    print(f'[STAGE 5] USDC {amount_float}$ got. Start swaps')
    swaps(private_key, 'FTM_USDC')
    print(f'[STAGE 5] Complete swaps in Fantom')
    rand_wait_before_bridge = random.randint(FTM_WAIT_MIN, FTM_WAIT_MAX)
    print(f'[STAGE 5] Sleep for {rand_wait_before_bridge}s before bridge...')
    sleep(rand_wait_before_bridge)
    amount = usdc_fantom_contract.functions.balanceOf(
        account.address).call()
    match START_FROM:
        case 'AVAX':
            print(f'[STAGE 5] Bridge USDC to Polygon')
            while True:
                result = swap_usdc_fantom_to_polygon(amount, private_key)
                if (result > 0):
                    break
                print(f'[STAGE 5] Try to repeat bridge')
                sleep(30)
        case 'MATIC':
            print(f'[STAGE 5] Bridge USDC to Avalanche')
            while True:
                result = swap_usdc_fantom_to_avax(amount, private_key)
                if (result > 0):
                    break
                print(f'[STAGE 5] Try to repeat bridge')
                sleep(30)
        case _:
            print(f'[STAGE 5] Not found start mode')
            return

    print(f'[STAGE 5] Bridge complete')


if __name__ == '__main__':
    print('[STAGE 5] Run global main script!')
