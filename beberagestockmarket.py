import re
from datetime import timedelta, datetime
import numpy as np
from scipy.stats.mstats import gmean


class Stock():  # This is a single stock with all info inside

    """
    creates a stock and includes all transactions on a given stock

    stock format:
        symbol: 3 characters
        stock_type: only "common" or "preferred" admitted
        last_dividend: numeric value
        par value: numeric value
        fixed_dividend: percent introduced as integer. Internally divides per 100
                        not mandatory for stock_type common

    operations:
        dividend yield: given a price
        P/E ratio or PER: given a price

    """

    def __init__(self, symbol, stock_type, last_dividend, par_value, fixed_dividend=None) :

        if len(symbol.strip()) != 3:
            raise Exception("Symbol {symbol} must have 3 characters and has {number}".format(number=len(symbol.strip()),
                                                                                             symbol=symbol.strip()))
        else:
            self.symbol = symbol.strip().upper()
        if stock_type.lower() not in ['common', 'preferred']:
            raise Exception("Only common or preferred values are admitted")
        else:
            self.stock_type = stock_type.lower()
        if not isinstance(last_dividend, (int, float)):
            raise Exception("Last dividend should be a numeric value")
        else:
            self.last_dividend = last_dividend
        if not isinstance(par_value, (int, float)):
            raise Exception("Par Value should be a numeric value")
        else:
            self.par_value = par_value
        if fixed_dividend:
            if isinstance(fixed_dividend, (int, float)):
                self.fixed_dividend = fixed_dividend / 100
            else:
                r = re.compile('(\d+(\.\d+)?)\%')
                percentage = fixed_dividend.replace(' ', '')
                if r.match(percentage):
                    self.fixed_dividend = float(percentage.strip('%')) / 100
                else:
                    try:
                        self.fixed_dividend = float(fixed_dividend) / 100
                    except ValueError:
                        self.fixed_dividend = 0
        else:
            self.fixed_dividend = 0
        if self.stock_type == 'preferred' and self.fixed_dividend == 0:
            raise Exception("No Fixed Dividend. Needed for Preferred stocks")

    def __str__(self):
        return self.symbol

    def dividend_yield(self, price):    # it calculates the dividend yield for a given stock
        if price == 0:
            raise Exception("Divide by 0!")
        if self.stock_type == 'common':
            return self.last_dividend / price
        else:
            return (self.fixed_dividend * self.par_value) / price

    def pe_ratio(self, price):  # it calculates the PER for a given stock
        if self.last_dividend == 0 or self.par_value == 0:
            return None
        if self.stock_type == 'common':
            return price / self.last_dividend
        else:
            return price / (self.fixed_dividend * self.par_value)


class Trade():  # a single trade with all info needed. If timestamp is None then will get time now

    """
    Creates a single trade.
    Trade format:
        stock: must be stock type
        quantity: integer value
        op: just 2 options ... "sell" or "buy"
        price: numeric value
        timestamp: on ISO format. If is passed as None it will take the time at that moment

    """

    def __init__(self, stock, quantity, op, price, timestamp=None):

        if type(stock) != Stock:
            raise Exception('No stock received')
        self.stock = stock
        self.symbol = stock.symbol          # Necessary for filters
        if type(quantity) != int:
            raise Exception('Quantity must be integer')
        else:
            self.quantity = quantity
        if not isinstance(price, (int, float)):
            raise Exception("Price should be a numeric value")
        else:
            self.price = price
        if op.lower() not in ['sell', 'buy']:
            raise Exception("You should indicate a 'sell' or 'buy' operation")
        self.op = op.lower()
        if timestamp:
            try:
                datetime.strftime(timestamp, '%Y-%m%dT%H:%M:%S.%f')
                self.timestamp = timestamp
            except ValueError:
                raise Exception("Time stamp is not in ISO format: YYYY-MM-DDTHH:MM:SS.mmmm")
        else:
            self.timestamp = datetime.utcnow().isoformat()

    def __str__(self):
        return self.stock.symbol


