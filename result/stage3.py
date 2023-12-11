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
from modules.btcb.result.main import send_btcb_to_avax  # NOQA: E402

config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../config.json')
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

POLYGON_RPC_URL = config['POLYGON_RPC_URL']
BMATIC_WAIT_MIN = config['BMATIC_WAIT_MIN']
BMATIC_WAIT_MAX = config['BMATIC_WAIT_MAX']

BTCB_POLYGON_ADDRESS = "0x2297aEbD383787A160DD0d9F71508148769342E3"
btcb_polygon_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'abis/btcb_abi.json')
btcb_polygon_abi = json.load(open(btcb_polygon_abi_path))


def stage3(private_key):
    polygon_w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
    account = polygon_w3.eth.account.from_key(private_key)
    btcb_polygon_contract = polygon_w3.eth.contract(
        address=BTCB_POLYGON_ADDRESS, abi=btcb_polygon_abi)
    btcb_amount_polygon = 0

    print(f'[STAGE 3] Waiting BTCB in Polygon')
    while (btcb_amount_polygon < 1):
        try:
            btcb_amount_polygon = btcb_polygon_contract.functions.balanceOf(
                account.address).call()
        except:
            pass
        sleep(30)

    print(f'[STAGE 3] Start swaps in Polygon')
    swaps(private_key, 'MATIC')
    print(f'[STAGE 3] Complete swaps in Polygon')
    rand_wait_before_bridge = random.randint(BMATIC_WAIT_MIN, BMATIC_WAIT_MAX)
    print(f'[STAGE 3] Sleep for {rand_wait_before_bridge}s before bridge...')
    sleep(rand_wait_before_bridge)
    print(f'[STAGE 3] Bridging to Avalanche...')
    btcb_amount_polygon = btcb_polygon_contract.functions.balanceOf(
        account.address).call()
    while True:
        result = send_btcb_to_avax(private_key, btcb_amount_polygon)
        if (result > 0):
            break
        print(f'[STAGE 3] Try to repeat bridge...')
        sleep(30)
    print(f'[STAGE 3] Complete transfer BTCB to Avalanche')


if __name__ == '__main__':
    print('[STAGE 3] Run global main script!')
