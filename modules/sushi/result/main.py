import json
import os
import decimal as decimal_lib
from time import sleep

from web3 import Web3
from modules.utils import check_enough_gas_1559
from web3.middleware import geth_poa_middleware


with open('config.json', "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

RPC_AVALANCHE = config['AVAX_RPC_URL']
RPC_POLYGON = config['POLYGON_RPC_URL']
RPC_FANTOM = config['FANTOM_RPC_URL']

MAX_PRIORITY_FEE_AVAX = config['MAX_PRIORITY_FEE_AVAX']
MAX_FEE_AVAX = config['MAX_FEE_AVAX']

MAX_PRIORITY_FEE_POLYGON = config['MAX_PRIORITY_FEE_POLYGON']
MAX_FEE_POLYGON = config['MAX_FEE_POLYGON']

MAX_PRIORITY_FEE_FTM = config['MAX_PRIORITY_FEE_FTM']
MAX_FEE_FTM = config['MAX_FEE_FTM']

GASLIMIT_AVAX = config['GASLIMIT_AVAX']
GASLIMIT_POLYGON = config['GASLIMIT_POLYGON']
GASLIMIT_FTM = config['GASLIMIT_FTM']

POLYGON = 'POLYGON'
AVALANCHE = 'AVALANCHE'
FANTOM = 'FANTOM'

RPC = {
    AVALANCHE: RPC_AVALANCHE,
    POLYGON: RPC_POLYGON,
    FANTOM: RPC_FANTOM
}

MAX_PRIORITY_FEE = {
    AVALANCHE: MAX_PRIORITY_FEE_AVAX,
    POLYGON: MAX_PRIORITY_FEE_POLYGON,
    FANTOM: MAX_PRIORITY_FEE_FTM
}

MAX_FEE = {
    AVALANCHE: MAX_FEE_AVAX,
    POLYGON: MAX_FEE_POLYGON,
    FANTOM: MAX_FEE_FTM
}

GAS_LIMIT = {
    AVALANCHE: GASLIMIT_AVAX,
    POLYGON: GASLIMIT_POLYGON,
    FANTOM: GASLIMIT_FTM
}

AVALANCHE_ERC20_ADDRESS = {
    'USDC': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
    'FRAX': '0xD24C2Ad096400B6FBcd2ad8B24E7acBc21A1da64',
    'DAI': '0xd586E7F844cEa2F87f50152665BCbc2C279D8d70',
    'TUSD': '0x1C20E891Bab6b1727d14Da358FAe2984Ed9B59EB',
    'BUSD': '0x9C9e5fD8bbc25984B178FdCE6117Defa39d2db39',
}
AVALANCHE_ERC20_TOKENS = {
    'USDC': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
    'FRAX': '0xD24C2Ad096400B6FBcd2ad8B24E7acBc21A1da64',
    'DAI': '0xd586E7F844cEa2F87f50152665BCbc2C279D8d70',
    'TUSD': '0x1C20E891Bab6b1727d14Da358FAe2984Ed9B59EB',
    'BUSD': '0x9C9e5fD8bbc25984B178FdCE6117Defa39d2db39',
}
POLYGON_ERC20_ADDRESS = {
    'USDC': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
    'FRAX': '0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89',
    'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
    'BUSD': '0x9C9e5fD8bbc25984B178FdCE6117Defa39d2db39',
    'MATIC': '0x0000000000000000000000000000000000001010',
}
POLYGON_ERC20_TOKENS = {
    'USDC': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
    'FRAX': '0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89',
    'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
    'BUSD': '0x9C9e5fD8bbc25984B178FdCE6117Defa39d2db39',
    'MATIC': '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
}
FANTOM_ERC20_ADDRESS = {
    'USDC': '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
    'FRAX': '0xdc301622e621166BD8E82f2cA0A26c13Ad0BE355',
    'DAI': '0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E',
}
FANTOM_ERC20_TOKENS = {
    'USDC': '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
    'FRAX': '0xdc301622e621166BD8E82f2cA0A26c13Ad0BE355',
    'DAI': '0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E',
}

polygon_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/polygon_erc20_abi.json")
POLYGON_ERC20_ABI = json.load(open(polygon_abi_file_path))
avalanche_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/avalanche_erc20_abi.json")
AVALANCHE_ERC20_ABI = json.load(open(avalanche_abi_file_path))
fantom_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/polygon_erc20_abi.json")
FANTOM_ERC20_ABI = json.load(open(fantom_abi_file_path))

NETWORK_ERC20_ADDR = {
    AVALANCHE: AVALANCHE_ERC20_ADDRESS,
    POLYGON: POLYGON_ERC20_ADDRESS,
    FANTOM: FANTOM_ERC20_ADDRESS,
}

NETWORK_ERC20_ABI = {
    AVALANCHE: AVALANCHE_ERC20_ABI,
    POLYGON: POLYGON_ERC20_ABI,
    FANTOM: FANTOM_ERC20_ABI,
}

NETWORK_ERC20_TOKENS = {
    AVALANCHE: AVALANCHE_ERC20_TOKENS,
    POLYGON: POLYGON_ERC20_TOKENS,
    FANTOM: FANTOM_ERC20_TOKENS,
}

TXN_EXPLORER = {
    AVALANCHE: 'https://snowtrace.io/tx/',
    POLYGON: 'https://polygonscan.com/tx/',
    FANTOM: 'https://ftmscan.com/tx/',
}

sushi_address = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'
sushi_abi_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../abis/sushi_abi.json")
sushi_abi = json.load(open(sushi_abi_file_path))


def check_enough_gas(web3_provider: Web3, address: str, GAS_LIMIT: int = 3000000):
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


def int_to_decimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"] * decimal)))


def decimal_to_int(price, decimal):
    divisor = decimal_lib.Decimal('10') ** decimal
    result = decimal_lib.Decimal(price) / divisor
    result = result.quantize(decimal_lib.Decimal(
        f'1E-{decimal - 1}'), rounding=decimal_lib.ROUND_DOWN)
    return result.normalize()


def float_str(amount, decimals=18):
    temp_str = "%0.18f"
    temp_str = temp_str.replace('18', str(decimals))
    text_float = temp_str % amount
    return text_float


def get_erc20_contract(web3: Web3, contract_address, ERC20_ABI=''):
    if ERC20_ABI == '':
        erc20_abi_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "../abis/erc20_abi.json")
        usdc_abi = json.load(open(erc20_abi_path))
        ERC20_ABI = usdc_abi

    contract = web3.eth.contract(
        Web3.to_checksum_address(contract_address), abi=ERC20_ABI)

    return contract


