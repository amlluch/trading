from behave import fixture, use_fixture
from beberagestockmarket import Trade, Trading, Stock
from datetime import datetime, timedelta

import csv


@fixture
def preload_stocks(context):

    context.stock_list = list()
    with open('features/fixtures/stocks.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            context.stock_list.append(Stock(row['symbol'].strip(),
                                            row['stock_type'].strip(),
                                            int(row['last_dividend']),
                                            float(row['par_value']),
                                            fixed_dividend=float(row['fix_dividend'])))


@fixture
def preload_trades(context):
    trading_list = list()
    with open('features/fixtures/trades.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            stock = next((x for x in context.stock_list if x.symbol == row['symbol'].strip()), None)
            if not stock:
                continue
            timestamp = datetime.utcnow() + timedelta(minutes=float(row['timestamp']))
            trading_list.append(Trade(stock,
                                      int(row['quantity']),
                                      row['op'].strip(),
                                      float(row['price']),
                                      timestamp=timestamp))

    context.trading = Trading(trading_list)


def before_scenario(context, scenario):

    if 'bulk' in scenario.tags:
        use_fixture(preload_stocks, context)
        use_fixture(preload_trades, context)
