# Price Prediction Application (working title)

![candlestick chart image](https://wallpapercave.com/wp/wp8544224.jpg)

## Introduction

Today’s financial markets are complex, fast-paced, dominated by algorithms, and 
produce more data per day than a human could parse in their lifetime. To solve this 
problem, we have developed an application that is capable of not only parsing this immense 
amount of data, but can also predict future price movements of financial markets.

## Design Overview / Tech Stack

The application is built in a modular fashion, and features a tool for data importation, a database, 
machine learning models, and a responsive UI for normal users and administrators.

Both the import tool and machine learning models are built using Python, the database is implemented 
via MySQL, and the UI is written using React Native.

## Dataset

The chosen dataset consists historical price tick data from of a selection of currency pairs, sourced 
from [Binance](https://data.binance.vision). Check the README in **example-data** for more information.

## Current Progress

### Import Tool: In progress

The import tool is in an alpha state, and not yet feature complete. 
- Can read CSV and Parquet files
- Can modify column names
- Can connect to a MySQL database
- Can write modified data to Parquet files (exists only for debugging reasons)

Remaining:
- Add logic to read database schema and determine contraints
- Dynamically adjust incoming data depending on constraints
- Add logic to modify/remove column data

### Machine Learning Models: Not started

Remaining:
- Implement LSTM and Transformer models

### Database: In progress

Database is in an alpha state, and not yet feature complete.
- Initial Schema has been created
- Database has successfully loaded with test data

Remaining:
- Finalize schema
- Hash passwords of newly created users before storage
- Perform further tests with more data (dependent on progress of other modules)

### UI: In progress

UI is in an alpha state, and not yet feature complete.
- Initial login page design completed

Remaining:
- Finalize login page design
- Connect to MySQL database
- Hash user passwords before sending to database for authentication
- Implement user and admin views
- Deploy to web browsers via React Native for Web

*The list of remaining tasks is not final, and may be adjusted over time.*

### Overall application: In progress

Upon completion of individual modules, they will be assembled and under final testing/adjustment.

### Installation Instructions

Coming soon...
