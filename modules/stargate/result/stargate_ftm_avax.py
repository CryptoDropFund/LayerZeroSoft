import os
from web3 import Web3
import json

from modules.utils import check_enough_gas

with open('config.json', "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

# Operation Type
TYPE_SWAP_REMOTE = 1

# Chain ID
AVALANCHE_ID = 106
FANTOM_ID = 112

# Pool ID
USDC_AVALANCHE_POOL_ID = 1
USDC_FANTOM_POOL_ID = 1

# Options
EXTRA_GAS_PARAMS = [0, 0, '0x0000000000000000000000000000000000000001']
PAYLOAD_VALUE = "0x"

# RPCs
FANTOM_RPC_URL = config['FANTOM_RPC_URL']
AVAX_RPC_URL = config['AVAX_RPC_URL']

# Slippage
SLIPPAGE = config['SLIPPAGE_STARGATE']

# Gas
GAS_LIMIT = config['STARGATE_GASLIMIT']

MAX_PRIORITY_FEE_AVAX = config['MAX_PRIORITY_FEE_AVAX']
MAX_FEE_AVAX = config['MAX_FEE_AVAX']

MAX_PRIORITY_FEE_FTM = config['MAX_PRIORITY_FEE_FTM']
MAX_FEE_FTM = config['MAX_FEE_FTM']

usdc_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/usdc_abi.json")
usdc_abi = json.load(open(usdc_abi_file_path))

fantom_w3 = Web3(Web3.HTTPProvider(FANTOM_RPC_URL))
stargate_fantom_address = fantom_w3.to_checksum_address(
    '0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6')
stargate_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/router_abi.json")
stargate_abi = json.load(open(stargate_abi_path))
stargate_fantom_contract = fantom_w3.eth.contract(
    address=stargate_fantom_address, abi=stargate_abi)

usdc_fantom_address = fantom_w3.to_checksum_address(
    '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75')
usdc_fantom_contract = fantom_w3.eth.contract(
    address=usdc_fantom_address, abi=usdc_abi)


avax_w3 = Web3(Web3.HTTPProvider(AVAX_RPC_URL))
stargate_avax_address = avax_w3.to_checksum_address(
    '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')
stargate_avax_contract = avax_w3.eth.contract(
    address=stargate_avax_address, abi=stargate_abi)

usdc_avax_address = avax_w3.to_checksum_address(
    '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E')
usdc_avax_contract = avax_w3.eth.contract(
    address=usdc_avax_address, abi=usdc_abi)


def decimal_to_int(price, decimal):
    return int(price) / int("".join((["1"] + ["0"] * decimal)))

# Fantom -> Avalanche USDC Bridge


def swap_usdc_fantom_to_avax(amount, PRIVATE_KEY):
    account = fantom_w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    nonce = fantom_w3.eth.get_transaction_count(address)
    # gas_price = fantom_w3.eth.gas_price
    min_amount = amount - (amount * SLIPPAGE) // 1000

    fees = stargate_fantom_contract.functions.quoteLayerZeroFee(AVALANCHE_ID,
                                                                TYPE_SWAP_REMOTE,
                                                                "0x0000000000000000000000000000000000000001",
                                                                PAYLOAD_VALUE,
                                                                EXTRA_GAS_PARAMS
                                                                ).call()
    fee = fees[0]

    # Check allowance
    allowance = usdc_fantom_contract.functions.allowance(
        address, stargate_fantom_address).call()
    if allowance < amount:
        check_enough_gas(fantom_w3, address, GAS_LIMIT)
        # Можно уменьшить allowance, до amount - allowance
        try:
            approve_txn = usdc_fantom_contract.functions.approve(stargate_fantom_address, amount).build_transaction({
                'from': address,
                'gas': GAS_LIMIT,
                # 'gasPrice': gas_price,
                'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_FTM, 'gwei'),
                'maxFeePerGas': Web3.to_wei(MAX_FEE_FTM, 'gwei'),
                'nonce': nonce,
            })
            try:
                del approve_txn['gasPrice']
            except:
                pass
            signed_approve_txn = fantom_w3.eth.account.sign_transaction(
                approve_txn, PRIVATE_KEY)
            approve_txn_hash = fantom_w3.eth.send_raw_transaction(
                signed_approve_txn.rawTransaction)
            receipt = fantom_w3.eth.wait_for_transaction_receipt(
                approve_txn_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"Can't approve allowance for {amount}")
                return -1

            print(
                f"[STARGATE] FANTOM | USDC APPROVED | https://ftmscan.com/tx/{approve_txn_hash.hex()} ")
            nonce += 1
        except:
            print(f'[STARGATE] Exception catched. Retry')
            return -1

    check_enough_gas(fantom_w3, address, GAS_LIMIT)
    # Stargate Swap
    chainId = AVALANCHE_ID
    source_pool_id = USDC_FANTOM_POOL_ID
    dest_pool_id = USDC_AVALANCHE_POOL_ID
    refund_address = account.address
    amountIn = amount
    amountOutMin = min_amount
    lzTxObj = EXTRA_GAS_PARAMS
    to = account.address
    data = PAYLOAD_VALUE
    try:

        swap_txn = stargate_fantom_contract.functions.swap(
            chainId, source_pool_id, dest_pool_id, refund_address, amountIn, amountOutMin, lzTxObj, to, data
        ).build_transaction({
            'from': address,
            'value': fee,
            'gas': GAS_LIMIT,
            # 'gasPrice': fantom_w3.eth.gas_price,
            'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_FTM, 'gwei'),
            'maxFeePerGas': Web3.to_wei(MAX_FEE_FTM, 'gwei'),
            'nonce': fantom_w3.eth.get_transaction_count(address),
        })
        try:
            del swap_txn['gasPrice']
        except:
            pass

        signed_swap_txn = fantom_w3.eth.account.sign_transaction(
            swap_txn, PRIVATE_KEY)
        swap_txn_hash = fantom_w3.eth.send_raw_transaction(
            signed_swap_txn.rawTransaction)
        receipt = fantom_w3.eth.wait_for_transaction_receipt(
            swap_txn_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[STARGATE] Can't send transaction Fantom to Polygon")
            return -1
        print(
            f'[STARGATE] Success transfer USDC for {decimal_to_int(amount, 6)} from Fantom to Avalanche')
        return 1
    except:
        print(f'[STARGATE] Exception catched. Retry')
        return -1

# Avalanche -> Fantom USDC Bridge


def swap_usdc_avax_to_fantom(amount, PRIVATE_KEY):
    account = avax_w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    nonce = avax_w3.eth.get_transaction_count(address)
    # gas_price = avax_w3.eth.gas_price
    min_amount = amount - (amount * SLIPPAGE) // 1000
    fees = stargate_avax_contract.functions.quoteLayerZeroFee(FANTOM_ID,
                                                              TYPE_SWAP_REMOTE,
                                                              "0x0000000000000000000000000000000000000001",
                                                              PAYLOAD_VALUE,
                                                              EXTRA_GAS_PARAMS
                                                              ).call()
    fee = fees[0]

    # Check Allowance
    allowance = usdc_avax_contract.functions.allowance(
        address, stargate_avax_address).call()
    if allowance < amount:
        check_enough_gas(avax_w3, address, GAS_LIMIT)
        try:
            approve_txn = usdc_avax_contract.functions.approve(stargate_avax_address, amount).build_transaction({
                'from': address,
                'gas': GAS_LIMIT,
                # 'gasPrice': gas_price,
                'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
                'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
                'nonce': nonce,
            })
            # del approve_txn['gasPrice']
            signed_approve_txn = avax_w3.eth.account.sign_transaction(
                approve_txn, PRIVATE_KEY)
            approve_txn_hash = avax_w3.eth.send_raw_transaction(
                signed_approve_txn.rawTransaction)

            receipt = avax_w3.eth.wait_for_transaction_receipt(
                approve_txn_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"Can't approve allowance for {amount}")
                return -1
            print(
                f"[STARGATE] AVALANCHE | USDC APPROVED | https://snowtrace.io/tx/{approve_txn_hash.hex()} ")
            nonce += 1
        except:
            print(f'[STARGATE] Exception catched. Retry')
            return -1

    usdc_balance = usdc_avax_contract.functions.balanceOf(address).call()
    check_enough_gas(avax_w3, address, GAS_LIMIT)
    # Stargate Swap
    chainId = FANTOM_ID
    source_pool_id = USDC_AVALANCHE_POOL_ID
    dest_pool_id = USDC_FANTOM_POOL_ID
    refund_address = account.address
    amountIn = amount
    amountOutMin = min_amount
    lzTxObj = EXTRA_GAS_PARAMS
    to = account.address
    data = PAYLOAD_VALUE
    try:
        swap_txn = stargate_avax_contract.functions.swap(
            chainId, source_pool_id, dest_pool_id, refund_address, amountIn, amountOutMin, lzTxObj, to, data
        ).build_transaction({
            'from': address,
            'value': fee,
            'gas': GAS_LIMIT,
            # 'gasPrice': avax_w3.eth.gas_price,
            'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
            'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
            'nonce': avax_w3.eth.get_transaction_count(address),
        })
        # del swap_txn['gasPrice']
        signed_swap_txn = avax_w3.eth.account.sign_transaction(
            swap_txn, PRIVATE_KEY)
        swap_txn_hash = avax_w3.eth.send_raw_transaction(
            signed_swap_txn.rawTransaction)
        receipt = avax_w3.eth.wait_for_transaction_receipt(
            swap_txn_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[STARGATE] Can't send transaction Avalanche to Fantom")
            return -1
        print(
            f'[STARGATE] Success transfer USDC for {decimal_to_int(amount, 6)} from Avalanche to Fantom')
        return 1
    except:
        print(f'[STARGATE] Exception catched. Retry')
        return -1
