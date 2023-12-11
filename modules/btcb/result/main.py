import os
import sys
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware
import json
from eth_abi.packed import encode_packed

from modules.utils import check_enough_gas

with open('config.json', "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

GAS_LIMIT = config['BTCB_GASLIMIT']

MAX_PRIORITY_FEE_AVAX = config['MAX_PRIORITY_FEE_AVAX']
MAX_FEE_AVAX = config['MAX_FEE_AVAX']

MAX_PRIORITY_FEE_POLYGON = config['MAX_PRIORITY_FEE_POLYGON']
MAX_FEE_POLYGON = config['MAX_FEE_POLYGON']

POLYGON_ID = 109
AVALANCHE_ID = 106

AVAX_RPC_URL = config['AVAX_RPC_URL']
web3_avax = Web3(Web3.HTTPProvider(AVAX_RPC_URL))
# web3_avax.eth.set_gas_price_strategy(medium_gas_price_strategy)
web3_avax.middleware_onion.inject(geth_poa_middleware, layer=0)

POLYGON_RPC_URL = config['POLYGON_RPC_URL']
web3_polygon = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
web3_polygon.eth.set_gas_price_strategy(medium_gas_price_strategy)
web3_polygon.middleware_onion.inject(geth_poa_middleware, layer=0)

BTCB_AVAX_ADDRESS = "0x152b9d0FdC40C096757F570A51E494bd4b943E50"
btcb_avax_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/btcb_abi.json")
btcb_avax_abi = json.load(open(btcb_avax_abi_path))
btcb_avax_contract = web3_avax.eth.contract(
    address=BTCB_AVAX_ADDRESS, abi=btcb_avax_abi)

BTCB_POLYGON_ADDRESS = "0x2297aEbD383787A160DD0d9F71508148769342E3"
btcb_polygon_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/btcb_abi.json")
btcb_polygon_abi = json.load(open(btcb_polygon_abi_path))
btcb_polygon_contract = web3_polygon.eth.contract(
    address=BTCB_POLYGON_ADDRESS, abi=btcb_polygon_abi)


def solidity_pack(types, values):
    packed_data = encode_packed(types, values)
    return packed_data


def address_to_bytes32(address: str) -> str:
    address_without_prefix = address[2:] if address.startswith(
        "0x") else address
    padded_address = "0" * \
        (64 - len(address_without_prefix)) + address_without_prefix

    # return Web3.to_bytes(text=padded_address)
    return f'0x{padded_address}'


def send_btcb_to_avax(private_key, btcb_amount):
    account = web3_polygon.eth.account.from_key(private_key)
    address = account.address
    check_enough_gas(web3_polygon, address, GAS_LIMIT)
    BRIDGE_POLYGON_ADDRESS = "0x2297aEbD383787A160DD0d9F71508148769342E3"
    bridge_polygon_abi_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "../abis/btcb_bridge_abi.json")
    bridge_polygon_abi = json.load(open(bridge_polygon_abi_path))
    bridge_polygon_contract = web3_polygon.eth.contract(
        address=BRIDGE_POLYGON_ADDRESS, abi=bridge_polygon_abi)
    adapter_param = solidity_pack(["uint16", "uint256"], [1, 225000])
    btcb_amount_float = btcb_amount / 10 ** 8
    fees = bridge_polygon_contract.functions.estimateSendFee(
        AVALANCHE_ID,
        address_to_bytes32(address),
        btcb_amount,
        False,
        adapter_param
    ).call()
    fee = fees[0]
    # Approve BTCB (Polytgon)
    allowance = btcb_polygon_contract.functions.allowance(
        address, BRIDGE_POLYGON_ADDRESS).call()
    if (allowance < btcb_amount):
        try:
            nonce = web3_polygon.eth.get_transaction_count(address)
            transaction_params = {
                'from': address,
                'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_POLYGON, 'gwei'),
                'maxFeePerGas': Web3.to_wei(MAX_FEE_POLYGON, 'gwei'),
                # 'gasPrice': web3_polygon.eth.gas_price,
                'nonce': nonce,
                'gas': GAS_LIMIT
            }
            txn = btcb_polygon_contract.functions.approve(
                BRIDGE_POLYGON_ADDRESS, btcb_amount).build_transaction(transaction_params)
            try:
                del txn['gasPrice']
            except:
                pass
            signed_txn = web3_polygon.eth.account.sign_transaction(
                txn, private_key)
            tx_hash = web3_polygon.eth.send_raw_transaction(
                signed_txn.rawTransaction)
            receipt = web3_polygon.eth.wait_for_transaction_receipt(
                tx_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"[BTCB BRIDGE] Can't approve BTCB for {btcb_amount_float} on {address}")
                return -1
            print(
                f'[BTCB BRIDGE] Success approve BTCB for {btcb_amount_float} on {address}')
        except:
            print(
                f'[BTCB BRIDGE] Failed approve BTCB on {address}. Will be retried.')
            return -1

    check_enough_gas(web3_polygon, address, GAS_LIMIT)
    nonce = web3_polygon.eth.get_transaction_count(address)
    transaction_params = {
        'from': address,
        'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_POLYGON, 'gwei'),
        'maxFeePerGas': Web3.to_wei(MAX_FEE_POLYGON, 'gwei'),
        # 'gasPrice': web3_polygon.eth.gas_price,
        'nonce': nonce,
        'gas': GAS_LIMIT,
        'value': fee
    }
    try:
        bridge_txn = bridge_polygon_contract.functions.sendFrom(address, AVALANCHE_ID, address_to_bytes32(address), btcb_amount, btcb_amount, [
            address, '0x0000000000000000000000000000000000000001', adapter_param]).build_transaction(transaction_params)
        try:
            del bridge_txn['gasPrice']
        except:
            pass
        signed_bridge_txn = web3_polygon.eth.account.sign_transaction(
            bridge_txn, private_key)
        bridge_tx_hash = web3_polygon.eth.send_raw_transaction(
            signed_bridge_txn.rawTransaction)
        receipt = web3_polygon.eth.wait_for_transaction_receipt(
            bridge_tx_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[BTCB BRIDGE] Can't bridge BTCB from Polygon to Avalanche for {btcb_amount_float} BTC")
            return -1
        print(
            f"[BTCB BRIDGE] Success bridge BTCB from Polygon to Avalanche for {btcb_amount_float} BTC")
        return 1
    except Exception as e:
        print(f'e: {e}')
        print(f'[BTCB BRIDGE] Critical exception. Operation failed.')
        return -1


def send_btcb_to_polygon(private_key, btcb_amount):
    account = web3_avax.eth.account.from_key(private_key)
    address = account.address
    check_enough_gas(web3_avax, address, GAS_LIMIT)
    BRIDGE_AVAX_ADDRESS = "0x2297aEbD383787A160DD0d9F71508148769342E3"
    bridge_avax_abi_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "../abis/btcb_bridge_abi.json")
    bridge_avax_abi = json.load(open(bridge_avax_abi_path))
    bridge_avax_contract = web3_avax.eth.contract(
        address=BRIDGE_AVAX_ADDRESS, abi=bridge_avax_abi)
    adapter_param = solidity_pack(["uint16", "uint256"], [1, 225000])
    btcb_amount_float = btcb_amount / 10 ** 8

    fees = bridge_avax_contract.functions.estimateSendFee(
        POLYGON_ID,
        address_to_bytes32(address),
        btcb_amount,
        False,
        adapter_param
    ).call()
    fee = fees[0]
    # Approve BTCB (Avax)
    allowance = btcb_avax_contract.functions.allowance(
        address, BRIDGE_AVAX_ADDRESS).call()
    if (allowance < btcb_amount):
        try:
            nonce = web3_avax.eth.get_transaction_count(address)
            transaction_params = {
                'from': address,
                # 'gasPrice': web3_avax.eth.gas_price,
                'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
                'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
                'nonce': nonce,
                'gas': GAS_LIMIT
            }
            txn = btcb_avax_contract.functions.approve(
                BRIDGE_AVAX_ADDRESS, btcb_amount).build_transaction(transaction_params)
            # del txn['gasPrice']
            signed_txn = web3_avax.eth.account.sign_transaction(
                txn, private_key)
            tx_hash = web3_avax.eth.send_raw_transaction(
                signed_txn.rawTransaction)
            receipt = web3_avax.eth.wait_for_transaction_receipt(
                tx_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"[BTCB BRIDGE] Can't approve BTCB for {btcb_amount_float} on {address}")
                return -1
            print(
                f'[BTCB BRIDGE] Success approve BTCB for {btcb_amount_float} on {address}')
        except:
            print(
                f'[BTCB BRIDGE] Failed to approve BTCB on {address}. Will be retried.')
            return -1

    # Send BTCB
    check_enough_gas(web3_avax, address, GAS_LIMIT)
    nonce = web3_avax.eth.get_transaction_count(address)
    transaction_params = {
        'from': address,
        # 'gasPrice': web3_avax.eth.gas_price,
        'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
        'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
        'nonce': nonce,
        'gas': GAS_LIMIT,
        'value': fee
    }
    try:
        bridge_txn = bridge_avax_contract.functions.sendFrom(address, POLYGON_ID, address_to_bytes32(address), btcb_amount, btcb_amount, [
            address, '0x0000000000000000000000000000000000000001', adapter_param]).build_transaction(transaction_params)
        # del bridge_txn['gasPrice']
        signed_bridge_txn = web3_avax.eth.account.sign_transaction(
            bridge_txn, private_key)
        bridge_tx_hash = web3_avax.eth.send_raw_transaction(
            signed_bridge_txn.rawTransaction)
        receipt = web3_avax.eth.wait_for_transaction_receipt(
            bridge_tx_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[BTCB BRIDGE] Can't bridge BTCB from Avalanche to Polygon for {btcb_amount_float} BTC on address {address}")
            return -1
        print(
            f"[BTCB BRIDGE] Success bridge BTCB from Avalanche to Polygon for {btcb_amount_float} BTC on address {address}")
        return 1
    except:
        print(f'[BTCB BRIDGE] Critical exception. Operation failed.')
        return -1


if __name__ == '__main__':
    with open("private.txt", "r") as f:
        keys_list = [row.strip() for row in f]
    if len(keys_list) == 0:
        print(f'private.txt is empty')
        sys.exit(1)

    for private_key in keys_list:
        try:
            account = web3_avax.eth.account.from_key(private_key)
            btcb_amount_avax = btcb_avax_contract.functions.balanceOf(
                account.address).call()
            btcb_amount_polygon = btcb_polygon_contract.functions.balanceOf(
                account.address).call()
            # send_btcb_to_avax(account, private_key, btcb_amount_polygon)

        except Exception as e:
            print(f'Error: {e}')
