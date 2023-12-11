import os
import random
from time import sleep
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware
import json

from modules.utils import check_enough_gas

with open('config.json', "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

GAS_LIMIT = config['AAVE_GASLIMIT']

MAX_PRIORITY_FEE_AVAX = config['MAX_PRIORITY_FEE_AVAX']
MAX_FEE_AVAX = config['MAX_FEE_AVAX']

AVAX_RPC_URL = config['AVAX_RPC_URL']
web3_avax = Web3(Web3.HTTPProvider(AVAX_RPC_URL))
web3_avax.eth.set_gas_price_strategy(medium_gas_price_strategy)
web3_avax.middleware_onion.inject(geth_poa_middleware, layer=0)

# Contract constants
AVAX_ADDRESS = Web3.to_checksum_address(
    "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7")
avax_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/avax_abi.json")
avax_abi = json.load(open(avax_abi_file_path))
avax_contract = web3_avax.eth.contract(address=AVAX_ADDRESS, abi=avax_abi)

USDC_ADDRESS = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
usdc_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/erc20_abi.json")
usdc_abi = json.load(open(usdc_abi_file_path))
usdc_contract = web3_avax.eth.contract(address=USDC_ADDRESS, abi=usdc_abi)

BTCB_ADDRESS = "0x152b9d0FdC40C096757F570A51E494bd4b943E50"
btcb_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/avalanche_btcb_abi.json")
btcb_abi = json.load(open(btcb_abi_file_path))
btcb_contract = web3_avax.eth.contract(address=BTCB_ADDRESS, abi=btcb_abi)

LENDING_POOL_ADDRESS_PROVIDER_ADDRESS = "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb"
lending_pool_address_provider_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/pool_addresses_provider.json")
lending_pool_address_provider_abi = json.load(
    open(lending_pool_address_provider_abi_path))
lending_pool_address_provider = web3_avax.eth.contract(
    address=LENDING_POOL_ADDRESS_PROVIDER_ADDRESS, abi=lending_pool_address_provider_abi)

ORACLE_ADDRESS = '0xEBd36016B3eD09D4693Ed4251c67Bd858c3c7C9C'
oracle_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/oracle_abi.json")
oracle_abi = json.load(
    open(oracle_abi_path))
oracle_provider = web3_avax.eth.contract(
    address=ORACLE_ADDRESS, abi=oracle_abi)


USDC_AAVE_ADDRESS = '0x625E7708f30cA75bfd92586e17077590C60eb4cD'
usdc_aave_contract = web3_avax.eth.contract(
    address=USDC_AAVE_ADDRESS, abi=usdc_abi)

lending_pool_abi_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/pool_abi.json")
lending_pool_abi = json.load(open(lending_pool_abi_path))


def get_borrowable_data(lending_pool, my_address):
    [
        total_collateral,
        total_debt,
        available_borrow,
        current_liquidation_threshold,
        tlv,
        health_factor,
    ] = lending_pool.functions.getUserAccountData(my_address).call()
    return (float(available_borrow), float(total_debt), float(total_collateral), float(health_factor))


def approve_usdc(account, amount, private_key, approve_address):
    check_enough_gas(web3_avax, account.address, GAS_LIMIT)
    nonce = web3_avax.eth.get_transaction_count(account.address)
    transaction_params = {
        'from': account.address,
        'chainId': web3_avax.eth.chain_id,
        'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
        'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
        # 'gasPrice': web3_avax.eth.gas_price,
        'nonce': nonce,
        'gas': GAS_LIMIT
    }
    txn = usdc_contract.functions.approve(
        approve_address, amount).build_transaction(transaction_params)
    try:
        del txn['gasPrice']
    except:
        pass
    signed_txn = web3_avax.eth.account.sign_transaction(txn, private_key)
    tx_hash = web3_avax.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash


def approve_btcb(account, amount, private_key, approve_address):
    check_enough_gas(web3_avax, account.address, GAS_LIMIT)
    nonce = web3_avax.eth.get_transaction_count(account.address)
    transaction_params = {
        'from': account.address,
        'chainId': web3_avax.eth.chain_id,
        'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
        'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
        # 'gasPrice': web3_avax.eth.gas_price,
        'nonce': nonce,
        'gas': GAS_LIMIT
    }
    txn = btcb_contract.functions.approve(
        approve_address, amount).build_transaction(transaction_params)
    try:
        del txn['gasPrice']
    except:
        pass
    signed_txn = web3_avax.eth.account.sign_transaction(txn, private_key)
    tx_hash = web3_avax.eth.send_raw_transaction(signed_txn.rawTransaction)

    return tx_hash


def get_btc_price():
    return float(oracle_provider.functions.getAssetPrice(BTCB_ADDRESS).call())

# Deposit USDC


def deposit(private_key, usdc_amount):
    account = web3_avax.eth.account.from_key(private_key)
    address = account.address
    check_enough_gas(web3_avax, address, GAS_LIMIT)
    try:
        lending_pool_address = lending_pool_address_provider.functions.getPool().call()
        lending_pool = web3_avax.eth.contract(
            address=lending_pool_address, abi=lending_pool_abi)
        usdc_amount_uint = int(Web3.to_wei(usdc_amount, 'mwei'))
        # Approve USDC
        allowance = usdc_contract.functions.allowance(
            account.address, lending_pool_address).call()
        if (allowance < usdc_amount_uint):
            tx_hash = approve_usdc(account, usdc_amount_uint,
                                   private_key, lending_pool_address)
            receipt = web3_avax.eth.wait_for_transaction_receipt(
                tx_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"[AAVE] Can't approve USDC for {usdc_amount} on {address}")
                return -1
            print(
                f'[AAVE] Success approve USDC for {usdc_amount} on {address}')
        # Deposit USDC
        nonce = web3_avax.eth.get_transaction_count(address)
        transaction_params = {
            'from': address,
            'chainId': web3_avax.eth.chain_id,
            'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
            'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
            # 'gasPrice': web3_avax.eth.gas_price,
            'nonce': nonce,
            'gas': GAS_LIMIT
        }
        deposit_txn = lending_pool.functions.supply(
            USDC_ADDRESS, usdc_amount_uint, address, 0).build_transaction(transaction_params)
        try:
            del deposit_txn['gasPrice']
        except:
            pass
        signed_deposit_txn = web3_avax.eth.account.sign_transaction(
            deposit_txn, private_key)
        deposit_tx_hash = web3_avax.eth.send_raw_transaction(
            signed_deposit_txn.rawTransaction)
        receipt = web3_avax.eth.wait_for_transaction_receipt(
            deposit_tx_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[AAVE] Can't deposit USDC for {usdc_amount} on {address}")
            return -1
        print(
            f'[AAVE] Success deposit USDC for {usdc_amount} on {address}')
        return 1
    except:
        print(f'[AAVE] Exception catched. Retry')
        return -1


# Borrow function (borrow BTC.B)


def borrow(private_key):
    account = web3_avax.eth.account.from_key(private_key)
    address = account.address
    check_enough_gas(web3_avax, address, GAS_LIMIT)
    try:
        lending_pool_address = lending_pool_address_provider.functions.getPool().call()
        lending_pool = web3_avax.eth.contract(
            address=lending_pool_address, abi=lending_pool_abi)

        # Borrow BTC-B
        # Calculate borrow
        borrowable_btc, _, _, _ = get_borrowable_data(
            lending_pool, address)
        btc_price = get_btc_price()
        amount_borrow = borrowable_btc / btc_price
        # Random loan value
        random_loan = random.uniform(0.2, 0.3)
        btcb_amount = int(amount_borrow * (10 ** 8) * random_loan)
        btcb_amount_str = btcb_amount / 10 ** 8

        nonce = web3_avax.eth.get_transaction_count(address)
        transaction_params = {
            'from': address,
            'chainId': web3_avax.eth.chain_id,
            'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
            'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
            # 'gasPrice': web3_avax.eth.gas_price,
            'nonce': nonce,
            'gas': GAS_LIMIT
        }
        borrow_txn = lending_pool.functions.borrow(
            BTCB_ADDRESS, btcb_amount, 2, 0, address).build_transaction(transaction_params)
        try:
            del borrow_txn['gasPrice']
        except:
            pass
        signed_borrow_txn = web3_avax.eth.account.sign_transaction(
            borrow_txn, private_key)
        borrow_tx_hash = web3_avax.eth.send_raw_transaction(
            signed_borrow_txn.rawTransaction)
        receipt = web3_avax.eth.wait_for_transaction_receipt(
            borrow_tx_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[AAVE] Can't borrow BTCB for {btcb_amount_str} on {address}")
            return -1
        print(
            f'[AAVE] Complete borrow BTCB for {btcb_amount_str} on account {address}')
        return 1
    except:
        print(f'[AAVE] Exception catched. Retry')
        return -1

# Repay (repay BTC-B + withdraw USDC)


def repay(private_key):
    account = web3_avax.eth.account.from_key(private_key)
    address = account.address
    check_enough_gas(web3_avax, address, GAS_LIMIT)
    try:
        lending_pool_address = lending_pool_address_provider.functions.getPool().call()
        lending_pool = web3_avax.eth.contract(
            address=lending_pool_address, abi=lending_pool_abi)
        btcb_amount = btcb_contract.functions.balanceOf(address).call()
        btcb_amount_str = btcb_amount / 10 ** 8
        allowance = btcb_contract.functions.allowance(
            address, lending_pool_address).call()

        if (allowance < btcb_amount):
            tx_hash = approve_btcb(account, btcb_amount,
                                   private_key, lending_pool_address)
            receipt = web3_avax.eth.wait_for_transaction_receipt(
                tx_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"[AAVE] Can't approve BTCB for {btcb_amount_str} in repay on {address}")
                return -1
            print(
                f'[AAVE] Success approve BTCB for {btcb_amount_str} on {address}')

        # Repay BTC-B
        transaction_params = {
            'chainId': web3_avax.eth.chain_id,
            # 'gasPrice': web3_avax.eth.gas_price,
            'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
            'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
            'nonce': web3_avax.eth.get_transaction_count(address),
            'gas': GAS_LIMIT
        }

        repay_txn = lending_pool.functions.repay(
            BTCB_ADDRESS, btcb_amount, 2, address).build_transaction(transaction_params)
        try:
            del repay_txn['gasPrice']
        except:
            pass

        signed_repay_txn = web3_avax.eth.account.sign_transaction(
            repay_txn, private_key)
        repay_tx_hash = web3_avax.eth.send_raw_transaction(
            signed_repay_txn.rawTransaction)
        receipt = web3_avax.eth.wait_for_transaction_receipt(
            repay_tx_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[AAVE] Can't repay BTCB for {btcb_amount} on {address}")
            return -1
        print(f'[AAVE] Success repay BTCB for {btcb_amount} on {address}')
        return 1
    except:
        print(f'[AAVE] Exception catched. Retry')
        return -1


def withdraw(private_key, retry=0):
    account = web3_avax.eth.account.from_key(private_key)
    address = account.address
    check_enough_gas(web3_avax, address, GAS_LIMIT)
    try:
        lending_pool_address = lending_pool_address_provider.functions.getPool().call()
        lending_pool = web3_avax.eth.contract(
            address=lending_pool_address, abi=lending_pool_abi)
        # Withdraw USDC
        available_usdc_uint256 = usdc_aave_contract.functions.balanceOf(
            address).call()
        available_usdc_str = available_usdc_uint256 / 10 ** 8

        transaction_params = {
            'chainId': web3_avax.eth.chain_id,
            # 'gasPrice': web3_avax.eth.gas_price,
            'maxPriorityFeePerGas': Web3.to_wei(MAX_PRIORITY_FEE_AVAX, 'gwei'),
            'maxFeePerGas': Web3.to_wei(MAX_FEE_AVAX, 'gwei'),
            'nonce': web3_avax.eth.get_transaction_count(address),
            'gas': GAS_LIMIT
        }
        withdraw_sum = available_usdc_uint256
        if (retry == 1):
            withdraw_sum = int(available_usdc_uint256 -
                               500000)
        if (retry == 2):
            withdraw_sum = int(available_usdc_uint256 -
                               1000000)
        if (retry == 3):
            withdraw_sum = int(available_usdc_uint256 -
                               2000000)
        if (retry > 3):
            return -1
        withdraw_txn = lending_pool.functions.withdraw(
            USDC_ADDRESS, withdraw_sum, address).build_transaction(transaction_params)
        try:
            del withdraw_txn['gasPrice']
        except:
            pass

        signed_withdraw_txn = web3_avax.eth.account.sign_transaction(
            withdraw_txn, private_key)
        withdraw_tx_hash = web3_avax.eth.send_raw_transaction(
            signed_withdraw_txn.rawTransaction)
        receipt = web3_avax.eth.wait_for_transaction_receipt(
            withdraw_tx_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[AAVE] Can't retreive USDC for {available_usdc_str} on {address}")
            return -1
        print(
            f'[AAVE] Success withdraw USDC for {available_usdc_str} on {address}')
        return 1
    except:
        print(f'[AAVE] Exception catched. Retry')
        return -1


if __name__ == '__main__':
    pass
