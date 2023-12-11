import os
from time import sleep
from web3 import Web3
import requests
import json
import decimal as decimal_lib

from modules.utils import check_enough_gas

with open('config.json', "r") as jsonfile:
    config = json.load(jsonfile)
    jsonfile.close()

SLIPPAGE = config['SLIPPAGE_SWAP']
RPC_AVALANCHE = config['AVAX_RPC_URL']
RPC_POLYGON = config['POLYGON_RPC_URL']
RPC_FANTOM = config['FANTOM_RPC_URL']

MAX_PRIORITY_FEE_AVAX = config['MAX_PRIORITY_FEE_AVAX']
MAX_FEE_AVAX = config['MAX_FEE_AVAX']

MAX_PRIORITY_FEE_POLYGON = config['MAX_PRIORITY_FEE_POLYGON']
MAX_FEE_POLYGON = config['MAX_FEE_POLYGON']

MAX_PRIORITY_FEE_FTM = config['MAX_PRIORITY_FEE_FTM']
MAX_FEE_FTM = config['MAX_FEE_FTM']


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


def get_api_call_data(url):
    try:
        call_data = requests.get(url)
    except Exception as e:
        print(f'[1INCH] Failed get api data. Try to repeat after 5s')
        sleep(5)
        return get_api_call_data(url)
    try:
        api_data = call_data.json()
        return api_data
    except Exception as e:
        print(f'[1INCH] Failed transform api data to json.')
        return None


def inch_allowance(swap_out_adr, my_address, base_url):
    try:
        _1inchurl = f'{base_url}/approve/allowance?tokenAddress={swap_out_adr}&walletAddress={my_address}'
        json_data = get_api_call_data(_1inchurl)
        if not json_data:
            return -1
        out_allowance = -1

        if 'allowance' in json_data.keys():
            out_allowance = json_data['allowance']

        return out_allowance
    except:
        return -1


def api_1inch_is_stable(base_url):
    _1inchurl = f'{base_url}/healthcheck'
    json_data = get_api_call_data(_1inchurl)

    if json_data['status'] == 'OK':
        return True

    print(f"[1INCH] API 1inch doesn't work!")
    return False


def inch_set_approve(web3: Web3, private_key, network, swap_in_addr, my_address, chain_id, base_url):
    try:
        _1inchurl = f'{base_url}/approve/transaction?tokenAddress={swap_in_addr}'
        tx = get_api_call_data(_1inchurl)
        tx['chainId'] = chain_id
        # tx['gasPrice'] = int(tx['gasPrice'])
        tx['from'] = Web3.to_checksum_address(my_address)
        tx['to'] = Web3.to_checksum_address(tx['to'])
        tx['value'] = int(tx['value'])
        tx['nonce'] = web3.eth.get_transaction_count(my_address)
        tx['maxPriorityFeePerGas'] = Web3.to_wei(
            MAX_PRIORITY_FEE[network], 'gwei')
        tx['maxFeePerGas'] = Web3.to_wei(MAX_FEE[network], 'gwei')

        estimate = web3.eth.estimate_gas(tx)
        gas_limit = estimate
        tx['gas'] = gas_limit
        try:
            del tx['gasPrice']
        except:
            pass
        check_enough_gas(web3, my_address, gas_limit)

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[1INCH] Can't approve {swap_in_addr}")
            return False

        txn_text = tx_hash.hex()

        print(
            f"[1INCH] Success approve on 1inch for {swap_in_addr} tx {TXN_EXPLORER[network]}{txn_text} on address {my_address}")
        return True
    except:
        print(
            f"[1INCH] Failed approve on 1inch in for {swap_in_addr} on address {my_address}")
        print(f'[1INCH] Failed transaction: {tx}')
        return False


