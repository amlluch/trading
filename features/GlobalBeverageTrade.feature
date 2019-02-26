
Feature: Trade testing
  Single trade and trading tests

  Scenario: Single trade featuring
    Given a list of stock elements
    | symbol | stock_type | last_dividend | fix_dividend  | par_value |
    | TEA    | Common     |             0 |             0 |       100 |
    | POP    | Common     |             8 |             0 |       100 |
    | ALE    | Common     |            23 |             0 |        60 |
    | GIN    | Preferred  |             8 |            2% |       100 |
    | JOE    | Common     |            13 |             0 |       250 |
    | MIL    | Common     |            12 |             0 |        21 |
    | MOM    | Preferred  |            17 |             3 |       100 |
    When I have a stock from GIN company
    And I buy a number of 30 stocks at a price of 435 pennies
    Then I create NOW a trade and I add that trade to my trading market


  Scenario: Create a trading
    Given a list of stock elements
    | symbol | stock_type | last_dividend | fix_dividend  | par_value |
    | TEA    | Common     |             0 |             0 |       100 |
    | POP    | Common     |             8 |             0 |       100 |
    | ALE    | Common     |            23 |             0 |        60 |
    | GIN    | Preferred  |             8 |            2% |       100 |
    | JOE    | Common     |            13 |             0 |       250 |
    | MIL    | Common     |            12 |             0 |        21 |
    | MOM    | Preferred  |            17 |             3 |       100 |
    When I have a group of operations with a delta timestamp from now in minutes
    |symbol | indicator | quantity | price  | timestamp |
    | TEA   | buy       |      250 |  235.0 |      -3.5 |
    | TEA   | sell      |      125 |  234.5 |      -1.7 |
    | GIN   | sell      |      101 |  189.0 |      -2.3 |
    | JOE   | sell      |     1325 |  199.0 |      -6.4 |
    | GIN   | buy       |     1897 |  187.0 |        -4 |
    | MIL   | sell      |     1200 |  188.0 |        -2 |

    Then get all trades from TEA
    Then get Weighted Stock Price on trades in past 5 minutes
    Then calculate the geometric mean for all stocks

  @bulk
  Scenario: trading operations with fixtures
    Given a list of stock elements
    | symbol | stock_type | last_dividend | fix_dividend  | par_value |
    | TEA    | Common     |             0 |             0 |       100 |
    | POP    | Common     |             8 |             0 |       100 |
    | ALE    | Common     |            23 |             0 |        60 |
    | GIN    | Preferred  |             8 |            2% |       100 |
    | JOE    | Common     |            13 |             0 |       250 |
    | MIL    | Common     |            12 |             0 |        21 |
    | MOM    | Preferred  |            17 |             3 |       100 |
    When I get many operations from fixtures
    Then get all trades from TEA
    Then get Weighted Stock Price on trades in past 5 minutes
    Then calculate the geometric mean for all stocks