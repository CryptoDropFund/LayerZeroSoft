from web3 import Web3

# Установка провайдера Infura для подключения к сети Avalanche
w3 = Web3(Web3.HTTPProvider(
    'https://avax-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))

# Определение адресов контрактов USDC, BUSD и Uniswap
usdc_address = '0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664'
busd_address = '0x4Fabb145d64652a948d72533023f6E7A623C7C53'
uniswap_address = '0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106'

# Загрузка контрактов USDC, BUSD и Uniswap с помощью их адресов и ABI
usdc_contract = w3.eth.contract(address=usdc_address, abi=USDC_ABI)
busd_contract = w3.eth.contract(address=busd_address, abi=BUSD_ABI)
uniswap_contract = w3.eth.contract(address=uniswap_address, abi=UNISWAP_ABI)

# Установка адреса вашего кошелька на сети Avalanche
my_address = '0x1234567890123456789012345678901234567890'

# Определение количества USDC, которые вы хотите продать
usdc_amount = 1000

# Получение количества BUSD, которые вы получите в обмен на USDC на DEX Uniswap
busd_amount = uniswap_contract.functions.getAmountsOut(
    usdc_amount,
    [usdc_address, busd_address]
).call()[-1]

# Получение текущего allowance для контракта Uniswap
allowance = usdc_contract.functions.allowance(
    my_address,
    uniswap_address
).call()

# Если текущий allowance меньше необходимого, то выполните операцию approve для контракта USDC
if allowance < usdc_amount:
    tx_hash = usdc_contract.functions.approve(
        uniswap_address,
        2**256 - 1
    ).transact({
        'from': my_address,
        'gas': 100000,
        'gasPrice': w3.toWei('10', 'gwei')
    })

# Выполнение операции обмена на DEX Uniswap
tx_hash = uniswap_contract.functions.swapExactTokensForTokens(
    usdc_amount,
    busd_amount,
    [usdc_address, busd_address],
    my_address,
    int(time.time()) + 300
).transact({
    'from': my_address,
    'gas': 100000,
    'gasPrice': w3.toWei('10', 'gwei')
})
