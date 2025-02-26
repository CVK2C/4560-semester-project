
## Example Data Explanation

Spot trade tick data obtained from Binance at [data.binance.vision](https://data.binance.vision) is stored as compressed CSV files, with unlabeled columns.
Column labels can be found at [Binance's GitHub](https://github.com/binance/binance-public-data):

1. tradeId: unique for each trade
2. price: value of the base asset in relation to the quote asset (In terms of BTC/USDT, BTC would be the base asset, and USDT would be the quote asset)
3. qty: amount of the base asset that was traded
4. quoteQty: amount of the quote asset that was traded
5. time: Unix timestamp of when the trade occured
6. isBuyerMaker: Indicates whether the trade was a buy or a sell (False = buy, True = sell)
7. isBestMatch: Indicates whether the trade was filled at the best available price

## Modifications For The Project

The columns *quoteQty* and *isBestMatch* will not be included in the project's database, as they are not needed to either train ML models or generate candlestick charts.
The column *isBuyerMaker* will be converted to an integer value, where True = 1, and False = 0. Thus, a value of 0 will indicate a buy, and a value of 1 will indicate a sell.

## Example Table

| tradeId   | price          | qty        | quoteQty      | time          | isBuyerMaker | isBestMatch |
| :-------: | :------------: | :--------: | :-----------: | :-----------: | :----------: | :---------: |
| 500151364 | 19166.90000000 | 0.00476300 | 91.29194470   | 1607385600160 | False        | True        |
| 500151365 | 19166.89000000 | 0.00550000 | 105.41789500  | 1607385600231 | True         | True        |
| 500151366 | 19166.89000000 | 0.00770200 | 147.62338678  | 1607385600231 | True         | True        |
| 500151367 | 19166.90000000 | 0.00260100 | 49.85310690   | 1607385600233 | False        | True        |
| 500151368 | 19166.90000000 | 0.00260100 | 49.85310690   | 1607385600256 | False        | True        |
| 500151369 | 19166.90000000 | 0.00260100 | 49.85310690   | 1607385600288 | False        | True        |
| 500151370 | 19166.90000000 | 0.00247400 | 47.41891060   | 1607385600309 | False        | True        |
| 500151371 | 19166.90000000 | 0.00241100 | 46.21139590   | 1607385600339 | False        | True        |
| 500151372 | 19166.90000000 | 0.00234800 | 45.00388120   | 1607385600366 | False        | True        |
| 500151373 | 19166.90000000 | 0.00228400 | 43.77719960   | 1607385600397 | False        | True        |
| 500151374 | 19166.90000000 | 0.00222100 | 42.56968490   | 1607385600417 | False        | True        |
| 500151375 | 19166.90000000 | 0.00215700 | 41.34300330   | 1607385600447 | False        | True        |
| 500151376 | 19166.90000000 | 0.00212500 | 40.72966250   | 1607385600471 | False        | True        |
| 500151377 | 19166.90000000 | 0.00088800 | 17.02020720   | 1607385600496 | False        | True        |
| 500151378 | 19166.90000000 | 0.00059400 | 11.38513860   | 1607385600734 | False        | True        |
| 500151379 | 19166.90000000 | 0.06006600 | 1151.27901540 | 1607385600847 | False        | True        |
| 500151380 | 19166.90000000 | 0.04000000 | 766.67600000  | 1607385600852 | False        | True        |
| 500151381 | 19166.90000000 | 0.03000000 | 575.00700000  | 1607385600947 | False        | True        |
| 500151382 | 19166.90000000 | 0.35300000 | 6765.91570000 | 1607385601041 | False        | True        |
| 500151383 | 19166.90000000 | 0.04900000 | 939.17810000  | 1607385601123 | False        | True        |
| 500151384 | 19166.89000000 | 0.05210600 | 998.70997034  | 1607385601159 | True         | True        |
