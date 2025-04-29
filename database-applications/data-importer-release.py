# Code development was assisted by an LLM (Qwen2.5-coder:32b). Check ai_disclaimer.pdf for prompts and responses.
# NOTE: MySQL database credentials have been removed for privacy/security reasons. 
# NOTE: Fill in these values before running this script.

import os
import sys
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
import pyarrow as pa
from pyarrow import csv as pv
from pathlib import Path
import mysql.connector
import argparse
import numpy as np

def list_files_in_directory(directory):

	csv_files = []
	
	for root, _, files in os.walk(directory):
		for file in files:
			if file.endswith('.zip'):
				csv_files.append(os.path.join(root, file))
				
	return csv_files

def convert_to_nanosecond_precision_float(timestamp):
	# Convert the timestamp to a string to count its digits
	timestamp_str = str(timestamp)
	
	# Determine the number of digits in the integer part of the timestamp
	num_digits = len(timestamp_str.split('.')[0])
	
	if num_digits == 19:
		# Already in nanoseconds as an integer, convert to float
		return float(timestamp) / 1e9
	elif num_digits == 16:
		# Microseconds to nanoseconds: divide by 10^3 and then convert to float
		return float(timestamp) / 1e6
	elif num_digits == 13:
		# Milliseconds to nanoseconds: divide by 10^6 and then convert to float
		return float(timestamp) / 1e3
	elif num_digits == 10:
		# Seconds to nanoseconds: convert to float
		return float(timestamp)
	else:
		raise ValueError("Unsupported timestamp precision. Expected 10, 13, 16, or 19 digits for seconds, milliseconds, microseconds, or nanoseconds.")

def convert_to_nanosecond_precision_int(timestamp):
	# Convert the timestamp to a string to count its digits
	timestamp_str = str(timestamp)
	
	# Determine the number of digits in the integer part of the timestamp
	num_digits = len(timestamp_str.split('.')[0])
	
	if num_digits == 19:
		# Already in nanoseconds as an integer
		return int(timestamp)
	elif num_digits == 16:
		# Microseconds to nanoseconds: multiply by 10^3
		return int(timestamp * 10**3)
	elif num_digits == 13:
		# Milliseconds to nanoseconds: multiply by 10^6
		return int(timestamp * 10**6)
	elif num_digits == 10:
		# Seconds to nanoseconds: multiply by 10^9
		return int(timestamp * 10**9)
	else:
		raise ValueError("Unsupported timestamp precision. Expected 10, 13, 16, or 19 digits for seconds, milliseconds, microseconds, or nanoseconds.")

def convert_tick_data_to_ohlc(df):
	# Convert 'time' column to datetime
	df['datetime'] = pd.to_datetime(df['time'], unit='ns')
	
	# Set the datetime as the index
	df.set_index('datetime', inplace=True)
	
	# Drop the unnecessary 'side' column and 'time' column
	df.drop(['trade_id', 'side', 'time'], axis=1, inplace=True)

	# Create a 1-minute OHLCV dataframe
	ohlc_1min = df.resample('min').agg({
		'price': ['first', 'max', 'min', 'last'],
		'volume': 'sum'
	})
	
	ohlc_1min.columns = ['open', 'high', 'low', 'close', 'volume']
	ohlc_1min['start_time'] = (ohlc_1min.index - pd.Timedelta(seconds=60) + pd.Timedelta(nanoseconds=1)).astype('int64')
	ohlc_1min['end_time'] = ohlc_1min.index.astype('int64')
	
	# Define higher timeframes and their corresponding resampling rules
	timeframes = {
		'2min': 2,
		'3min': 3,
		'5min': 5,
		'15min': 15,
		'30min': 30,
		'h': 60,
		'4h': 240,
		'D': 1440,
		'7D': 10080
	}
	
	ohlc_dataframes = {'1min': ohlc_1min}
	
	for rule, multiplier in timeframes.items():
		ohlc_prev_df = ohlc_dataframes[f'{multiplier // timeframes[rule]}min']
		
		# Resample the previous timeframe to the current one
		ohlc_df = ohlc_prev_df.resample(rule).agg({
			'open': 'first',
			'high': 'max',
			'low': 'min',
			'close': 'last',
			'volume': 'sum'
		}).dropna()
		
		ohlc_df['start_time'] = (ohlc_df.index - pd.Timedelta(minutes=multiplier) + pd.Timedelta(nanoseconds=1)).astype('int64')
		ohlc_df['end_time'] = ohlc_df.index.astype('int64')
		
		ohlc_dataframes[rule] = ohlc_df

	return ohlc_dataframes

