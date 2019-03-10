import unittest
import beberagestockmarket
from beberagestockmarket import Trading
from features.environment import preload_stocks, preload_trades
from datetime import datetime, timedelta
from math import isclose


class TestTrading(unittest.TestCase):

    def setUp(self):
        preload_stocks(self)        # load self.stock_list from BDD
        preload_trades(self)        # load self.trading  from BDD

        self.single_trade = self.trading.first()
        self.trading_list = self.trading.to_list()
        self.single_stock = self.stock_list[0]

        self.bad_trading_list = self.trading_list.copy()
        self.bad_trading_list.append('bad element')

    @staticmethod
    def preferred_yield(price, dividend, par):
        return (dividend * par) / price

    def test_trading_instantiation(self):
        """
        You can instantiate using a list of trade objects or with no parameters
        If you instantiate with a list, every single object must be Trade type
        """
        self.assertIsInstance(Trading(self.trading_list), Trading)
        self.assertIsInstance(Trading(), Trading)

        with self.assertRaises(Exception):
            Trading(self.bad_trading_list)

    def test_trading_addition(self):
        """
        Testing adding elements to a Trading with different data types

        new_trading = Trading(list_of_trades) + Trade(single_trade_params)
        new_trading = Trading(list_of_trades) + list_of_trades
        new_trading = Trading(list_of_trades) + Trading(list_of_trades)

        """
        self.assertIsInstance(self.trading + self.trading, Trading)
        self.assertIsInstance(self.trading + self.single_trade, Trading)
        self.assertIsInstance(self.single_trade + self.trading, Trading)
        self.assertIsInstance(self.trading + self.trading_list, Trading)
        self.assertIsInstance(self.trading_list + self.trading, Trading)

        with self.assertRaises(Exception):
            self.trading + 1
            self.trading + self.bad_trading_list

    def test_trading_filters(self):
        """
        filter: gets a list of trades filtered by criteria
            examples:
                trading.filter().to_list() : will return a list with all trades inside the trading
                trading.filter(symbol='POP').to_list(): will return a list with all trades for this stock
                trading.filter(symbol='POP', op='sell').to_list() will return a list with all sell operations from this stock
        exclude: as filter but excluding by criteria
        before: gets all trades before a time
        after: gets all trades after a time
        order_by: order the trading list by any field. Start the field name by '-' for reverse ordering

        TRADES:

        symbol,  op,   quantity,    price, timestamp
        TEA      buy        250     235.0       -3.5
        TEA      sell       125     234.5       -1.7
        GIN      sell       101     189.0       -2.3
        JOE      sell      1325     199.0       -6.4
        GIN      buy       1897     187.0       -4
        MIL      sell      1200     188.0       -2

        """
        self.assertEqual(len(self.trading.to_list()), 6)

        filtered_trading = Trading(self.trading.filter(symbol='TEA').to_list())
        self.assertEqual(len(filtered_trading.get_symbols()), 1)

        filtered_trading = Trading(self.trading.filter(symbol='TEA', op='sell').to_list())
        self.assertEqual(len(filtered_trading.to_list()), 1)

        filtered_trading = Trading(self.trading.filter(symbol='TEA').exclude(op='sell').to_list())
        self.assertEqual(len(filtered_trading.to_list()), 1)

        filtered_trading = self.trading.filter().to_list()
        self.assertEqual(len(filtered_trading), 6)

        time_before = datetime.utcnow() - timedelta(minutes=2)

        filtered_trading = self.trading.before(time_before).order_by('symbol').to_list()
        self.assertEqual(len(filtered_trading), 5)
        self.assertEqual(filtered_trading[0].symbol, 'GIN')
        new_ordered = Trading(filtered_trading).order_by('-timestamp').to_list()
        self.assertEqual(new_ordered[0].symbol, 'MIL')

        filtered_trading = self.trading.after(time_before).order_by('-timestamp').to_list()
        self.assertEqual(len(filtered_trading), 1)
        self.assertEqual(filtered_trading[0].symbol, 'TEA')

        filtered_trading = self.trading.exclude(symbol='TEA').after(time_before).order_by('timestamp').to_list()
        self.assertEqual(len(filtered_trading), 0)

        with self.assertRaises(Exception):
            Trading(self.trading.filter(symbol='TEA').exclude(opa='sell').to_list())
            Trading(None.filter(symbol='TEA').to_list())

    def test_trading_calculations(self):
        """
        weighted_price: calculates the Volume Weighted Stock Price for a given symbol
        geometric_mean:  geometric mean for whole trading
        """
        antes = Trading(self.trading.after(datetime.utcnow() + timedelta(minutes=(-1) * 5)).
                        before(datetime.utcnow()).to_list())                                # all trades last 5 minutes
        self.assertTrue(isclose(antes.weighted_price('TEA'), 234.83333, abs_tol=1e-5))
        self.assertTrue(isclose(self.trading.geometric_mean(), 201.35, abs_tol=1e-2))

    def test_stock(self):
        """
        dividend yield: given a price

        P/E ratio or PER: given a price
        | my_symbol | my_price  | results |
        | GIN       |       225 |   112.5 |
        | ALE       |        92 |     4.0 |
        | MOM       |        90 |    30.0 |
        | JOE       |        91 |     7.0 |
        | TEA       |        45 |     0.0 |

        """
        # Dividend yield for a given price
        dividend_yield = self.single_stock.dividend_yield(225)      # for single stock
        target = self.single_stock.last_dividend / 225              # calculate manually
        self.assertEqual(dividend_yield, target)

        for stock in self.stock_list:                               # for the whole stock list
            dividend_yield = stock.dividend_yield(225)
            target = stock.last_dividend / 225 if stock.stock_type == 'common' \
                else self.preferred_yield(225, stock.fixed_dividend, stock.par_value)
            self.assertEqual(dividend_yield, target)
        # Tests the PER for the stocks in table with previously calculated results
        prices = [225, 92, 90, 91, 45]
        results = [112.5, 4.0, 30.0, 7.0, 0.0]
        symbols = ['GIN', 'ALE', 'MOM', 'JOE', 'TEA']

        for symbol, price, result in zip(symbols, prices, results):
            stock = next((x for x in self.stock_list if x.symbol == symbol), None)
            self.assertEqual(stock.pe_ratio(price), result if result != 0 else None)


if __name__ == '__main__':
    unittest.main()