class Trading():    # A list of trades all together

    """
    A bunch of trades all together. You can create a void trading or a new one with a list of trades.
    It will check that every element of the list is a trade.

    Operation:

        _add_trade: add a trade to the trading. Must receive a trade element (Trading += Trade)
        _add_tradelist: add a list of trades to trading  (Trading += list_of_trades)
        filter: gets a list of trades filtered by criteria
            examples:
                trading.filter().to_list() : will return a list with all trades inside the trading
                trading.filter(symbol='POP').to_list(): will return a list with all trades for this stock
                trading.filter(symbol='POP', op='sell').to_list() will return a list with all sell operations from this stock
        exclude: as filter but excluding by criteria
        before: gets all trades before a time
        after: gets all trades after a time
        order_by: order the trading list by any field. Start the field name by '-' for reverse ordering
        to_list: returns filtered trade as a list or the whole trading as a list (list of Trade types)
        first: returns first trade from the trading list or filtered list (Trade type)
        get_symbols: gets all different stock symbols
        weighted_price: calculates the Volume Weighted Stock Price for a given symbol
        geometric_mean:  geometric mean for whole trading

        It is possible to chain filters. Next example gets buy operations from POP symbol last 5 minutes

        trading.filter(symbol='POP').exclude(op='sell').before(datetime.now()).after(datetime.now-timedelta(minutes=5).to_list()

        You can add Tradings. You can add a Trade, a list of trades or a Trading object
            new_trading = Trading(list_of_trades) + Trade(single_trade_params)
            new_trading = Trading(list_of_trades) + list_of_trades
            new_trading = Trading(list_of_trades) + Trading(list_of_trades)


    """

    def __init__(self, trading_list=None):  # you can create a void trade or a new one from a lits of trades
        self.trading_list = list()
        if trading_list:
            for trade in trading_list:
                if type(trade) != Trade:
                    raise Exception("No valid list. All elements must belong to Trade class")
            self.trading_list += trading_list
        self.filter_list = None

    def __add__(self, other):
        trading_list = self.trading_list.copy()
        trading = Trading(trading_list)
        if type(other) == Trade:
            trading._add_trade(other)
        elif type(other) == list:
            trading._add_tradelist(other)
        elif type(other) == Trading:
            trading._add_tradelist(other.to_list())
        else:
            raise Exception('Object must be Trade, a Trading or a list of Trade objects')

        return trading

    def __radd__(self, other):
        return self + other

    def _add_trade(self, trade):     # for adding a trade to the trading
        if type(trade) != Trade:
            raise Exception('Must be a Trade object')
        self.trading_list.append(trade)

    def _add_tradelist(self, trades):
        for trade in trades:
            if type(trade) != Trade:
                raise Exception('All objects should be Trade type')
        self.trading_list.extend(trades)

    def _tradingfilter(func):                                       # This decorator checks if exists a filter list.
        def add_filter_list(inst, *args, **kwargs):                 # If don't, creates it from the trading list
            if inst.filter_list is None:                            # in this case inst = self
                inst.filter_list = inst.trading_list.copy()
            for key in kwargs:                                      # checks key arguments for filters
                if not hasattr(inst.filter_list[0], key):
                    raise Exception('{} attribute doesn\'t exist'.format(key))
            result = func(inst, *args, **kwargs)
            return result
        return add_filter_list

    @_tradingfilter
    def filter(self, **kwargs):                     # you can get all trades just passing NO parameters
        for key, value in kwargs.items():           # or filter by any trade attribute or a group of attributes
            self.filter_list = [x for x in self.filter_list if getattr(x, key) == value]
        return self

    @_tradingfilter
    def exclude(self, **kwargs):
        for key, value in kwargs.items():
            self.filter_list = [x for x in self.filter_list if getattr(x, key) != value]
        return self

    @_tradingfilter
    def before(self, time):     # all trades BEFORE a time. Needs to_list()
        self.filter_list = [x for x in self.filter_list if x.timestamp <= time]
        return self

    @_tradingfilter
    def after(self, time):      # all trades AFTER a time. Needs to_list()
        self.filter_list = [x for x in self.filter_list if x.timestamp >= time]
        return self

    @_tradingfilter
    def order_by(self, field=None):
        if not field:
            field = 'timestamp'     # Order by timestamp by default
        if field[0:1] == '-':
            reverse = True          # Start the field by '-' for reverse sorting
            field = field[1:]
        else:
            reverse = False
        if self.filter_list:
            if not (hasattr(self.filter_list[0], field)):
                raise Exception('{} attribute doesn\'t exist'.format(field))
        self.filter_list.sort(key=lambda x: getattr(x, field), reverse=reverse)
        return self

    @_tradingfilter
    def to_list(self):          # Returns the filtered list of trades
        filter_list = self.filter_list.copy()
        self.filter_list = None
        return filter_list

    @_tradingfilter
    def first(self):
        filter_list = self.filter_list.copy()
        self.filter_list = None
        return filter_list[0]

    def get_symbols(self):      # gets the different stocks on the trading
        symbols = []

        for elem in self.trading_list:
            if elem.symbol not in symbols:
                symbols.append(elem.symbol)
        return symbols

    def weighted_price(self, symbol):   # calculates the Volume Weighted Stock Price for a given symbol

        stock_list = self.filter(symbol=symbol).to_list()
        if not stock_list:
            raise Exception('No objects on this query')
        matrix = np.asarray([[x.quantity, x.price] for x in stock_list], dtype=np.float32)
        prices = matrix[:,1]
        quantities = matrix[:,0]
        total_quantities = sum(quantities)
        if total_quantities == 0:
            raise Exception('Divide by 0!')

        return sum(np.multiply(prices, quantities)) / total_quantities

    def geometric_mean(self):       # geometric mean for whole trading
        stock_symbols = self.get_symbols()
        weights = [self.weighted_price(x) for x in stock_symbols]
        if not weights:
            raise Exception('No objects on this query')
        return gmean(weights)

