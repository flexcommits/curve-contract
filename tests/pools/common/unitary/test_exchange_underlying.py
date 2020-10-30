from itertools import permutations

import pytest
from pytest import approx

pytestmark = [pytest.mark.usefixtures("add_initial_liquidity", "approve_bob"), pytest.mark.lending]


@pytest.mark.itercoins("sending", "receiving", underlying=True)
@pytest.mark.parametrize("fee,admin_fee", set(permutations([0, 0, 0.04, 0.5], 2)))
def test_amounts(
    bob,
    swap,
    underlying_coins,
    sending,
    receiving,
    fee,
    admin_fee,
    underlying_decimals,
    set_fees,
    n_coins,
    is_metapool,
):
    if fee or admin_fee:
        set_fees(10**10 * fee, 10**10 * admin_fee)
        if is_metapool and min(sending, receiving) > 0:
            fee = 0

    amount = 10**underlying_decimals[sending]
    underlying_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
    swap.exchange_underlying(sending, receiving, amount, 0, {'from': bob})

    assert underlying_coins[sending].balanceOf(bob) == 0

    received = underlying_coins[receiving].balanceOf(bob)
    prec = -min(underlying_decimals[receiving], 4)
    assert 1 - 10**prec - fee <= received / 10**underlying_decimals[receiving] < 1-fee


@pytest.mark.itercoins("sending", "receiving", underlying=True)
@pytest.mark.parametrize("fee,admin_fee", set(permutations([0, 0, 0.04, 0.5], 2)))
def test_fees(
    bob,
    swap,
    underlying_coins,
    sending,
    receiving,
    fee,
    admin_fee,
    underlying_decimals,
    wrapped_decimals,
    set_fees,
    get_admin_balances,
    base_amount,
    n_coins,
    is_metapool,
):
    if fee or admin_fee:
        set_fees(10**10 * fee, 10**10 * admin_fee)


    amount = (base_amount // 100) * 10**underlying_decimals[sending]
    underlying_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
    swap.exchange_underlying(sending, receiving, amount, 0, {'from': bob})

    admin_fees = get_admin_balances()
    if not (admin_fee * fee) or (is_metapool and min(sending, receiving) > 0):
        assert sum(admin_fees) <= 1
    else:
        admin_idx = min(n_coins-1, receiving)
        out_amount = amount / 10**underlying_decimals[sending]  # Basing on price 1.0
        expected_admin_fee = 10**wrapped_decimals[admin_idx] * fee * admin_fee * out_amount
        assert expected_admin_fee / admin_fees[admin_idx] == approx(1, rel=1e-3)


@pytest.mark.skip_pool("compound", "usdt")
@pytest.mark.itercoins("sending", "receiving", underlying=True)
def test_min_dy_underlying(bob, swap, underlying_coins, sending, receiving, underlying_decimals):
    amount = 10**underlying_decimals[sending]
    underlying_coins[sending]._mint_for_testing(bob, amount, {'from': bob})

    min_dy = swap.get_dy_underlying(sending, receiving, amount)
    swap.exchange_underlying(sending, receiving, amount, min_dy - 1, {'from': bob})

    assert abs(underlying_coins[receiving].balanceOf(bob) - min_dy) <= 1