def inch_swap(web3: Web3, private_key, network, swap_in_str, swap_out_str, amount, mode='TOKEN'):
    chain_id = web3.eth.chain_id
    account = web3.eth.account.from_key(private_key)
    my_address = account.address
    base_url = f'https://api.1inch.io/v5.0/{chain_id}'
    if not api_1inch_is_stable(base_url):
        print(f"[1INCH]: Error! API 1INCH doesn't work.")
        return -1

    try:
        swap_in_adr = Web3.to_checksum_address(
            NETWORK_ERC20_TOKENS[network][swap_in_str])
        swap_in_ABI = NETWORK_ERC20_ABI[network][swap_in_str]
        swap_in_contract_adr = Web3.to_checksum_address(
            NETWORK_ERC20_ADDR[network][swap_in_str])
        swap_in_contract = get_erc20_contract(
            web3, swap_in_contract_adr, swap_in_ABI)

        in_decimals = swap_in_contract.functions.decimals().call()
        # amount_d = int_to_decimal(amount, out_decimals)
        # amount_str = float_str(amount, out_decimals)
        amount_d = int_to_decimal(
            amount, in_decimals) if mode == 'TOKEN' else amount
        amount_str = float_str(
            amount, in_decimals) if mode == 'TOKEN' else decimal_to_int(amount, in_decimals)

        in_allowance = inch_allowance(swap_in_adr, my_address, base_url)
        if (int(in_allowance) < 0):
            print(f'[1INCH] Failed get inch_allowance. Try to repeat...')
            return -1

        swap_out_adr = Web3.to_checksum_address(
            NETWORK_ERC20_TOKENS[network][swap_out_str])

        if int(in_allowance) <= amount_d:
            while True:
                state = inch_set_approve(
                    web3, private_key, network, swap_in_adr, my_address, chain_id, base_url)
                if state == True:
                    break
                print(f'[1INCH] Try to repeat approve. Sleep 10s')
                sleep(10)
        check_enough_gas(web3, my_address, 800000)
        _1inchurl = f'{base_url}/swap?fromTokenAddress={swap_in_adr}&toTokenAddress={swap_out_adr}&amount={amount_d}&fromAddress={my_address}&slippage={SLIPPAGE}'
        json_data = get_api_call_data(_1inchurl)

        if ('error' in json_data):
            if ('Not enough' in json_data['description']):
                print(
                    f'[1INCH] Not enough balance on account {account.address}')
                print(f'[1INCH] NOT ENOUGH DATA {json_data}. Try to repeat.')
                return -1
                # exit(-1)
            if ('cannot estimate' in json_data['description']):
                print(f'[1INCH] Cannot esimate gas')
                return -1
            if ('Internal Server Error' in json_data['description']):
                print(f'[1INCH] Internal Server Error')
                return -1
            exit(-1)

        tx = json_data['tx']
        tx['chainId'] = chain_id
        tx['nonce'] = web3.eth.get_transaction_count(my_address)
        tx['to'] = Web3.to_checksum_address(tx['to'])
        try:
            del tx['gasPrice']
        except:
            pass
        # tx['gasPrice'] = int(tx['gasPrice'])
        tx['value'] = int(tx['value'])
        tx['maxPriorityFeePerGas'] = Web3.to_wei(
            MAX_PRIORITY_FEE[network], 'gwei')
        tx['maxFeePerGas'] = Web3.to_wei(MAX_FEE[network], 'gwei')
        # gas_price = tx['gasPrice']
        # print(f'gasPrice: {gas_price}')
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        txn_text = tx_hash.hex()
        to_token_amount = json_data['toTokenAmount']
        to_token_decimals = json_data['toToken']['decimals']

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, None, 1)
        if receipt['status'] != 1:
            print(
                f"[1INCH] Can't doing swap {swap_in_str} <-> {swap_out_str} for {amount_str} on address {my_address}")
            return -1
        print(
            f"[1INCH] Success swap {swap_in_str} <-> {swap_out_str} for {amount_str} tx {TXN_EXPLORER[network]}{txn_text} on address {my_address}")
        # return decimal_to_int(to_token_amount, to_token_decimals)
        return int(to_token_amount)

    except Exception as e:
        error = f'[1INCH] Failed swap {swap_in_str} <-> {swap_out_str} on address {my_address} | {e}'
        print(error)
        return -1


if __name__ == '__main__':
    print(f'[1INCH] Run global main script!')