def import_csv(zip_files, db_connector, db_cursor):

	pa_table = None
	pa_candle_table = None
	column_names = ["trade_id", "price", "volume", "quoteQty", "time", "side", "isBestMatch"]
	drop_columns = ["quoteQty", "isBestMatch"]
	
	for file in zip_files:
		
		with ZipFile(file, "r") as zf:
			# Get the path of the csv file
			csv_file = [f for f in zf.namelist() if f.endswith(".csv")][0]
			print(f"CSV: {csv_file}")  # DEBUG

			# Open the csv file as a file-like object that pyarrow can work with and save it to a pyarrow table
			with zf.open(csv_file) as f:
				data = BytesIO(f.read())

				pa_table = pv.read_csv(data)  # Save object to table
				pa_table = pa_table.rename_columns(column_names)  # Rename columns of the table
				pa_table = pa_table.drop(columns=drop_columns)  # Drop unnecessary columns from the table

				# Convert Unix timestamps to nanosecond precision (float)
				time_column = pa_table.column("time").to_numpy()
				new_time_column = [convert_to_nanosecond_precision_float(ts) for ts in time_column]
				new_time_column = pa.array(new_time_column, type=pa.float64())
				pa_table = pa_table.set_column(3, "time", new_time_column)

			# Re-read the csv file into another pyarrow table and convert the Unix timestamp to a nanosecond precision 64-bit int
			with zf.open(csv_file) as f:
				data = BytesIO(f.read())

				# Create a second table
				pa_candle_table = pv.read_csv(data)
				pa_candle_table = pa_candle_table.rename_columns(column_names)
				pa_candle_table = pa_candle_table.drop(columns=drop_columns)

				time_column = pa_candle_table.column("time").to_numpy()
				new_time_column = [convert_to_nanosecond_precision_int(ts) for ts in time_column]
				new_time_column = pa.array(new_time_column, type=pa.int64())
				pa_candle_table = pa_candle_table.set_column(3, "time", new_time_column)

			# Convert and output summary of dataframes for different timeframes
			pd_df = pa_candle_table.to_pandas()
			ohlc_df_list = convert_tick_data_to_ohlc(pd_df)
			timeframes = ["1min", "2min", "3min", "5min", "15min", "30min", "h", "4h", "D", "7D"]
			for tf in timeframes:
				try:
					ohlc_df_list[tf] = ohlc_df_list[tf].replace(np.nan, None)
					ohlc_val = list(ohlc_df_list[tf].itertuples(index=False, name=None))
					ohlc_query = f"CREATE TABLE IF NOT EXISTS {test_table}_{tf} (candle_id INT NOT NULL AUTO_INCREMENT, open FLOAT, high FLOAT, low FLOAT, close FLOAT, volume FLOAT, start_time BIGINT(255), end_time BIGINT(255), PRIMARY KEY (candle_id))"
					db_cursor.execute(ohlc_query)
					db_connector.commit()
					
					ohlc_query = f"INSERT INTO {test_table}_{tf} (open, high, low, close, volume, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
					db_cursor.executemany(ohlc_query, ohlc_val)
					db_connector.commit()
				except Exception as e:
					print(f"An error occurred inserting data into the database for timeframe {tf}: {e}")
					sys.exit()

			# Write table data to file and to the database in batches
			for batch in pa_table.to_batches(max_chunksize=500000):
				try:
					df_batch = batch.to_pandas()  # Convert the batch of the pyarrow table into a pandas dataframe for insertion into the database
					val = list(df_batch.itertuples(index=False, name=None))  # "INSERT" requires either tuple, or list of tuples
					sql_query = f"INSERT INTO {test_table} VALUES (%s, %s, %s, %s, %s)"
					db_cursor.executemany(sql_query, val)
					db_connector.commit()
				except Exception as e:
					print(f"An error occurred inserting data into the database: {e}")
					sys.exit()

if __name__ == "__main__":
	# Set up argument parser
	parser = argparse.ArgumentParser(description="Import trade data from CSV files into a MySQL database.")
	parser.add_argument("--directory", type=str, required=True, help="Directory containing the CSV files")
	
	args = parser.parse_args()
	directory_to_search = args.directory
	dir_name = Path(directory_to_search).name
	clear_db_query = "DROP DATABASE IF EXISTS PROJECT_4560"
	create_db_querys = ["CREATE DATABASE IF NOT EXISTS PROJECT_4560", "USE PROJECT_4560", f"CREATE TABLE {dir_name}_TICK_DATA (trade_id INT, price FLOAT, volume FLOAT, time DOUBLE PRECISION(19,8), side VARCHAR(255))"]

	test_database = "PROJECT_4560"
	test_table = f"{dir_name}_TICK_DATA"

	# Connect to MySQL server
	db_connector = mysql.connector.connect(host="localhost", user="", password="")
	db_cursor = db_connector.cursor()

	# DEBUG: Clear the database if it exists
	try:
		db_cursor.execute(clear_db_query)  
		db_connector.commit()
	except Exception as e:
		print(f"An error occurred when preparing the database: {e}")
		sys.exit()

	# Create the database if it does not exist
	for statement in create_db_querys:
		try:
			if statement == "":
				continue
			db_cursor.execute(statement)
			db_connector.commit()
		except Exception as e:
			print(f"An error occurred when preparing the database: {e}")
			sys.exit()

	# Search for compressed CSV files
	zip_files = list_files_in_directory(directory_to_search)

	# Sort list of compressed csv files
	zip_files.sort()

	# Process CSV files
	import_csv(zip_files, db_connector, db_cursor)
