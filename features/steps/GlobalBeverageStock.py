from behave import *
from beberagestockmarket import Stock

use_step_matcher("re")

def preferred_yield(price, dividend, par):
    return (dividend * par) / price


@given("a set of data")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """



@when('a 3 digits string named "(?P<symbol>.+)"')
def step_impl(context, symbol):
    """
    :type context: behave.runner.Context
    :type symbol: str
    """
    context.symbol = symbol


@step('a string named stock type with value "(?P<stock_type>.+)" of two possible')
def step_impl(context, stock_type):
    """
    :type context: behave.runner.Context
    :type stock_type: str
    """
    context.stock_type = stock_type


@step('a numeric number named Last Dividend with value "(?P<last_dividend>.+)"')
def step_impl(context, last_dividend):
    """
    :type context: behave.runner.Context
    :type last_dividend: float
    """
    context.last_dividend = float(last_dividend)


@step('other numeric value named Fixed Dividend with value (?P<fixed_dividend>.+)')
def step_impl(context, fixed_dividend):
    """
    :type context: behave.runner.Context
    :type fixed_dividend: str
    """

    context.fixed_dividend = fixed_dividend


@step('another numeric value named Par Value with value (?P<par_value>.+)')
def step_impl(context, par_value):
    """
    :type context: behave.runner.Context
    :type par_value: float
    """
    context.par_value = float(par_value)


@then("I create a single stock")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """

    stock = Stock(context.symbol, context.stock_type, context.last_dividend, context.par_value,
                  fixed_dividend=context.fixed_dividend)

    assert (context.symbol == str(stock))


@given("a list of stock elements")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    """
    | symbol | stock_type | last_dividend | fix_dividend | par_value |
    | TEA    | Common     |             0 |            0 |       100 |
    | POP    | Common     |             8 |            0 |       100 |
    | ALE    | Common     |            23 |            0 |        60 |
    | GIN    | Preferred  |             8 |          2 % |       100 |
    | JOE    | Common     |            13 |            0 |       250 |
    | MIL    | Common     |            12 |            0 |        21 |
    | MOM    | Preferred  |            17 |            1 |        23 | 
    """
    context.stock_list = list()
    for raw in context.table:
        context.stock_list.append(Stock(raw['symbol'],
                                        raw['stock_type'],
                                        float(raw['last_dividend']),
                                        float(raw['par_value']),
                                        raw['fix_dividend']))


@when("I have a symbol (?P<my_symbol>.+)")
def step_impl(context, my_symbol):
    """
    :type context: behave.runner.Context
    :type my_symbol: str
    """
    context.my_symbol = my_symbol


@step("with price of (?P<my_price>.+) pennies")
def step_impl(context, my_price):
    """
    :type context: behave.runner.Context
    :type my_price: int
    """
    context.my_price = int(my_price)


@then("calculate the dividend yield")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """

    stock = next((x for x in context.stock_list if x.symbol == context.my_symbol), None)
    context.my_stock = stock

    assert stock.dividend_yield(context.my_price) == stock.last_dividend / context.my_price   \
        if stock.stock_type == 'common' else preferred_yield(context.my_price, stock.fixed_dividend, stock.par_value)


@then("calculate the P/E Ratio and compare to (?P<result>.+)")
def step_impl(context, result):
    """
    :type context: behave.runner.Context
    :type result: float
    """
    result = float(result)
    assert context.my_stock.pe_ratio(context.my_price) == None if result == 0 else result
