# Code development was assisted by an LLM (Qwen2.5-coder:32b). Check q32b-log for prompts and responses.
# NOTE: MySQL database credentials have been removed for privacy/security reasons. Fill in these values before running this script.

import argparse
import pymysql
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from multiprocessing import Pool, cpu_count
from datetime import datetime
import os
import pickle

# Directory paths for training and testing data
TRAINING_DIR_PATH = 'training_data/'
TESTING_DIR_PATH = 'testing_data/'
SCALER_PATH = 'scaler.pkl'

# Ensure directories exist
os.makedirs(TRAINING_DIR_PATH, exist_ok=True)
os.makedirs(TESTING_DIR_PATH, exist_ok=True)

# Function to connect to the MySQL database
def get_db_connection(db_config):
	return pymysql.connect(**db_config)

# Function to fetch min and max trade_id from the database
def get_trade_id_range(connection, table_name):
	try:
		with connection.cursor() as cursor:
			query = f"SELECT MIN(trade_id), MAX(trade_id) FROM {table_name}"
			cursor.execute(query)
			result = cursor.fetchone()
			return result[0], result[1]
	finally:
		connection.close()

# Function to fetch data in chunks based on trade_id range
def fetch_chunk(connection, table_name, start_trade_id, end_trade_id):
	try:
		with connection.cursor() as cursor:
			query = f"""
				SELECT price, volume, side, trade_id, time
				FROM {table_name}
				WHERE trade_id BETWEEN {start_trade_id} AND {end_trade_id}
			"""
			cursor.execute(query)
			columns = [desc[0] for desc in cursor.description]
			data = cursor.fetchall()
			return pd.DataFrame(data, columns=columns)
	finally:
		connection.close()

# Function to preprocess a chunk of data using a given scaler
def preprocess_chunk(chunk, scaler):
	# Optimize data types
	chunk['price'] = chunk['price'].astype('float64')
	chunk['volume'] = chunk['volume'].astype('float64')
	chunk['side'] = chunk['side'].astype('uint8')
	chunk['time'] = chunk['time'].astype('float64')
	
	# Normalize price, volume, and time using the provided scaler
	chunk[['price', 'volume', 'time']] = scaler.transform(chunk[['price', 'volume', 'time']])
	
	return chunk

# Function to write a DataFrame to Parquet file, appending if it exists
def write_to_parquet(df, file_path):
	df.to_parquet(file_path, index=False)

# Function to process data in chunks and write to disk using a given scaler
def process_data_in_chunks(connection_params, table_name, start_trade_id, end_trade_id, is_training, worker_id, scaler):
	connection = get_db_connection(connection_params)
	chunk = fetch_chunk(connection, table_name, start_trade_id, end_trade_id)
	
	if not chunk.empty:
		processed_chunk = preprocess_chunk(chunk, scaler)
		
		# Create a unique file path for each worker
		if is_training:
			file_path = os.path.join(TRAINING_DIR_PATH, f'training_worker_{worker_id}_{start_trade_id}.parquet')
		else:
			file_path = os.path.join(TESTING_DIR_PATH, f'testing_worker_{worker_id}_{start_trade_id}.parquet')
		
		write_to_parquet(processed_chunk, file_path)

# Function to merge parquet files in a directory into a single DataFrame
def merge_parquet_files(directory):
	return pd.concat([pd.read_parquet(os.path.join(directory, f)) for f in os.listdir(directory) if f.endswith('.parquet')], ignore_index=True)

# Main function to orchestrate the preprocessing
def main(table_name_prefix):
	table_name = f"{table_name_prefix}_TICK_DATA"
	
	# Database connection parameters
	DB_CONFIG = {
		'host': 'localhost',
		'user': '',
		'password': '',
		'database': 'PROJECT_4560'
	}
	
	# Get trade_id range
	connection = get_db_connection(DB_CONFIG)
	start_trade_id, end_trade_id = get_trade_id_range(connection, table_name)
	
	# Calculate 60% and 40% of the data range
	total_range = end_trade_id - start_trade_id + 1
	training_end_trade_id = start_trade_id + int(0.6 * total_range) - 1
	
	# Number of processes (CPU cores)
	n_partitions = 8 #cpu_count()
	
	# Define chunk sizes for training and testing
	training_chunk_size = int((training_end_trade_id - start_trade_id + 1) / n_partitions)
	testing_chunk_size = int((end_trade_id - training_end_trade_id) / n_partitions)
	
	# Fetch the first chunk to train the scaler
	initial_chunk = fetch_chunk(get_db_connection(DB_CONFIG), table_name, start_trade_id, start_trade_id + training_chunk_size - 1)
	
	if not initial_chunk.empty:
		# Optimize data types for the initial chunk
		initial_chunk['price'] = initial_chunk['price'].astype('float64')
		initial_chunk['volume'] = initial_chunk['volume'].astype('float64')
		initial_chunk['side'] = initial_chunk['side'].astype('uint8')
		initial_chunk['time'] = initial_chunk['time'].astype('float64')
		
		# Train the scaler on the first chunk
		scaler = MinMaxScaler()
		initial_chunk[['price', 'volume', 'time']] = scaler.fit_transform(initial_chunk[['price', 'volume', 'time']])
		
		# Save the trained scaler to a file
		with open(SCALER_PATH, 'wb') as scaler_file:
			pickle.dump(scaler, scaler_file)
	
	# Prepare arguments for the multiprocessing pool for training data
	args_training = []
	current_start = start_trade_id
	for i in range(n_partitions):
		current_end = min(current_start + training_chunk_size - 1, training_end_trade_id)
		args_training.append((DB_CONFIG, table_name, current_start, current_end, True, i, scaler))
		current_start = current_end + 1
	
	# Prepare arguments for the multiprocessing pool for testing data
	args_testing = []
	current_start = training_end_trade_id + 1
	for i in range(n_partitions):
		current_end = min(current_start + testing_chunk_size - 1, end_trade_id)
		args_testing.append((DB_CONFIG, table_name, current_start, current_end, False, i, scaler))
		current_start = current_end + 1
	
	# Process training data
	with Pool(processes=n_partitions) as pool:
		pool.starmap(process_data_in_chunks, args_training)
	
	# Process testing data
	with Pool(processes=n_partitions) as pool:
		pool.starmap(process_data_in_chunks, args_testing)
	
	# Merge all parquet files into a single DataFrame and write to final file
	training_df = merge_parquet_files(TRAINING_DIR_PATH)
	testing_df = merge_parquet_files(TESTING_DIR_PATH)
	
	training_df.to_parquet('final_training_data.parquet', index=False)
	testing_df.to_parquet('final_testing_data.parquet', index=False)

if __name__ == "__main__":
	# Set up argument parser
	parser = argparse.ArgumentParser(description="Preprocess trading data from a MySQL database.")
	parser.add_argument('--table-prefix', type=str, required=True, help='Prefix of the table name (e.g., ETHUSDC)')
	
	args = parser.parse_args()
	
	start_time = datetime.now()
	main(args.table_prefix)
	end_time = datetime.now()
	
	print(f"Data preprocessed in {end_time - start_time}")
