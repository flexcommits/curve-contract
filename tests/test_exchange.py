import time

U = 10 ** 18
N_COINS = 3


def test_few_trades(w3, coins, swap):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    bob = w3.eth.accounts[1]  # Bob the customer

    # Allow $1000 of each coin
    for c in coins:
        c.approve(swap.address, 1000 * U,
                  transact={'from': sam})

    # Adding $100 liquidity of each coin
    swap.add_liquidity(0, 100 * U, 110 * U, int(time.time()) + 3600,
                       transact={'from': sam})

    # Fund the customer with $100 of each coin
    for c in coins:
        c.transfer(bob, 100 * U,
                   transact={'from': sam})

    # Customer approves
    coins[0].approve(swap.address, 50 * U, transact={'from': bob})

    # And trades
    swap.exchange(0, 1, 1 * U,
                  int(0.9 * U), int(time.time()) + 3600,
                  transact={'from': bob})

    assert coins[0].balanceOf(bob) == 99 * U
    assert coins[1].balanceOf(bob) > int(100.9 * U)
    assert coins[1].balanceOf(bob) < 101 * U

    # Why not more
    swap.exchange(0, 1, 1 * U,
                  int(0.9 * U), int(time.time()) + 3600,
                  transact={'from': bob})

    assert coins[0].balanceOf(bob) == 98 * U
    assert coins[1].balanceOf(bob) > int(101.9 * U)
    assert coins[1].balanceOf(bob) < 102 * U
