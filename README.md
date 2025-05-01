# Price Forecaster

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
- Can read CSV files from .zip archives
- Can modify column names
- Can connect to a MySQL server
- Can create new databases and tables
- Can import modified data from CSV files to a database
- Can write modified data to Parquet files (exists only for debugging reasons)
- Can remove/modify columns/column data depending on requirements

Remaining:
- Add capability to import data from Parquet files
- Add capability to import data from uncompressed CSV files
- Add logic to read database schema and determine constraints
- Dynamically adjust incoming data depending on constraints

### Machine Learning Models: In Progress

The machine learning models are in an alpha state, and not yet feature complete
- A basic LSTM model is implemented, and can successfully train and test on the dataset, and output predictions

Remaining:
- Refine LSTM model to improve prediction accuracy
- Implement Transformer models

### Database: In progress

Database is in an alpha state, and not yet feature complete.
- Schema has been finalized
- Database has successfully tested with a portion of the total dataset

Remaining:
- Hash passwords of newly created users before storage
- Perform further tests with the complete dataset

### UI: In progress

UI is in an alpha state, and not yet feature complete.
- Login page has been completed
- Can connect to the database
- Has been deployed to web browsers via React Native for Web
- Can view candlestick charts generated from data in the database

Remaining:
- Hash user passwords before sending to database for authentication
- Implement user and admin views


### Overall application: In progress

The project currently consists of the framework of the application, with some parts nearing a feature complete state.

### Installation Instructions

Coming soon...
