from time import sleep
from web3 import Web3


def check_enough_gas(web3_provider: Web3, address: str, GAS_LIMIT: int = 500000):
    native_token_balance = web3_provider.eth.get_balance(
        Web3.to_checksum_address(address))
    transaction_cost = GAS_LIMIT * web3_provider.eth.gas_price
    if (transaction_cost < native_token_balance):
        return
    print(f'Insufficient native token for transaction! Deposit native tokens for continue...')
    while (transaction_cost > native_token_balance):
        sleep(60)
        native_token_balance = web3_provider.eth.get_balance(
            Web3.to_checksum_address(address))
    return


def check_enough_gas_1559(web3_provider: Web3, address: str, gas_price: int, GAS_LIMIT: int = 500000):
    native_token_balance = web3_provider.eth.get_balance(
        Web3.to_checksum_address(address))
    transaction_cost = GAS_LIMIT * gas_price
    if (transaction_cost < native_token_balance):
        return
    print(f'Insufficient native token for transaction! Deposit native tokens for continue...')
    while (transaction_cost > native_token_balance):
        sleep(60)
        native_token_balance = web3_provider.eth.get_balance(
            Web3.to_checksum_address(address))
    return
