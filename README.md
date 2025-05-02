# Price Forecaster

![candlestick chart image](https://wallpapercave.com/wp/wp8544224.jpg)

https://github.com/CVK2C/4560-semester-project

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
The database applications (data import tool, data preprocessing script and machine learning models) have yet to be integrated, but can be run on their own. 

# Installation Instructions

## Frontend
1. Install Node.js
   - Download and install Node.js from https://nodejs.org
2. Install Expo CLI
   - Run the following command to install Expo CLI globally: `npm install -g expo-cli`
3. Create the project folder
  - Run `npx expo-cli init 4560-frontend`
4. Copy the `apps` folder to the `4560-frontend` folder
5. Navigate to the project directory
  - Run `cd 4560-frontend`
6. Start the project
  - Run `npx expo start`

Once everything is installed, you can run the app on your computer.
To run the app on a mobile device, install the Expo Go app from the App Store or Google Play. Then scan the QR code displayed in the terminal to open the app on your phone.

## Backend (Database and Flask Server)
This project uses Flask as the backend API to connect the React Native frontend with the database. The Flask application is currently hardcoded to connect to a local database.
You will need to:
1. Set up your own MySQL database
   - Visit the MySQL website at https://www.mysql.com to find instructions to install MySQL for your chosen operating system
   - With MySQL installed, login to it, either via a GUI application like MySQL Workbench, or the terminal
   - Create a database called `PROJECT_4560`
2. Update the Flask configuration to connect to your database instance, and Update API Endpoints in the React Native Frontend
   - Since the Flask server runs locally, you will also need to update the frontend to point to the correct host and port.
   - Edit the following files and replace the existing API URL with your own local IP address and port: `index.tsx` and `create-account.tsx` in the `apps` folder, and `explore.tsx` and `index.tsx` in the (tabs) folder

Make sure your device or emulator can reach your Flask server (they should be on the same network, and Flask should not be bound to localhost if accessed from another device). IMPORTANT: When configuring the API endpoint in the React Native app, do not use localhost or 127.0.0.1 as the host. These refer to the device itself, not your development machine. If you're running the app on a physical mobile device, it won't be able to reach the Flask server this way.

## Database Applications
### Data Importer Instructions

1. Set up Python virtual environment `python3 -m venv [venv]` and `source [venv]/bin/activate`
  - Replace `[venv]` with the actual name of the virtual environment
  - Use the `python` command on Windows OS instead of `python3`
  - Activate the environment with `[venv]\Scripts\activate.bat` or `[venv]\Scripts\Activate.ps1`
2. Install dependencies: `pip install pandas pyarrow numpy mysql-connector-python`
3. Run script: `python3 data-importer-release --directory /path/to/files`

### Data Preprocessing

1. Set up or reuse previous Python virtual environment
2. Install dependencies: `pip install pymysql pandas scikit-learn`
3. Run script: `python3 preprocess-release.py --table-prefix TABLE_PREFIX`

### LSTM Model

1. Set up or reuse previous Python virtual environment
2. Install dependencies: `pip install scikit-learn tensorflow[and-cuda] joblib`
3. Run script: `python3 lstm-release.py --table-prefix TABLE_PREFIX`

Note: A supported Nvidia GPU and the CUDA Toolkit are required to run this script. Check Nvidia's website for instructions on how to install set up the CUDA Toolkit for your specific OS and driver version.

## Tips Before Running The Application
1. Database credentials for your specific database need to be added to the Flask backend script as well as the data importer and preprocessing scripts.
2. Obtain the same or a similar dataset from Binance
3. Run the data importer script before interacting with the frontend
