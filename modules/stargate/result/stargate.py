import os
import time
from stargate_ftm_avax import swap_usdc_avax_to_fantom, swap_usdc_fantom_to_avax
from stargate_polygon_avax import swap_usdc_polygon_to_avax, swap_usdc_avax_to_polygon
import json
from web3 import Web3

config_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../config.json")
with open(config_file_path, "r") as jsonfile:
    config = json.load(jsonfile)
    print("Read successful")
    jsonfile.close()

# enter slippage as shown => 1 = 0.1%, 5 = 0.5%, 10 = 1%
SLIPPAGE = config["SLIPPAGE"]
AMOUNT_TO_SWAP = config["AMOUNT_TO_SWAP"]
SLEEPING_BETWEEN_TRANSACTIONS = config["SLEEPING_BETWEEN_TRANSACTIONS"]
MODE = config["MODE"]


def main():
    keys = open('private.txt', 'r').read().splitlines()
    for private_key in keys:
        try:
            slippage = SLIPPAGE
            # amount_to_swap = AMOUNT_TO_SWAP * (10 ** 6)
            amount_to_swap = int(Web3.to_wei(AMOUNT_TO_SWAP, 'mwei'))
            min_amount = amount_to_swap - (amount_to_swap * slippage) // 1000
            match MODE:
                case "AVAX_FANTOM":
                    print("Bridging USDC from AVAX to Fantom...")
                    avax_to_ftm_txn_hash = swap_usdc_avax_to_fantom(
                        amount_to_swap, min_amount, private_key)
                    print(
                        f'Transaction: https://snowtrace.io/tx/{avax_to_ftm_txn_hash.hex()}')
                case "FANTOM_AVAX":
                    print('Bridging USDC from Fantom to AVAX...')
                    ftm_to_avax_txn_hash = swap_usdc_fantom_to_avax(
                        amount_to_swap, min_amount, private_key)
                    print(
                        f'Transaction: https://ftmscan.com/tx/{ftm_to_avax_txn_hash.hex()}')
                case "POLYGON_AVAX":
                    print('Bridging USDC from Polygon to AVAX...')
                    polygon_to_avax_txn_hash = swap_usdc_polygon_to_avax(
                        amount_to_swap, min_amount, private_key)
                    print(
                        f'Transaction: https://polygonscan.com/tx/{polygon_to_avax_txn_hash.hex()}')
                case "AVAX_POLYGON":
                    print('Bridging USDC from AVAX to Polygon...')
                    avax_to_polygon_txn_hash = swap_usdc_avax_to_polygon(
                        amount_to_swap, min_amount, private_key)
                    print(
                        f'Transaction: https://snowtrace.io/tx/{avax_to_polygon_txn_hash.hex()}')
            time.sleep(SLEEPING_BETWEEN_TRANSACTIONS)
        except Exception as err:
            print(f'error: {err}')


if __name__ == '__main__':
    main()
