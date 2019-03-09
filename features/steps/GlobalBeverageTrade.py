from behave import *
from beberagestockmarket import Trade, Trading
from datetime import datetime
from datetime import timedelta
from math import isclose

use_step_matcher("re")


@when("I have a stock from <GIN> company")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: When I have a stock from <GIN> company')


@when('I have a stock from (?P<symbol>.+) company')
def step_impl(context, symbol):
    """
    :param symbol:
    :type context: behave.runner.Context
    """
    context.stock = next((x for x in context.stock_list if x.symbol == symbol), None)


@step("I (?P<op>.+) a number of (?P<quantity>.+) stocks at a price of (?P<price>.+) pennies")
def step_impl(context, op, quantity, price):
    """
    :param op: string
    :param price: float
    :param quantity: int
    :type context: behave.runner.Context
    """
    context.price = float(price)
    context.quantity = int(quantity)
    context.op = op


@then("I create NOW a trade and I add that trade to my trading market")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """

    trade = Trade(context.stock, context.quantity, context.op, context.price)
    trading = Trading()
    trading += trade


@when("I have a group of operations with a delta timestamp from now in minutes")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    """
                              | symbol | indicator | quantity | price | timestamp |
                              | TEA    | buy       | 250      | 235.0 |        +3 |
                              | TEA    | sell      | 125      | 234.5 |        -1 |
                              | GIN    | sell      | 101      | 189.0 |        +2 |
                              | JOE    | sell      | 1325     | 199.0 |        +3 |
                              | GIN    | buy       | 1897     | 187.0 |        -4 | 
    """
    trading = Trading()
    for raw in context.table:
        stock = next((x for x in context.stock_list if x.symbol == raw['symbol']), None)
        if not stock:
            continue
        timestamp = datetime.utcnow() + timedelta(minutes=float(raw['timestamp']))
        trade = Trade(stock, int(raw['quantity']), raw['indicator'], float(raw['price']), timestamp)
        trading += trade
    context.trading = trading


@then("get all trades from (?P<symbol>.+)")
def step_impl(context, symbol):
    """
    :param symbol: string
    :type context: behave.runner.Context
    """
    trade = context.trading.filter(symbol=symbol).to_list()
    cont = 0
    context.symbol = symbol
    for elem in trade:
        assert str(elem) == symbol
        cont += 1

    my_stock = context.stock_list[2]
    trading1 = Trading(context.trading.filter(symbol='TEA').to_list())
    trading2 = trading1 + Trade(my_stock, 3, 'sell', 321.3)
    trading3 = trading1 + context.trading.filter(symbol='GIN').to_list()
    trading4 = trading1 + Trading(context.trading.filter(symbol='JOE').to_list())
    trading5 = Trade(my_stock, 3, 'sell', 321.3) + trading1
    trading6 = context.trading.filter(symbol='GIN').to_list() + trading1

    print()
    print ('Initial trading')
    for trade in trading1.to_list():
        print (trade.symbol)
    print ('adding a list of trades')
    for trade in trading3.to_list():
        print (trade.symbol)
    print ('adding a single Trade')
    for trade in trading2.to_list():
        print (trade.symbol)
    print('adding a trading class')
    for trade in trading4.to_list():
        print (trade.symbol)
    print('Reverse operation with Trade object')
    for trade in trading5.to_list():
        print(trade.symbol)
    print('Reverse operation with list of Trades')
    for trade in trading6.to_list():
        print(trade.symbol)
    print('Ordered by timestamp')
    for trade in trading6.order_by().to_list():
        print(trade.timestamp)
    print('Ordered by timestamp reverse')
    for trade in trading6.order_by('-timestamp').to_list():
        print(trade.timestamp)
    print()


@then("get Weighted Stock Price on trades in past (?P<minutes>.+) minutes")
def step_impl(context, minutes):
    """
    :param minutes:
    :type context: behave.runner.Context
    """

    minutes = float(minutes)
    # calculates last 5 minutes trades

    antes =Trading(context.trading.after(datetime.utcnow() + timedelta(minutes=(-1)*minutes)).before(datetime.utcnow()).to_list())

    assert isclose(antes.weighted_price(context.symbol),234.83333,abs_tol=1e-5)



@then("calculate the geometric mean for all stocks")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert isclose(context.trading.geometric_mean(), 201.35, abs_tol=1e-2)


 #   print (context.fixture)


@when("I get many operations from fixtures")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    print (u'STEP: When I get many operations from fixtures')