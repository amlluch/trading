
Feature: Global Beberage Corporation Exchange Stocks
  Creation of stocks and lists

  Scenario Outline: Simple stock
    Given a set of data
    When a 3 digits string named "<Symbol>"
    And a string named stock type with value "<Stock Type>" of two possible
    And a numeric number named Last Dividend with value "<Last Dividend>"
    And other numeric value named Fixed Dividend with value <Fix Dividend>
    And another numeric value named Par Value with value <Par Value>
    Then I create a single stock

    Examples:
      | Symbol | Stock Type | Last Dividend | Fix Dividend  | Par Value |
      | TEA    | Common     |             0 |             0 |       100 |
      | POP    | Common     |             8 |             0 |       100 |
      | ALE    | Common     |            23 |             0 |        60 |
      | GIN    | Preferred  |             8 |            2% |       100 |
      | JOE    | Common     |            13 |             0 |       250 |
      | MIL    | Common     |            12 |             0 |        21 |
      | MOM    | Preferred  |            17 |             1 |        23 |


  Scenario Outline: get dividend yield and PER
    Given a list of stock elements
      | symbol | stock_type | last_dividend | fix_dividend  | par_value |
      | TEA    | Common     |             0 |             0 |       100 |
      | POP    | Common     |             8 |             0 |       100 |
      | ALE    | Common     |            23 |             0 |        60 |
      | GIN    | Preferred  |             8 |            2% |       100 |
      | JOE    | Common     |            13 |             0 |       250 |
      | MIL    | Common     |            12 |             0 |        21 |
      | MOM    | Preferred  |            17 |             3 |       100 |

    When I have a symbol <my_symbol>
    And with price of <my_price> pennies
    Then calculate the dividend yield
    Then calculate the P/E Ratio and compare to <results>

    Examples:
      | my_symbol | my_price  | results |
      | GIN       |       225 |   112.5 |
      | ALE       |        92 |     4.0 |
      | MOM       |        90 |    30.0 |
      | JOE       |        91 |     7.0 |
      | TEA       |        45 |     0.0 |