def swap(web3_provider: Web3, private_key: str, network: str, swap_in_str, swap_out_str, amount):
    web3_provider.middleware_onion.inject(geth_poa_middleware, layer=0)
    sushi_contract = web3_provider.eth.contract(
        Web3.to_checksum_address(sushi_address), abi=sushi_abi)
    chain_id = web3_provider.eth.chain_id
    account = web3_provider.eth.account.from_key(private_key)
    my_address = account.address

    sell_address = Web3.to_checksum_address(
        NETWORK_ERC20_TOKENS[network][swap_in_str])
    sell_abi = NETWORK_ERC20_ABI[network][swap_in_str]
    sell_contract_address = Web3.to_checksum_address(
        NETWORK_ERC20_ADDR[network][swap_in_str])
    sell_contract = get_erc20_contract(
        web3_provider, sell_contract_address, sell_abi)

    out_decimals = sell_contract.functions.decimals().call()
    amount_d = int_to_decimal(amount, out_decimals)
    amount_str = float_str(amount, out_decimals)

    buy_address = Web3.to_checksum_address(
        NETWORK_ERC20_TOKENS[network][swap_out_str]
    )

    path = [sell_address,
            buy_address]

    # while True:
    #     try:
    #         sushi_contract.functions.getAmountsOut(
    #             amount_d,
    #             path
    #         ).call()[1]
    #         break
    #     except:
    #         print(f'[SUSHI]: Pair not found. Repeat after 30 seconds...')
    #         sleep(30)

    allowance = sell_contract.functions.allowance(
        my_address, sushi_address).call()

    if (allowance <= amount_d):
        check_enough_gas_1559(web3_provider, my_address,
                              MAX_FEE[network], GAS_LIMIT[network])
        try:
            approve_txn = sell_contract.functions.approve(sushi_address, amount_d).build_transaction({
                'from': my_address,
                'gas': GAS_LIMIT[network],
                'maxPriorityFeePerGas': Web3.to_wei(
                    MAX_PRIORITY_FEE[network], 'gwei'),
                'maxFeePerGas': Web3.to_wei(MAX_FEE[network], 'gwei'),
                'nonce': web3_provider.eth.get_transaction_count(my_address),
            })
            signed_approve_txn = web3_provider.eth.account.sign_transaction(
                approve_txn, private_key)
            approve_tx_hash = web3_provider.eth.send_raw_transaction(
                signed_approve_txn.rawTransaction)
            receipt = web3_provider.eth.wait_for_transaction_receipt(
                approve_tx_hash, None, 1)
            if receipt['status'] != 1:
                print(
                    f"[SUSHI] Can't approve {swap_in_str} for {amount_str} on {my_address}")
                return -1
            print(
                f'[SUSHI] Success approve {swap_in_str} for {amount_str} on {my_address}')
        except:
            print(
                f"[SUSHI] Failed approve for {swap_in_str} on address {my_address}")
            return -1
    check_enough_gas_1559(web3_provider, my_address,
                          MAX_FEE[network], GAS_LIMIT[network])
    deadline = web3_provider.eth.get_block('latest')['timestamp'] + 1200
    to = my_address
    # amount_min = int(amount_d * 0.2)
    amount_min = 0

    swap_txn = sushi_contract.functions.swapExactTokensForTokens(
        amount_d,
        amount_min,  # минимальное количество получаемых токенов, обычно устанавливают значение 0 для совместимости
        path,
        to,
        deadline
    ).build_transaction({
        'from': my_address,
        'gas': GAS_LIMIT[network],
        'maxPriorityFeePerGas': Web3.to_wei(
            MAX_PRIORITY_FEE[network], 'gwei'),
        'maxFeePerGas': Web3.to_wei(MAX_FEE[network], 'gwei'),
        'nonce': web3_provider.eth.get_transaction_count(my_address),
    })

    signed_swap_txn = web3_provider.eth.account.sign_transaction(
        swap_txn, private_key)
    tx_hash = web3_provider.eth.send_raw_transaction(
        signed_swap_txn.rawTransaction)
    receipt = web3_provider.eth.wait_for_transaction_receipt(
        tx_hash, None, 1)
    if receipt['status'] != 1:
        print(
            f"[SUSHI] Can't swap {swap_in_str} for {amount_str} to {swap_out_str} on {my_address}")
        return -1
    print(
        f'[SUSHI] Success swap {swap_in_str} for {amount_str} to {swap_out_str} on {my_address}')

    return 1
