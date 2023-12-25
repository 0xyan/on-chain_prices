from web3 import Web3
import requests
from dotenv import load_dotenv
import os

load_dotenv()

infura_key = os.getenv("INFURA_KEY")
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_key}"))

pair_address = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
# pair_address = Web3.to_checksum_address(pair_address)

pair_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "reserve1", "type": "uint112"},
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

# UNISWAP V2 PRICE CALC

pair_contract = w3.eth.contract(address=pair_address, abi=pair_abi)

reserves = pair_contract.functions.getReserves().call()

current_USDC = reserves[0] / 1e6
current_ETH = reserves[1] / 1e18
initial_price = current_USDC / current_ETH

eth_to_sell = 10
uniswap_fee = 0.003

# af = after fees
eth_to_sell_af = eth_to_sell * (1 - uniswap_fee)

new_ETH_reserve = current_ETH + eth_to_sell_af
new_USDC_reserve = (current_USDC * current_ETH) / new_ETH_reserve

price_after_swap = new_USDC_reserve / new_ETH_reserve

midprice = (initial_price + price_after_swap) / 2

final_price_uniswap = midprice * (1 - uniswap_fee)

# print(f"Initial price: {initial_price}, New price: {price_after_swap}, Midprice: {midprice} ")
print(f"Final price on Uni v2: {round(final_price_uniswap, 7)}")

# 1INCH PRICE CALC

method = "get"
apiUrl = "https://api.1inch.dev/swap/v5.2/1/quote"
requestOptions = {
    "headers": {"Authorization": "Bearer 3nms53nV5fafyHttqCDpE0sN5NGHGoU7"},
    "body": {},
    "params": {
        "src": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        "dst": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "amount": "10000000000000000000",
    },
}

# Prepare request components
headers = requestOptions.get("headers", {})
body = requestOptions.get("body", {})
params = requestOptions.get("params", {})


response = requests.get(apiUrl, headers=headers, params=params)
usdc_received = response.json()
usdc_received = float(usdc_received["toAmount"]) / 1e6
final_price_1inch = usdc_received / eth_to_sell

print(f"Final price on 1inch: {final_price_1inch}")
