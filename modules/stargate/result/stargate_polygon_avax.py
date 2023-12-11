import os
from web3 import Web3
import json
import time

with open('config.json', "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

# Operation Type
TYPE_SWAP_REMOTE = 1

# Chain ID
POLYGON_ID = 109
AVALANCHE_ID = 106

# Pool ID
USDC_POLYGON_POOL_ID = 1
USDC_AVALANCHE_POOL_ID = 1

# Options
EXTRA_GAS_PARAMS = [0, 0, "0x0000000000000000000000000000000000000001"]
PAYLOAD_VALUE = "0x"

# RPCs
POLYGON_RPC_URL = config['POLYGON_RPC_URL']
AVAX_RPC_URL = config['AVAX_RPC_URL']

# Slippage
SLIPPAGE = config['SLIPPAGE_STARGATE']

# Gas
GAS_LIMIT = config['STARGATE_GASLIMIT']

MAX_PRIORITY_FEE_AVAX = config['MAX_PRIORITY_FEE_AVAX']
MAX_FEE_AVAX = config['MAX_FEE_AVAX']

MAX_PRIORITY_FEE_POLYGON = config['MAX_PRIORITY_FEE_POLYGON']
MAX_FEE_POLYGON = config['MAX_FEE_POLYGON']


stargate_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/router_abi.json")
stargate_abi = json.load(open(stargate_abi_file_path))
usdc_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/usdc_abi.json")
usdc_abi = json.load(open(usdc_abi_file_path))

polygon_w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
stargate_polygon_address = polygon_w3.to_checksum_address(
    '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')
stargate_polygon_contract = polygon_w3.eth.contract(
    address=stargate_polygon_address, abi=stargate_abi)
usdc_polygon_address = polygon_w3.to_checksum_address(
    '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')
usdc_polygon_contract = polygon_w3.eth.contract(
    address=usdc_polygon_address, abi=usdc_abi)


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

# Polygon -> Avalanche USDC Bridge


def swap_usdc_polygon_to_avax(amount, PRIVATE_KEY):
    account = polygon_w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    # gas_price = polygon_w3.eth.gas_price
    min_amount = amount - (amount * SLIPPAGE) // 1000
    fees = stargate_polygon_contract.functions.quoteLayerZeroFee(AVALANCHE_ID,
                                                                 TYPE_SWAP_REMOTE,
                                                                 "0x0000000000000000000000000000000000001010",
                                                                 PAYLOAD_VALUE,
                                                                 EXTRA_GAS_PARAMS
                                                                 ).call()
    fee = fees[0]

    nonce = polygon_w3.eth.get_transaction_count(address)
    allowance = usdc_polygon_contract.functions.allowance(
        address, stargate_polygon_address).call()
    if allowance < amount:
        try:
            approve_txn = usdc_polygon_contract.functions.approve(stargate_polygon_address, amount).build_transaction({
                'from': address,
                'gas': GAS_LIMIT,
                # 'gasPrice': gas_price,
                'nonce': nonce,
                'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_POLYGON, 'gwei'),
                'maxFeePerGas': Web3.to_wei(MAX_FEE_POLYGON, 'gwei')
            })
            # del approve_txn['gasPrice']
            signed_approve_txn = polygon_w3.eth.account.sign_transaction(
                approve_txn, PRIVATE_KEY)
            approve_txn_hash = polygon_w3.eth.send_raw_transaction(
                signed_approve_txn.rawTransaction)
            receipt = polygon_w3.eth.wait_for_transaction_receipt(
                approve_txn_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"[STARGATE] Can't approve allowance for {amount}")
                return -1
        except:
            print(f'[STARGATE] Crytical error. Operation failed.')
            return -1

        print(
            f"[STARGATE] POLYGON | USDС APPROVED https://polygonscan.com/tx/{approve_txn_hash.hex()}")
        nonce += 1

    try:
        # Stargate Swap
        chainId = AVALANCHE_ID
        source_pool_id = USDC_POLYGON_POOL_ID
        dest_pool_id = USDC_AVALANCHE_POOL_ID
        refund_address = account.address
        amountIn = amount
        amountOutMin = min_amount
        lzTxObj = EXTRA_GAS_PARAMS
        to = account.address
        data = PAYLOAD_VALUE

        swap_txn = stargate_polygon_contract.functions.swap(
            chainId, source_pool_id, dest_pool_id, refund_address, amountIn, amountOutMin, lzTxObj, to, data
        ).build_transaction({
            'from': address,
            'value': fee,
            'gas': GAS_LIMIT,
            # 'gasPrice': polygon_w3.eth.gas_price,
            'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_POLYGON, 'gwei'),
            'maxFeePerGas': Web3.to_wei(MAX_FEE_POLYGON, 'gwei'),
            'nonce': nonce,
        })
        # del swap_txn['gasPrice']
        signed_swap_txn = polygon_w3.eth.account.sign_transaction(
            swap_txn, PRIVATE_KEY)
        swap_txn_hash = polygon_w3.eth.send_raw_transaction(
            signed_swap_txn.rawTransaction)
        receipt = polygon_w3.eth.wait_for_transaction_receipt(
            swap_txn_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[STARGATE] Can't send transaction Polygon -> AVAX")
            return -1
        print(
            f'[STARGATE] Success transfer USDC for {decimal_to_int(amount, 6)} from Polygon to Avalanche')
        return 1
    except:
        print(f'[STARGATE] Critical error. Operation failed.')
        return -1


# Avalanche -> Polygon USDC Bridge
def swap_usdc_avax_to_polygon(amount, PRIVATE_KEY):
    account = avax_w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    # gas_price = avax_w3.eth.gas_price
    min_amount = amount - (amount * SLIPPAGE) // 1000
    fees = stargate_avax_contract.functions.quoteLayerZeroFee(POLYGON_ID,
                                                              TYPE_SWAP_REMOTE,
                                                              "0x0000000000000000000000000000000000000001",
                                                              PAYLOAD_VALUE,
                                                              EXTRA_GAS_PARAMS
                                                              ).call()
    fee = fees[0]

    nonce = avax_w3.eth.get_transaction_count(address)
    # Check Allowance
    allowance = usdc_avax_contract.functions.allowance(
        address, stargate_avax_address).call()
    if allowance < amount:
        try:
            approve_txn = usdc_avax_contract.functions.approve(stargate_avax_address, amount).build_transaction({
                'from': address,
                'gas': GAS_LIMIT,
                # 'gasPrice': gas_price,
                'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
                'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
                'nonce': nonce,
            })
            try:
                del approve_txn['gasPrice']
            except:
                pass
            signed_approve_txn = avax_w3.eth.account.sign_transaction(
                approve_txn, PRIVATE_KEY)
            approve_txn_hash = avax_w3.eth.send_raw_transaction(
                signed_approve_txn.rawTransaction)
            receipt = avax_w3.eth.wait_for_transaction_receipt(
                approve_txn_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"[STARGATE] Can't approve allowance for {amount}")
                return -1

            print(
                f"[STARGATE] AVALANCHE | USDC APPROVED | https://snowtrace.io/tx/{approve_txn_hash.hex()} ")
            nonce += 1
        except:
            print(f'[STARGATE] Crytical error. Operation failed')
            return -1

        # time.sleep(50)

    try:
        # Stargate Swap
        chainId = POLYGON_ID
        source_pool_id = USDC_AVALANCHE_POOL_ID
        dest_pool_id = USDC_POLYGON_POOL_ID
        refund_address = account.address
        amountIn = amount
        amountOutMin = min_amount
        lzTxObj = EXTRA_GAS_PARAMS
        to = account.address
        data = PAYLOAD_VALUE

        swap_txn = stargate_avax_contract.functions.swap(
            chainId, source_pool_id, dest_pool_id, refund_address, amountIn, amountOutMin, lzTxObj, to, data
        ).build_transaction({
            'from': address,
            'value': fee,
            'gas': GAS_LIMIT,
            # 'gasPrice': avax_w3.eth.gas_price,
            'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
            'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
            'nonce': nonce,
        })
        try:
            del swap_txn['gasPrice']
        except:
            pass

        signed_swap_txn = avax_w3.eth.account.sign_transaction(
            swap_txn, PRIVATE_KEY)
        swap_txn_hash = avax_w3.eth.send_raw_transaction(
            signed_swap_txn.rawTransaction)
        receipt = avax_w3.eth.wait_for_transaction_receipt(
            swap_txn_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[STARGATE] Can't send transaction AVAX -> Polygon")
            return -1
        print(
            f'[STARGATE] Success transfer USDC for {decimal_to_int(amount, 6)} from Avalanche to Polygon')
        return 1
    except:
        print(f'[STARGATE] Crytical error. Operation failed')
        return -1
