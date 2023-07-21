from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import config, network, interface, web3

amount = web3.toWei(0.1, "ether")


def get_pool():
    pool_addresses_provider = interface.IPoolAddressesProvider(
        config["networks"][network.show_active()]["pool_addresses_provider"]
    )
    pool_address = pool_addresses_provider.getPool()
    pool = interface.IPool(pool_address)
    return pool


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token ...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_borrowable_data(pool, account):
    (
        totalCollateral,
        totalDebt,
        availableBorrows,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = pool.getUserAccountData(account.address)
    # availableBorrows = web3.fromWei(availableBorrows, "ether")
    # totalCollateral = web3.fromWei(totalCollateral, "ether")
    # totalDebt = web3.fromWei(totalDebt, "ether")
    availableBorrows = availableBorrows
    totalCollateral = totalCollateral
    totalDebt = totalDebt
    print(f"You have {totalCollateral} worth of USD deposited")
    print(f"You have {totalDebt} worth of USD borrowed")
    print(f"You can borrow {availableBorrows} worth of USD")
    return (float(availableBorrows), float(totalDebt))


def get_asset_price(price_feed_address):
    asset_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = (
        asset_price_feed.latestRoundData()[1] / 10 ** asset_price_feed.decimals()
    )
    print(f"The asset price is {latest_price}")
    return (float)(latest_price)


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    pool = get_pool()
    print(pool)
    approve_erc20(amount, pool.address, erc20_address, account)
    tx = pool.supply(erc20_address, amount, account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")
    borrowable_usd, total_debt = get_borrowable_data(pool, account)
    dai_usd_price = get_asset_price(
        config["networks"][network.show_active()]["dai_usd_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_usd_price) * (borrowable_usd * 0.95)
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["eth_price_feed"]
    )
    amount_dai_to_borrow_in_eth = amount_dai_to_borrow * dai_eth_price
    print(f"We are going to borrow {amount_dai_to_borrow_in_eth} ETH")
    dai_address = config["networks"][network.show_active()]["dai_token"]

    borrow_tx = pool.borrow(
        dai_address,
        1000000,
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.status()
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(pool, account)
