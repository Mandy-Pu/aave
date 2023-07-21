from scripts.helpful_scripts import get_account
from brownie import network, config, Contract


def get_weth():
    account = get_account()
    contract_address = config["networks"][network.show_active()]["weth_token"]
    weth = Contract.from_explorer(contract_address)
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    print("Received 0.1 WETH")
    return tx


def main():
    get_weth()
